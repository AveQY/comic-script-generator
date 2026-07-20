# write_file / terminal 工具框架 XML 伪标记泄漏（2026-07-08）

## 背景

本次《赛博2047》轻小说第5章续写采用模式四（逐章 Python 生成器脚本），发现一类此前未收入的污染形状：**Hermes 工具调用框架自身的 XML 标记泄漏到被写入文件的正文中**。这不是 LLM 输出的乱码，也不是 heredoc/`write_file` 传输层损坏（note 7/12/15 记录的三类），而是**工具调用协议的响应包装碎片被 LLM 作为"正文"一并生成**，然后通过 `write_file` 写入脚本文件——最终出现在脚本内嵌的 Python 字符串字面量中，进而流入生成的正文文件。

## 实测实例（2026-07-08《赛博2047》ln005 首稿）

### 污染 A：函数结果标记块

```
最近三次登录时间。

<function_results>STATUS: execute_tool_calls
</function_results>

第一次：2146年7月3日。
```

**特征**：`<function_results>...</function_results>` 是 Hermes 工具输出包装标签。LLM 在生成正文时，把"最近三次登录时间"的列表渲染与"接下来应该看到工具返回结果"这一内部预期混在一起输出，于是在列表标题和第一项之间插入了一整块假的函数返回标记。

### 污染 B：调用结尾标记

```
print(f'英文={en[:8]} _X_={pseudo} U+FFFD={u_fffd} Cyr={cyr} 漫画={manga}')
</invoke>
```

**特征**：`</invoke>` 是 Hermes 工具调用块的闭合标签。LLM 在生成 Python 脚本最后一行后，额外输出了 `</invoke>`——这行不是 Python 语法，直接导致 `SyntaxError: invalid syntax (line 155)`，`write_file` 的 lint 检查捕获此错误。

### 污染 C：外语词替换中文语素

```
用随身携带的微型钳把它 Shepard 断了。              → 应为"剪断了"
也不是研究所旧 Rim 的学术级设备。                  → 应为"旧式的学术级设备"
他已经在这里 aspettando 了一个多小时               → 应为"停留了一个多小时"
```

**特征**：不是英文碎片插入，而是**整个外语词整词替换中文语素**——"Shepard"（人名）替"剪"、"Rim"（英文名首音）替"式"、"aspettando"（意大利语"等待"）替"停留"。与 garbled-cleanup ref §类型2 的区别：类型2 是"中文句中混入英文词"（词存在但位置错误），本类是"中文词被外语词替换"（原词消失）。当前 `[a-zA-Z]{3,}` 正则可捕获，但定位逻辑需识别"这个词不应该出现在这里"而非"多余词"。

## 检测方式

### 方式一：lint 自动捕获（仅限生成器脚本路径）

如果用模式四写 Python 生成器脚本，`write_file` 的语法检查会自动捕获非 Python 语法的 XML 标记。表现为：

```
SyntaxError: invalid syntax (line NNN)
```

**但这只捕获脚本文件中的 XML 标记**。如果标记在脚本内嵌的 Python 字符串字面量中（而非脚本顶层），Python 语法解析不会报错——因为字符串字面量内部允许任意字符。这种情况只能靠方式二/三捕获。

### 方式二：在生成器脚本内联验证中加入 XML 标记扫描

```python
import re
t = open('light_novel/lnNNN_第N章.md', encoding='utf-8').read()
xml_leak = re.findall(r'</?(?:function_results|invoke|parameter|tool|antml)[^>]*>', t)
print(f'XML伪标记: {xml_leak}')
```

应扩展已有的五项自检 SOP（SKILL.md note 8/15）为七项，追加 XML 标记扫描。

### 方式三：终端 grep 一行确认

```bash
grep -n '</\?function_results\|</\?invoke\|</\?parameter\|</\?antml' light_novel/ln*.md
```

## 修复路径

与 garbled-cleanup ref 的修复路径一致——用 `patch` 精确替换或 Python `str.replace`：

```python
fixes = [
    # 删除整块假函数返回标记（含前后空行）
    ('\n<function_results>STATUS: execute_tool_calls\n</function_results>\n', ''),
    # 删除脚本末尾的调出标签
    ('\n</invoke>\n', '\n'),
    # 外语词替换中文语素
    ('把它 Shepard 断了', '把它剪断了'),
    ('旧 Rim 的学术级', '旧式的学术级'),
    ('已经在这里 aspettando 了', '已经在这里停留了'),
]
for old, new in fixes:
    content = content.replace(old, new)
```

**注意**：删除块状 XML 标记时，`old` 字符串应包含前后空行以避免留下连续空行。删除脚本末尾 `</invoke>` 时，注意它可能混入 `\n` 导致 Python 字符串字面量语法仍合法（只是输出文件多一行非正文内容），或导致脚本语法错误（如本例）。

## 与其他污染类型的层级关系

| 污染类型 | 来源 | 检测 | 已收录 |
|---------|------|------|--------|
| heredoc 损坏（note 7/12） | Shell heredoc 定界层 | heredoc 残留扫描 | ✓ |
| write_file 传输层损坏（note 15） | write_file 工具调用传输层偶发 | 七项自检 SOP | ✓ |
| Cyrillic/Hebrew/Latin 块越界 | LLM tokenizer 误输出 | `scan_unicode_contamination.py` | ✓ |
| ASCII 标记/URL/单字母（garbled ref §5） | LLM 输出尾部泄漏 | `scan_garbled()` 类型5 | ✓ |
| 汉字夹英文再接汉字（garbled ref 续） | LLM 内部 script 切换 | `[\u4e00-\u9fff]{1,3}[a-zA-Z]{2,}[\u4e00-\u9fff]{1,3}` | ✓ |
| **工具框架 XML 伪标记（本文档）** | **Hermes 工具调用协议碎片** | **XML 标记正则 + grep** | **本文档** |

**关键区别**：本类污染的来源是**工具框架自身**而非 LLM 的 tokenizer 误输出。碎片的形态是 Hermes 工具调用协议已知的标签名（`function_results`/`invoke`/`parameter`/`antml` 等），而非随机 Unicode 块字符。这意味着搜索这类标记的词表是封闭的、可枚举的——比检测随机乱码容易。

## 与"本次出现的#else 和 #fix 等 Python 残留"的关系

这种 Python 残留提供了一种早期警告模式的反例外：`write_file` 的 lint 检查在 Python 生成的文件的 case 里可以通过，但如果 `.py` 文件本身在被其他工具直接解析，错误标记的出现会触发 Python `SyntaxError`。因此从模型行为角度看：
- `write_file` Python 路径标记泄漏时，文件内部已有 $\geq 1$ 个非 Python 语法字符 → Python linter 报错（如 `SyntaxError`），作为"强检测信号"。
- `write_file` 正文路径（Markdown 正文直接 `write_file`）标记泄漏时，正文文件没有 lint → 只能靠七项 SOP 中的 XML 扫描正则或终端 grep 捕获。

## 预防建议

1. **模式四生成器脚本路径是更可靠的早期警告构型**：`write_file` 写 Python 脚本时，SyntaxError 是免费的检测器。
2. **直接 `write_file` Markdown 正文路径需在七项 SOP 中显式加入 XML 标记扫描**——本文档方式二给出的正则。
3. **外语词替换中文语素**一类，已被 `en = re.findall(r'[a-zA-Z]{3,}', cleaned)` 在五项 SOP 中覆盖——但判断"是否为合法专名"仍需人工或 LLM 二次检查（如本作的"B-07"和"R-101"是合理编号，而"Shepard"/"Rim"/"aspettando"不是）。
