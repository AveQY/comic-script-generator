# patch 工具在中文长篇正文中的误替换陷阱（2026-07-08）

## 背景

生成《米其林一星外卖哥》前3章轻小说时，第一章初稿 CJK 字数 2147（低于 2500 阈值）。按 `light-novel-single-batch-generation-2026-07-08.md` 的"段级补足 loop"方法，用 `patch` 对第一章做增补。但过程中连续触发了 patch 的误替换陷阱，导致文本损坏。

## 陷阱一：`new_string` 的隐式替换范围远超 `old_string`

### 现象

patch 的 `old_string` 精确选择了要替换的目标段，但 `new_string` 写入后，文件中**相邻的整段文字被删除或截断**——这是 LLM 在构造 `new_string` 时，无意中把 `old_string` 周围但不应包含的句子也"重写"了。表现为：

- 替换后某段的句子被截断（如"电动车拐上主路的时候"后面直接跟引号，中间的差评描述段全部消失）
- 替换区域外出现孤立字符（如 `];`、空白行、格式被打散）

### 根因

LLM 模型在写 `new_string` 时，倾向于把"我理解的段落全貌"重新输出，而不是"只把 old_string 的内容加几个句子的增量"。这导致：

1. `old_string` 写的是一段话的"头尾"（如 A 段 + B 段）。
2. LLM 在 `new_string` 中将 A 段重写得稍有不同（多了几句话），将 B 段完全省略。
3. 结果：A 段变了（增补成功），B 段"消失"了——不同部分被"修正"成了空。

### 防御规则

**`new_string` 必须在结构上等于 `old_string` + 新增段，不能省略 `old_string` 中的任何句子。** 具体做法：

1. 写 `patch` 前，先把 `old_string` 原文完整复制到 `new_string` 里，再在合适位置插入新段。
2. 不要尝试在 `new_string` 中重写 `old_string` 的措辞——`patch` 是 replace，不是 rewrite。
3. 复杂增补（涉及多段、跨段落）时，优先 `read_file` 确认区域结构，然后再 compose `old_string` / `new_string`。

## 陷阱二：`new_string` 中无意引入 phantom 字符

### 现象

修一个增补段时，`new_string` 中出现了一个 `];`（像 Python 列表闭合的残留），与中文正文毫无关系。`patch` 将这个 `];` 写进了文件中——不影响 Markdown 渲染但破坏了文件内容，`validate_light_novel.py` 的字数/对白检查不会捕获它。

### 根因

长对话中 LLM 在连续生成多段中文正文后，偶尔会在 `new_string` 中夹入代码片段碎片（`];`, `}`, `</...>` 等）。原因是 LLM 在这种文本模式中会将 Python 生成脚本的结构隐式带入正文生成——前一个 `patch` 是改 Python 脚本的内容，下一个 `patch` 是改正文，但 LLM 没有完全切换模式。

### 防御规则

**每个 `patch` 后立即跑一次 phantom 字符扫描**，同样的验证脚本已经在 `light-novel-heredoc-pitfall-2026-07-08.md` 和 `light-novel-garbled-text-cleanup-2026-07-08.md` 中给出。扫描模式至少包括：

```python
import re
phantom_patterns = [r'\];', r'\}\s*$', r'\]\s*$', r"\\]='", r'isVisible', r'jar']
for p in phantom_patterns:
    if re.search(p, text):
        print(f'PHANTOM: {p}')
```

## 陷阱三：previous `patch` 的部分成果被下一个 `patch` 又修坏

### 现象

为修陷阱一新增的 `"];` 字符，我用第二次 `patch` 修。但第二次 `patch` 写 `new_string` 时又把陷阱一那个之前已经修好的"被截断的段落"再次截断——因为我没去 `read_file`，而是凭对话里的印象直接构造 `new_string`。

### 根因

patch 已经把字段在文件中翻来覆去几十次，但 LLM 没读文件，所以构造 `new_string` 时用的是"我脑海中的状态"，与文件实际状态脱节。每次 patch 都需要与文件真实状态对齐。

### 防御规则

**`patch` 前若对"文件当前内容"有怀疑，必须 `read_file` 再 patch。** 特别是连续多个 patch 修复同一个文件时，每个 patch 都必须基于"上一个 patch 完成后文件的实际内容"，而不是 LLM 内存中的版本。

## 完整安全流程（重要，建议嵌入章节生成 SOP）

每章字数不达标时，patch 增补应执行以下序列：

1. **`read_file`** 目标章节，确认要增补的段落的精确原文。
2. **构造 `old_string`**：取目标段的"头 + 中间一句"——选取在文件中唯一的句子组合。
3. **构造 `new_string`**：把 `old_string` 完整复制进来，再在合适位置插入**新增段（80-180 字）**——不动 `old_string` 的其他部分。
4. **执行 `patch`**。
5. **立即 `read_file` 验证**：读取 patch 后的文件，确认相邻段未消失、无 phantom。
6. **如发现损坏**：基于刚才读到的实际状态再 patch，不要"凭印象修"。
7. **跑字数自检**。
8. **跑 phantom 扫描**。
9. **跑漫画字段污染扫描**。
10. **跑 `validate_light_novel.py`**。

这比直接"凭印象 patch + 验证脚本一次性检查"多 2-3 步，但避免了"修出一章"里夹一个 `];`、相邻段被吃掉这种需要在交付前才发现的"看不见的问题"。

## 与现有文档的关系

本文档与以下文档互补：
- `light-novel-single-batch-generation-2026-07-08.md` 的"字数不够的段级补足 loop"——描述了 patch 增补的位置选择、补足模板，但**没有详述 patch 的失败模式**。
- `light-novel-heredoc-pitfall-2026-07-08.md`——关注 heredoc 写入的 phantom 字符，本文件关注 patch 写入的 phantom 字符和误替换。
- `light-novel-garbled-text-cleanup-2026-07-08.md`——关注跨语言污染检测，本文件补充了"patch 本身也可以引入污染"的视角。

## 建议在 SKILL.md 中加一句话提示

在轻小说模式六的"验证与维护"段（写完每章后运行的检查项那里），建议加一行：

> **`patch` 工具增补正文的安全性（重要）**：使用 patch 增补章节内容时，每次 patch 完成后必须 `read_file` 校验相邻段未被误删、无 phantom 字符（如 `];`、`}`），详见 `references/patch-intext-pitfall-2026-07-08.md`。
