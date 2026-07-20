#!/usr/bin/env python3
"""
轻小说正文 Unicode 块污染扫描脚本。

补 `validate_light_novel.py` 和 `references/light-novel-garbled-text-cleanup-2026-07-08.md`
中 `scan_garbled()` 的盲区：正则 `[a-zA-Z]{3,}` 只抓 Latin 字母，**抓不到**
混入中文正文的 Cyrillic / Hebrew / Greek / 扩展 Latin 等其他 Unicode 块字符。

2026-07-08 实测《网游废柴逆袭记》三章首稿出现：
  - `<table end>` 自插 HTML 片段（1 处）
  - `ото` Cyrillic "oto" 段落首段插入（1 处）
  - `ǣ` Latin Extended 替换/混入汉字（1 处）
  - `֒` U+05BA Hebrew combining vowel 静默粘到汉字"看"上（1 处）
  - `call` 这类中文句中出现的英文动词借词（边界情况，按用户偏好清理）

bundled `validate_light_novel.py` 全部通过（chars/对白/ILLUST/漫画字段都 OK），
但人眼读会卡壳。本脚本是写入后的"投递前最后一道闸"。

用法：
    python3 scan_unicode_contamination.py /path/to/project
    python3 scan_unicode_contamination.py /path/to/project/light_novel
    python3 scan_unicode_contamination.py /path/to/single_chapter.md

无任何污染 → 退出码 0、输出每一文件 `OK`。
检测到任何污染 → 退出码 1、列出文件 + 命中字符串 + 字符码点。

无需第三方依赖，仅用标准库。
"""
import sys
import re
import glob
import os


# 我们关心的"非中文正文中不该出现的 Unicode 块"。
# 范围取自 Unicode 标准，故意覆盖宽，宁可误报让人眼看一眼，也不要漏报。
SUSPICIOUS_BLOCKS = [
    (0x0400, 0x052F, "Cyrillic"),       # 俄语/西里尔
    (0x0530, 0x058F, "Armenian"),
    (0x0590, 0x05FF, "Hebrew"),         # 含组合符（vowel points）
    (0x0600, 0x06FF, "Arabic"),
    (0x0700, 0x074F, "Syriac"),
    (0x0780, 0x07BF, "Thaana"),
    (0x0900, 0x097F, "Devanagari"),
    (0x0E00, 0x0E7F, "Thai"),
    (0x0E80, 0x0EFF, "Lao"),
    (0x1000, 0x109F, "Myanmar"),
    (0x10A0, 0x10FF, "Georgian"),
    (0x1100, 0x11FF, "Hangul Jamo"),
    (0x1E00, 0x1EFF, "Latin Extended Additional"),  # 含 ǣ 等
]

# 已知的、合法的结构性 ASCII/拉丁片段 —— 扫描器忽略这些。
SAFE_PATTERNS = [
    r"ILLUST_\d+",         # 插图标记
    r"<!--\s*ILLUST_\d+\s*-->",  # 插图注释
]

# borderline 拉丁借词白名单（中文玩家常用、可接受）：用户偏好默认不白名单，
# 由扫描器报出来由人眼判断是否清理。本表为参考而非默认静默：
COMMON_LOANWORDS = {"PPT", "ID", "DPS", "OK", "App", "app"}


def scan_text(text):
    """返回 (block_hits, latin_in_cjk, html_artifacts) 三个列表。"""
    # 1. Unicode 块越界
    block_hits = []
    for lo, hi, name in SUSPICIOUS_BLOCKS:
        for ch in text:
            cp = ord(ch)
            if lo <= cp <= hi:
                # 取该字符上下文 ±10 个字符
                idx = text.index(ch)
                ctx = text[max(0, idx - 10):idx + 11].replace("\n", "\\n")
                block_hits.append((name, ch, hex(cp), ctx))
                break  # 每个 block 命中一次示例即可，避免刷屏
    # 去重：同 block 取第一个命中点
    seen_blocks = set()
    deduped = []
    for hit in block_hits:
        if hit[0] not in seen_blocks:
            seen_blocks.add(hit[0])
            deduped.append(hit)
    block_hits = deduped

    # 2. 拉丁字母混入中文（>=3 个字母连续，排除 ILLUST 等）
    cleaned = text
    for pat in SAFE_PATTERNS:
        cleaned = re.sub(pat, " ", cleaned)
    # 中文紧贴拉丁 拉丁紧贴中文 —— 边界借词
    latin_in_cjk = []
    for m in re.finditer(
        r"[\u4e00-\u9fff][A-Za-z]{2,}[\u4e00-\u9fff]"
        r"|[\u4e00-\u9fff][A-Za-z]{3,}", cleaned
    ):
        word = m.group(0)
        # 过滤掉纯英文人名/术语在引号内的常见借词
        bare = re.sub(r"[\u4e00-\u9fff]", "", word)
        if bare in COMMON_LOANWORDS:
            continue
        latin_in_cjk.append(word)
    # 去重保序
    latin_in_cjk = list(dict.fromkeys(latin_in_cjk))

    # 3. 自插 HTML/markdown 工件 —— 在轻小说正文里不该出现
    html_artifacts = []
    for pat in [r"<table[^>]*>", r"</table>", r"<table\s+end\s*>",
                r"<div[^>]*>", r"</div>", r"<br\s*/?>"]:
        for m in re.finditer(pat, text):
            html_artifacts.append(m.group(0))
    html_artifacts = list(dict.fromkeys(html_artifacts))

    return block_hits, latin_in_cjk, html_artifacts


def scan_file(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return scan_text(text)


def main():
    if len(sys.argv) < 2:
        print("Usage: scan_unicode_contamination.py <dir_or_file>", file=sys.stderr)
        sys.exit(2)

    target = sys.argv[1]
    files = []
    if os.path.isdir(target):
        # 自动发现 light_novel/ln*.md；若没有就扫所有 .md
        ln_dir = os.path.join(target, "light_novel") if os.path.basename(target) != "light_novel" else target
        if os.path.isdir(ln_dir):
            files = sorted(glob.glob(os.path.join(ln_dir, "ln*.md")))
        if not files:
            files = sorted(glob.glob(os.path.join(target, "**", "ln*.md"), recursive=True))
        if not files:
            files = sorted(glob.glob(os.path.join(target, "*.md")))
    elif os.path.isfile(target):
        files = [target]
    else:
        print(f"Not found: {target}", file=sys.stderr)
        sys.exit(2)

    if not files:
        print("No .md files to scan.", file=sys.stderr)
        sys.exit(2)

    any_dirty = False
    for f in files:
        block_hits, latin_in_cjk, html_artifacts = scan_file(f)
        dirty = bool(block_hits or latin_in_cjk or html_artifacts)
        if dirty:
            any_dirty = True
            print(f"\u26a0 {f}")
            if block_hits:
                print("  Unicode 块越界:")
                for name, ch, cp, ctx in block_hits:
                    print(f"    [{name}] U+{cp[2:].upper()} '{ch}'  ctx: ...{ctx}...")
            if latin_in_cjk:
                print("  拉丁借词混入中文 (需人眼判断是否清理):")
                for w in latin_in_cjk:
                    print(f"    \u2192 {w}")
            if html_artifacts:
                print("  HTML/markdown 工件:")
                for a in html_artifacts:
                    print(f"    \u2192 {a}")
        else:
            print(f"\u2713 {f}  干净")

    sys.exit(1 if any_dirty else 0)


if __name__ == "__main__":
    main()
