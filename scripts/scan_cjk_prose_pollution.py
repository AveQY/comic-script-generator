#!/usr/bin/env python3
"""
CJK 散文输出污染扫描（扩展版，补 scan_unicode_contamination.py 的盲区）。

`scan_unicode_contamination.py` 的 SUSPICIOUS_BLOCKS 已覆盖 Cyrillic / Hebrew /
Devanagari / Latin Extended Additional 等 13 个 Unicode 块。但它**漏报**：

  - **Hiragana (U+3040-309F)**：LLM 中文叙事拟仿日文评论区时可能混入，
    例 ln005_第五章：「这条是ちゃぁ你?求问哪一年的省赛」中的 `ちゃぁ`。
  - **Katakana (U+30A0-30FF)**：同理。
  - **Latin-1 Supplement (U+00C0-0xFF)**：含 `í é ñ à …`，比 `À-ÿ` ASCII 范围
    更靠前但同时也比 U+1E00 Latin Extended Additional 更靠前。例 ln004_第四章：
    `评论区里ríos的人比昨天更多了` 中的 `í` (U+00ED)，被
    `[a-zA-ZÀ-ÿ]{2,}` 误判合法通过。

另外补两类 `scan_unicode_contamination.py` 与 `scan_garbled()` 都不覆盖的：

  - **Python 标识符泄漏到对白前缀**（note 17 新子型）：对白列表
    `「这位老哥,.ObjectMeta来这巷子里吃饭的...」——张师傅` 中的 `.ObjectMeta`，
    是 LLM 在概念建模阶段把 Python 类名连同点号整个携入对白文本里。`[a-zA-Z]{3,}`
    能抓 `ObjectMeta` 但抓不到带点号前缀的整词；需用 `[.\w]+\.[A-Z]\w+` 探测。
  - **繁简混排**（同一 CJK Unified 块内）：ln006_第六章「小舌頭」中的 `頭` 虽然
    是合法 CJK 字符，但简体正文里出现繁体构件是 LLM 跨 locale 输出的痕迹，会
    在投递给读者前破坏一致性。本脚本通过对照常用繁简转换字典子集检测。

用法：
    python3 scan_cjk_prose_pollution.py /path/to/light_novel
    python3 scan_cjk_prose_pollution.py /path/to/chapter.md

无污染 → 退出码 0。
检测到污染 → 退出码 1，列出文件 + 命中类型 + 上下文。

仅用标准库。可与 `scan_unicode_contamination.py` 并行运行，互不替代。
"""
import sys
import re
import glob
import os

# 扩展的 SUSPICIOUS_BLOCKS —— 补 scan_unicode_contamination.py 漏报的三个块
EXTENDED_BLOCKS = [
    (0x00C0, 0x00FF, "Latin-1 Supplement"),  # 含 í é ñ à ç … 补 ASCII 误漏
    (0x3040, 0x309F, "Hiragana"),             # ちゃぁ 等
    (0x30A0, 0x30FF, "Katakana"),             # ツ 等
]

# 与 scan_unicode_contamination.py 一致：结构性 ASCII 片段忽略
SAFE_PATTERNS = [r"ILLUST_\d+", r"<!--\s*ILLUST_\d+\s*-->"]

# Python 标识符泄漏到对白前缀的探测正则
#    「<文本>.<CapitalizedWord>...」或 「<文本>.<lowercase>...」
PY_IDENT_LEAK = re.compile(r"[.\w]\.[A-Za-z][\w]{3,}")

# 繁简混排检测子集：常用繁体字（简体正文中不该出现的几个高频代表）
# 这不是完整转换表，仅最常被 LLM 误带的繁体构件——发现后再用更大表复核。
COMMON_TRADITIONAL_VARIANTS = {
    "頭": "头", "體": "体", "個": "个", "來": "来", "們": "们",
    "這": "这", "樣": "样", "說": "说", "對": "对", "時": "时",
    "點": "点", "後": "后", "裡": "里", "內": "内", "兩": "两",
    "邊": "边", "過": "过", "發": "发", "進": "进", "見": "见",
    "飲": "饮", "食": "食", "飯": "饭", "館": "馆", "鍋": "锅",
    "嚐": "尝", "鹹": "咸", "辣": "辣", "湯": "汤", "菜": "菜",
}


def scan_text(text):
    cleaned = text
    for pat in SAFE_PATTERNS:
        cleaned = re.sub(pat, " ", cleaned)

    block_hits = []  # (block_name, char_hex, ctx)
    for lo, hi, name in EXTENDED_BLOCKS:
        for ch in cleaned:
            if lo <= ord(ch) <= hi:
                idx = cleaned.index(ch)
                ctx = cleaned[max(0, idx - 12):idx + 13].replace("\n", "\\n")
                block_hits.append((name, f"U+{ord(ch):04X}", ctx))
                break  # 每 block 取一个代表样例

    ident_hits = []
    for m in PY_IDENT_LEAK.finditer(cleaned):
        idx = m.start()
        ctx = cleaned[max(0, idx - 8):m.end() + 12].replace("\n", "\\n")
        if any(seg.islower() for seg in m.group(0).split(".") if seg):
            # 至少有一节是 lowercase（避免擒住正常的英文句号简写）
            ident_hits.append((m.group(0), ctx))

    trad_hits = []
    for trad, simp in COMMON_TRADITIONAL_VARIANTS.items():
        if trad != simp and trad in text:
            idx = text.index(trad)
            ctx = text[max(0, idx - 12):idx + 13].replace("\n", "\\n")
            trad_hits.append((trad, simp, ctx))

    return block_hits, ident_hits, trad_hits


def scan_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return scan_text(f.read())


def main():
    if len(sys.argv) < 2:
        print("Usage: scan_cjk_prose_pollution.py <dir_or_file>", file=sys.stderr)
        sys.exit(2)

    target = sys.argv[1]
    files = []
    if os.path.isdir(target):
        ln_dir = (os.path.join(target, "light_novel")
                  if os.path.basename(target) != "light_novel" else target)
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
        block_hits, ident_hits, trad_hits = scan_file(f)
        dirty = bool(block_hits or ident_hits or trad_hits)
        if dirty:
            any_dirty = True
            print(f"\u26a0 {f}")
            if block_hits:
                print("  新 Unicode 块越界:")
                for name, cp, ctx in block_hits:
                    print(f"    [{name}] {cp}  ctx: ...{ctx}...")
            if ident_hits:
                print("  Python 标识符泄漏到正文:")
                for tok, ctx in ident_hits:
                    print(f"    \u2192 {tok}   ctx: ...{ctx}...")
            if trad_hits:
                print("  繁简混排:")
                for trad, simp, ctx in trad_hits:
                    print(f"    \u2192 {trad} (应为 {simp})  ctx: ...{ctx}...")
        else:
            print(f"\u2713 {f}  干净")

    sys.exit(1 if any_dirty else 0)


if __name__ == "__main__":
    main()
