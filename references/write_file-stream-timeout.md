# write_file Stream Timeout: ~8K Token Argument Limit

## 现象

调用 `write_file` 写入含大量中文的长篇正文（~14KB+ 脚本文件）时，工具调用在服务端等待完成时**整个 tool call 的序列化参数超过 ~8K tokens**，导致流传输超时，返回错误：

```
System: Your previous tool call was too large and the stream timed out...
Each tool call's arguments must be under ~8K tokens to avoid stream timeouts.
```

**注意**：这与 `write_file` 本身的能力上限（已验证可稳定处理 48KB+ 文件内容）不同——工具参数序列化后的 `content` 字段中的大量 Unicode 中文会迅速膨胀 token 计数，同一文件内容在工具参数里消耗的 token 远大于文件在磁盘上的字节数。

## 触发条件

- 单个 `write_file` 调用中 `content` 参数包含 **大量中文文本（>~4K 中文字符 或 总参数序列化 >8K tokens）**
- 常见于：一次性写入单章中文小说正文、包含大量中文 Markdown 的配置文件、含中文对话的脚本

## 解决方案（优先级降序）

### 方案 A：Python 生成器脚本（推荐，新写项目用）

把文件内容写入一个独立的 `.py` 文件，然后用 `write_file` 创建 + `terminal` 执行：

1. 用 `write_file` 创建一个 `gen_chapterN.py`，其中 `content = """..."""` 包含完整章节正文
2. `terminal(command="python3 gen_chapterN.py")` 执行脚本
3. 脚本内 `open(path, 'w', encoding='utf-8').write(content.strip())`
4. 验证：在脚本末尾加内联统计（字数、ILLUST 数、中文字符数）

**每脚本只写一个文件**，避免单个 `.py` 文件过大再次触发同样的 timeout。

```python
# gen_chapter1.py 模板
import os
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "light_novel")
os.makedirs(OUTPUT_DIR, exist_ok=True)

content = """...完整内容..."""

path = os.path.join(OUTPUT_DIR, "ln001_第一章.md")
with open(path, 'w', encoding='utf-8') as f:
    f.write(content.strip())

# 内联验证
c = open(path, encoding='utf-8').read()
print(f"中文字符: {sum(1 for ch in c if '\u4e00'<=ch<='\u9fff')}")
print(f"ILLUST: {c.count('<!-- ILLUST_')}")
```

### 方案 B：单脚本批量写入（≤6 文件，推荐已有目录结构的项目）

将全部元数据 + 章节内容写入一个 Python 脚本，末尾附验证段。详见 `references/light-novel-single-script-generation-2026-07-08.md`。

### 方案 C：分拆工具调用

- 先 `write_file` 写入不含中文的骨架/模板
- 再用后续 `patch` 分多次注入中文段落（注意 patch 也有类似陷阱，见 `references/patch-intext-pitfall-2026-07-08.md`）

**不推荐**：逐行 shell heredoc（已知会损坏中文内容）。

## 自检清单

用 `write_file` 写入含中文的文件前，估算参数序列化后的 token 数：
- 1 个中文字符 ≈ 1-2 tokens（UTF-8 字节数 3 但 tokenizer 通常压缩更好）
- 安全上限：content 参数中纯中文不超过 ~4K 字符（约 12KB UTF-8）
- 超过时直接使用方案 A 或 B

写入后必须验证：
1. 文件存在：`os.path.exists(path)`
2. 行数/字节数合理：`wc -l -c`
3. 中文字符数达标（每章 ≥2500 CJK）
4. 无残留碎片（`re.search(r'\\];|\\}\\s*$|\\\\]=\\'', text)`）
5. 运行 `validate_light_novel.py`（小说路线）或 `validate_episode.py`（漫画路线）
