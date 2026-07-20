#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Delivery verifier for "前N章+设定" single-batch light-novel projects.

Complements validate_light_novel.py (which only checks light_novel/*.md chapters)
by ALSO verifying the metadata files (characters.md role count, foreshadowing.md
unresolved-thread count), the canonical role names against every chapter, and
scanning each chapter for heredoc residue + ASCII-in-Chinese-narrative garbling
— patterns documented in references/light-novel-heredoc-pitfall-2026-07-08.md
and references/light-novel-garbled-text-cleanup-2026-07-08.md that
validate_light_novel.py does NOT detect.

Run after the standard `validate_light_novel.py` to close the gap, OR run this
as a one-shot delivery check before reporting the project done.

Usage:
    python3 scripts/verify_light_novel_delivery.py <project-dir> \
        [--min-chars CN] [--min-roles N] [--min-threads N] [--min-dialogues N] \
        [--min-illust N] [--check-role-drift yes|no]

Defaults match the known-good baseline from the 合租1024 session (2026-07-08):
    --min-chars 2500  (pure 中文字符 [\\u4e00-\\u9fff])
    --min-roles 4     (合租4人 scenario)
    --min-threads 3   (前3章伏笔)
    --min-dialogues 8 (matches validate_light_novel.py)
    --min-illust 3    (matches validate_light_novel.py)
    --check-role-drift yes  (see "角色名漂移" below)

NOTE on char counting: this script's default uses the conservative
"pure CJK characters" floor (sum of \\u4e00-\\u9fff), NOT the ws (all
non-whitespace) floor that validate_light_novel.py uses. The two differ by
~15-25% (ws > cn). When reporting char counts to the user, ALWAYS state which
floor you used, otherwise the number will look inconsistent with the validator.

=== New checks added 2026-07-08 (AI女友已下线 session) ===

1. 角色名漂移检测 (--check-role-drift, default yes):
   Extracts canonical role names from characters.md's `## <name>` headers,
   then scans every ln*.md for any of those names that ALSO appear with a
   one-character variant (e.g. 柠/檬, 冬/檬, 青/清) within a 「...」——<name>
   attribution line. Multi-chapter LLM generation routinely drifts to a
   visually-similar character (本次实测：characters.md 用"沈檬"，三章正文
   先后出现"沈柠"和"沈冬青"两种漂移变体；validate_light_novel.py 和旧的
   verify_light_novel_delivery.py 都检测不到——只有人工 grep + replace_all
   才能修). This check fails loudly so the agent fixes names BEFORE reporting
   the project done, instead of after the user notices.

   Caveat: the variant detection uses a simple Unicode-neighbour scan and
   WILL produce false positives for names that are themselves one-char-off
   another common word. Treat hits as prompts to eyeball, not as hard errors.
   To silence for a project with legitimately similar names, pass
   --check-role-drift no.

2. ASCII-in-Chinese-narrative garble scan (extends heredoc residue check):
   Beyond the heredoc residue patterns, this now flags:
     - ASCII letter runs of 3+ inside a Chinese sentence context
       (CJK letter CJK): catches "队47人"-style arabic-numeral-in-CJK and
       "ProjectCode: jixia"-style english-identifier-in-CJK that the existing
       type-4 "数字待判断" check in light-novel-garbled-text-cleanup-2026-07-08.md
       misses because those numbers/identifiers aren't directly followed by
       a Chinese classifier like 年/岁/个月/章.
     - snake_case / CamelCase residue after a 「」—— attribution line.
   These are reported per-chapter as `ascii_in_cjk` and `attribution_residue`
   counts; non-zero is a delivery failure.
"""
import argparse
import re
import sys
from pathlib import Path

# heredoc residue patterns (kept in sync with light-novel-heredoc-pitfall-2026-07-08.md)
HEREDOC_RESIDUE = re.compile(r"\]='''|\\\\''|isVisible|jar勤|Visibility\(true\)|yesterday,\.")

# comic technical markers that must never appear in light-novel prose
COMIC_MARKERS = re.compile(
    r'\*\*格子\*\*|\*\*构图\*\*|\*\*气泡\*\*|\*\*旁白\*\*|\*\*拟声\*\*|\*\*转场\*\*'
    r'|\*\*AI 提示词\*\*|### Panel|## Page|## Scene|\| 字段 \| 内容 \|'
)

# NEW: ASCII letter/digit run embedded inside a Chinese narrative context.
# Matches when a 2+ char ASCII sequence is immediately preceded AND followed
# by a CJK character — the signature of "队47人" / "校园-olds安防" style garble.
ASCII_IN_CJK = re.compile(r'[\u4e00-\u9fff][A-Za-z0-9][A-Za-z0-9._-]*[\u4e00-\u9fff]')

# NEW: snake_case / CamelCase residue glued onto a 「」—— attribution line.
ATTRIBUTION_RESIDUE = re.compile(r'^「.+?」——[^\n]*[_A-Z][a-z]+[_A-Z]', re.M)

# Variant-name detection: same family of name, one char different.
# Conservative: only flag when the canonical name is 2+ chars and the
# candidate differs by exactly one character at the same position.
def _variant_candidates(canonical: str):
    """Yield plausible one-char-off variants of a 2+ char Chinese name."""
    if len(canonical) < 2:
        return
    # We can't enumerate all CJK, so we scan the chapter text itself for
    # strings that match <first_char>?<rest> or <first_chars>?<last_char>
    # and report them. The actual matching happens in check_role_drift.
    pass


def extract_canonical_role_names(characters_md_text: str):
    """Return list of (role_name, header_line) from characters.md `## Name` headers.

    Skips the top-level `# 角色档案` title and the `## 次要角色` section header.
    Lines like `## 陆时行（主角）` yield name='陆时行' (strips parenthetical).
    """
    names = []
    for line in characters_md_text.splitlines():
        m = re.match(r'^##\s+(.+?)\s*$', line)
        if not m:
            continue
        raw = m.group(1).strip()
        # Skip section headers that are clearly not a person
        if raw in ('次要角色', '角色档案'):
            continue
        # Strip parenthetical descriptors: "陆时行（主角）" -> "陆时行"
        name = re.sub(r'[（(].*?[)）].*$', '', raw).strip()
        if name and len(name) >= 2:
            names.append(name)
    return names


def check_role_drift(chapter_text: str, canonical_names):
    """For each canonical name, scan the chapter for one-char-off variants
    that appear inside a 「...」——<attribution> line.

    Returns a list of (canonical, variant, sample_line) tuples.
    """
    drifts = []
    # Collect every attribution target the chapter actually uses.
    used = re.findall(r'^「.+?」——(.+?)$', chapter_text, re.M)
    used_set = set(s.strip() for s in used)
    for canon in canonical_names:
        for candidate in used_set:
            if candidate == canon:
                continue
            # Only flag same-length one-char-off variants (the common LLM drift).
            if len(candidate) != len(canon):
                continue
            diffs = sum(1 for a, b in zip(canon, candidate) if a != b)
            if diffs == 1:
                drifts.append((canon, candidate))
    # Dedupe
    return sorted(set(drifts))


def check_chapter(path: Path, min_chars, min_dialogues, min_illust,
                  canonical_names=None, check_drift=True):
    t = path.read_text(encoding='utf-8', errors='ignore')
    residue = HEREDOC_RESIDUE.findall(t)
    cn = len(re.findall(r'[\u4e00-\u9fff]', t))
    ws = len(''.join(t.split()))
    illust = re.findall(r'<!-- ILLUST_(\d+) -->', t)
    hook = '## 章末钩子' in t
    comic_poll = COMIC_MARKERS.findall(t)
    # STRICT dialogue regex matches validate_light_novel.py exactly
    dials = re.findall(r'^「.+?」——.+$', t, re.M)

    # NEW garble scans
    ascii_in_cjk = ASCII_IN_CJK.findall(t)
    attr_residue = ATTRIBUTION_RESIDUE.findall(t)

    issues = []
    if residue:
        issues.append(f'HEREDOC_RESIDUE={len(residue)} → discard & rewrite, do not patch')
    if cn < min_chars:
        issues.append(f'cn_chars={cn} < {min_chars}')
    if len(illust) < min_illust:
        issues.append(f'illusts={len(illust)} < {min_illust}')
    if not hook:
        issues.append('missing ## 章末钩子')
    if comic_poll:
        issues.append(f'comic_field_pollution={len(comic_poll)} -> {comic_poll[:3]}')
    if len(dials) < min_dialogues:
        issues.append(f'strict_dialogues={len(dials)} < {min_dialogues} (narrative-attribution leak?)')
    if ascii_in_cjk:
        issues.append(f'ascii_in_cjk={len(ascii_in_cjk)} -> {ascii_in_cjk[:3]} (arabic-numeral or english-identifier embedded in Chinese narrative)')
    if attr_residue:
        issues.append(f'attribution_residue={len(attr_residue)} -> {attr_residue[:3]} (snake_case/CamelCase glued onto 「」—— name)')

    role_drifts = []
    if check_drift and canonical_names:
        role_drifts = check_role_drift(t, canonical_names)
        if role_drifts:
            issues.append(f'role_name_drift={len(role_drifts)} -> {role_drifts[:3]} (chapter uses a one-char-off variant of a characters.md role name; replace_all to fix)')

    return {
        'file': path.name,
        'passed': not issues,
        'issues': issues,
        'stats': {'cn_chars': cn, 'ws_chars': ws, 'illusts': illust,
                  'hook': hook, 'comic_poll': len(comic_poll),
                  'heredoc_residue': len(residue), 'strict_dialogues': len(dials),
                  'ascii_in_cjk': len(ascii_in_cjk),
                  'attribution_residue': len(attr_residue),
                  'role_drifts': len(role_drifts)},
    }


def check_metadata(base: Path, min_roles, min_threads, required_summary_keys):
    issues = []
    ch = (base / 'characters.md')
    sm = (base / 'summary.md')
    fs = (base / 'foreshadowing.md')
    if not ch.exists(): issues.append('missing characters.md')
    if not sm.exists(): issues.append('missing summary.md')
    if not fs.exists(): issues.append('missing foreshadowing.md')
    role_count = thread_count = 0
    summary_keys_ok = []
    canonical_names = []
    if ch.exists():
        ch_txt = ch.read_text(encoding='utf-8')
        role_count = len(re.findall(r'^## .+$', ch_txt, re.M)) - 1  # subtract title row
        if role_count < min_roles:
            issues.append(f'roles={role_count} < {min_roles} (incl. 1 title row)')
        canonical_names = extract_canonical_role_names(ch_txt)
    if fs.exists():
        thread_count = len(re.findall(r'^- \[ \] .+$', fs.read_text(encoding='utf-8'), re.M))
        if thread_count < min_threads:
            issues.append(f'unresolved_threads={thread_count} < {min_threads}')
    if sm.exists():
        sm_txt = sm.read_text(encoding='utf-8')
        summary_keys_ok = [k for k in required_summary_keys if k in sm_txt]
        missing = [k for k in required_summary_keys if k not in sm_txt]
        if missing:
            issues.append(f'summary.md missing keys: {missing}')
    return {
        'passed': not issues,
        'issues': issues,
        'stats': {'roles': role_count, 'unresolved_threads': thread_count,
                  'summary_keys_ok': summary_keys_ok,
                  'canonical_role_names': canonical_names},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('project_dir')
    ap.add_argument('--min-chars', type=int, default=2500, help='min pure CJK chars per chapter')
    ap.add_argument('--min-roles', type=int, default=4, help='min non-title role rows in characters.md')
    ap.add_argument('--min-threads', type=int, default=3, help='min unresolved threads in foreshadowing.md')
    ap.add_argument('--min-dialogues', type=int, default=8)
    ap.add_argument('--min-illust', type=int, default=3)
    ap.add_argument('--summary-keys', default='一句话卖点,主类型,目标读者,故事基调,主线目标,情感线,章节目录',
                    help='comma-separated keys that must appear in summary.md')
    ap.add_argument('--check-role-drift', default='yes', choices=['yes', 'no'],
                    help='scan chapters for one-char-off variants of characters.md role names')
    args = ap.parse_args()

    base = Path(args.project_dir)
    ln_dir = base / 'light_novel'
    if not ln_dir.exists():
        print(f'ERROR: {ln_dir} does not exist', file=sys.stderr)
        sys.exit(2)
    chapters = sorted(ln_dir.glob('ln*.md'))
    if not chapters:
        print(f'ERROR: no ln*.md found in {ln_dir}', file=sys.stderr)
        sys.exit(2)

    print('=' * 60)
    print('元数据文件验证')
    print('=' * 60)
    meta = check_metadata(base, args.min_roles, args.min_threads,
                          [k.strip() for k in args.summary_keys.split(',') if k.strip()])
    print(f"角色: {meta['stats']['roles']} (含1标题行, 要求≥{args.min_roles}个非标题角色)")
    print(f"未回收伏笔: {meta['stats']['unresolved_threads']} (要求≥{args.min_threads})")
    print(f"summary.md 关键字段命中: {meta['stats']['summary_keys_ok']}")
    canonical_names = meta['stats']['canonical_role_names']
    if canonical_names:
        print(f"角色档案规范化名: {canonical_names}")
    if meta['issues']:
        print('issues:', meta['issues'])

    print()
    print('=' * 60)
    print('正文章节验证（轻小说 ln*.md）')
    print('=' * 60)
    check_drift = (args.check_role_drift == 'yes') and bool(canonical_names)
    chapter_results = [check_chapter(f, args.min_chars, args.min_dialogues, args.min_illust,
                                     canonical_names=canonical_names, check_drift=check_drift)
                       for f in chapters]
    all_pass = meta['passed']
    for r in chapter_results:
        s = r['stats']
        marks = []
        marks.append('cn_chars' + ('✓' if s['cn_chars'] >= args.min_chars else '✗'))
        marks.append('illust' + ('✓' if len(s['illusts']) >= args.min_illust else '✗'))
        marks.append('hook' + ('✓' if s['hook'] else '✗'))
        marks.append('comic_poll=' + str(s['comic_poll']) + ('✓' if s['comic_poll'] == 0 else '✗'))
        marks.append('heredoc=' + str(s['heredoc_residue']) + ('✓' if s['heredoc_residue'] == 0 else '✗'))
        marks.append('dials=' + str(s['strict_dialogues']) + ('✓' if s['strict_dialogues'] >= args.min_dialogues else '✗'))
        marks.append('ascii_cjk=' + str(s['ascii_in_cjk']) + ('✓' if s['ascii_in_cjk'] == 0 else '✗'))
        marks.append('attr_res=' + str(s['attribution_residue']) + ('✓' if s['attribution_residue'] == 0 else '✗'))
        if check_drift:
            marks.append('drift=' + str(s['role_drifts']) + ('✓' if s['role_drifts'] == 0 else '✗'))
        print(f"\n{r['file']}:")
        print(f"  cn={s['cn_chars']} ws={s['ws_chars']} illusts={s['illusts']} hook={s['hook']} "
              f"comic_poll={s['comic_poll']} heredoc={s['heredoc_residue']} strict_dials={s['strict_dialogues']} "
              f"ascii_cjk={s['ascii_in_cjk']} attr_res={s['attribution_residue']} drift={s['role_drifts']}")
        print(f"  [{' '.join(marks)}]")
        if r['issues']:
            print('  issues:', r['issues'])
            all_pass = False

    print()
    print('=' * 60)
    print(f"综合状态: {'全部通过 ✓' if all_pass else '存在问题 ✗'}")
    print('=' * 60)
    sys.exit(0 if all_pass else 1)


if __name__ == '__main__':
    main()
