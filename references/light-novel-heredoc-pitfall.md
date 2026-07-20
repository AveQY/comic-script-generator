# 中文正文的写入路径与 heredoc 损坏陷阱（2026-07-08 第四次单批项目补充）

## 背景

第四次单批项目（《DemoProjectM》，美食治愈，3 章前传）在写第三章 `ln003` 时命中一个前面三次单批项目都没碰到的失败模式：用 `terminal` 工具运行 `python3 << 'PYEOF'` + `r"""…"""` raw 三引号字符串写章正文，结果文件内容被严重损坏。

## 损坏现象

- Python 直接报 `SyntaxError: unterminated triple-quoted string literal (detected at line N)`，脚本根本没执行完。
- 即使不报语法错（短一些的正文），写入的文件也会出现以下残留碎片：
  - `]='\''`、`'\\''` 等 shell 引号转义残片粘进中文字句中段
  - `yesterday,."`、`isVisible`、`jar勤`、`Visibility(true)` 等英文/代码片段混入
  - 句子被腰斩，后半段变成不可读的非自然语言碎片
  - 对白 `「…」` 结构被打散，`——角色名` 后缀脱离对应行
- 一旦命中，整章不可用，必须丢弃重写——不能靠 `patch` 逐句修，损坏范围太大。

## 根因

Shell heredoc（`<< 'PYEOF'`）的定界处理与 Python raw 三引号字符串（`r"""…"""`）嵌套时，两层分隔/转义规则互相干扰：

1. heredoc 的 `'EOF'` 引号抑制了 shell 的变量展开，但 heredoc 仍然按行读取并在末尾寻找匹配定界符。
2. `r"""…"""` 内部若含有形似定界符边界的内容、或中英文混合触发 shell 的行级解析，会导致字节流提前终止或异物入侵。
3. 这与 SKILL.md note 7 已记录的「Shell heredoc 禁用于漫画脚本」是同一类问题，但那条例针对的是含 `**`/反引号/AI 提示词代码块的**漫画稿**；纯中文小说正文理论上没有这些字符，却仍会损坏——因为有人物对白里出现的「'南'字」「'勿忘我'」这种单引号、以及 `——`、`「」` 等全角字符，与 heredoc 的引号定界产生不预期交互。

## 正确写入路径（本次实测全过）

**首选：`write_file` 工具单次写入整章。**
- 本次第三章 `ln003` heredoc 失败后，改用 `write_file` 工具直接写入约 11.7KB 中文小说正文（含《DemoProjectM》第三章约 3200 中文字符 + 4 个 `<!-- ILLUST_N -->` + 对白 + 章末钩子），一次写入成功，无损坏，无截断。
- 这与 `light-novel-single-batch-generation-2026-07-08.md` 已记录的「正文逐章 `write_file`」模式一致——本次补充的是「即使全集一卷只有这一种写入路径，作用域依然稳定，不要因正文不含反引号/`**` 而尝试 heredoc 替代」。

**降级：`write_file` 失败时，把正文存为独立 `.py` 文件再运行。**
- 把 `content = """…"""` 放在一个独立的 `gen_ln003.py` 文件里（用 `write_file` 工具创建该脚本），再 `python3 gen_ln003.py` 执行——这样字符串从文件读入，不经过 shell heredoc 的定界层。
- 注意 `content` 要用普通 `"""…"""` 而非 `r"""…"""`——raw 字符串在中英文混合 + 全角标点下并不提供额外好处，反而干扰转义意图识别。

**禁止：任何形式的 shell heredoc 包裹多行中文正文。**
- `cat << EOF` / `cat > f << 'EOF'` / `python3 << PYEOF` + `r"""…"""`——全部禁用，不论正文是否含 Markdown 特殊字符。
- 这是对 SKILL.md note 7「禁止 Shell heredoc 写入漫画脚本」规则在小说路线的等价扩展：note 7 给出的理由是漫画稿含 `\`**\``/反引号，而本次显示小说稿即便只有全角标点和单引号对白，heredoc 仍会损坏。

## 验证损坏的方法

写入后立即跑一段最小校验，识别 heredoc 残留：

```python
import re
t = open(path, encoding='utf-8').read()
# heredoc 残留特征
residue = re.findall(r"\]='''|\\\\''|isVisible|jar勤|Visibility\(true\)|yesterday,\.", t)
# 标准小说格式完整性
cn = len(re.findall(r'[\u4e00-\u9fff]', t))
illust = re.findall(r'<!-- ILLUST_(\d+) -->', t)
hook = '## 章末钩子' in t
poll = re.findall(r'\*\*格子\*\*|\*\*构图\*\*|### Panel|## Page', t)
dials = re.findall(r'「.*?」——[^\n]+', t)
print(f'residue={len(residue)} cn={cn} illust={illust} hook={hook} poll={poll} dials={len(dials)}')
```

若 `residue > 0` 即命中 heredoc 损坏——丢弃文件重写，不要逐句修。

## 与现有规则的关系

- `light-novel-single-batch-generation-2026-07-08.md` 模式一已说「正文逐章 `write_file`」，本节补充其**反面案例**：为什么要逐章 `write_file` 而不是塞进一个 Python heredoc——因为 heredoc 会损坏中文正文，不是「会膨胀」（膨胀是元数据脚本的问题，见同文「元数据集中脚本」段的体积警示）。
- SKILL.md note 7 的禁令范围从漫画稿扩展到小说正文——两者统一为「heredoc 禁用于任何含中文对白/全角标点的多行正文」。
