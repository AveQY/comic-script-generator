# 逐章生成中途断流后的续写模式

> 2026-07-08《匿名差评师》第5-10章续写实测。用户指定一次性写 8 章（ln005-ln012），每章约 2500-3500 中文字符，走轻小说正式输出路径。

## 背景

主会话用 `write_file` + `patch` 逐章生成。两次因网络错误被中断：
- 第一次中断时写在 ln005 中途（仅 ~3.4KB 写入）。
- 第二次中断时写在 ln007 中途（已写完正文前半）。

系统注入了 `"The previous response was cut off by a network error mid-stream. Continue exactly where you left off. Do not restart or repeat prior text."`，这是 Hermes 框架级重启提示。会话被清空后从提示点重开，之前的输出不可恢复，必须由 agent 自己判断当前文件状态并决定续写策略。

## 续写时实际采用的策略（实测有效）

1. **先 `read_file` 受影响的章节**——不是只看最后几行，而是整章读完。中断会留下半截文件：
   - 例如 ln005 在第二次 `write_file` 时只剩 ~3.4KB 的前半章；
   - ln007 只写了章节正文的前 4 个 `---` 分隔场景，后两个场景（ILLUST_3、章末钩子）未写。

2. **续写策略有两种，按文件破坏程度选择**：
   - 局部截断（文件干净但末尾缺失章节钩子/下一段）：用 `patch` 追加缺失段；
   - 文件不完整且需从中间续写：直接用 `write_file` 覆写整章——比将"前半截 + 新内容"拼接更稳，因为 `write_file` 的 `content` 参数中长段中文叙事散文混合容易触发段落级肌理损坏（见 SKILL.md note 8 v1.19.1 + `references/write_file-paragraph-level-corruption-2026-07-08.md`）。

3. **判断策略的关键原则**：文件被中断的部分如果**已包含半段不完整的中文叙事且这段叙事看起来已经肌理退化**（字的语义错乱、多脚本污染、或尚未章末换行的 markdown 结构损坏）——**不要**尝试用 `patch` 修补这段；直接整章 `write_file` 覆写，并且让覆写版完全复述段落语义而不是从半截续写，避免从污染状态衔接。

4. **本会话中观察到的两类退化**（已由 SKILL.md note 8 v1.19.1 覆盖）：
   - 段落级多脚本乱码（Cyrillic / Hebrew chars / 英文整词 `OR`/`AND`）在 `write_file` 的 `content` 参数流式传输时混入。机械验证的覆盖盲区与 note 8 记录一致：Cyrillic 块已由 `scan_unicode_contamination.py` 覆盖，但段落级的连贯乱码（整段叙事语义错乱而非孤立字符）只能靠通读捕获。
   - `patch` 追加时同样可能触发肌理退化——`patch` 的 `new_string` 参数在 LLM 生成时也会携带相邻 script 字符污染。本会话 ln010 章「顾明远透露任务系统」段经历了完整的乱码段落，后在下一次 `patch` 中被整段替换修正。

## 在断流后实施的强制自检（复用已有 SOP）

续写完成某章后立即跑：
```python
import re
t = open('lnXXX_第X章.md', encoding='utf-8').read()
cjk = sum(1 for c in t if '\u4e00' <= c <= '\u9fff')
fmt = len(re.findall(r'^「.+?」——.+$', t, re.M))
illust = len(re.findall(r'<!--\s*ILLUST_\d+\s*-->', t))
sep = len(re.findall(r'^---$', t, re.M))
cleaned = re.sub(r'<!--.*?-->', '', t)
en = [g for g in re.findall(r'[a-zA-Z]{3,}', cleaned)]
cyr = re.findall(r'[\u0400-\u04ff]{2,}', t)
hebr = re.findall(r'[\u0590-\u05ff]{2,}', t)
print(f'CJK={cjk} 对白={fmt} 插图={illust} 分隔={sep} 英文={en[:6]} Cyr={cyr} Hebr={hebr}')
```

**特别注意 Cyrillic/Hebrew 的模式**：当 LLM 在长段中文叙事散文中切到类似"顾明远说出系统机制"这种近似技术陈述的密集对白段时，多脚本污染概率显著升高。这些段落往往强调 AI、系统、code、IP、域名、http header 等术语，LLM 的 tokenizer 在中英邻接场景下最容易将相邻 script 字符误输出为 Cyrillic/Hebrew。这是 `write_file` 调用前应预判的高风险段落类型——在 LLM 视角里，它已经在为某个段去想 API/代码，相邻的中文叙事散文在抽样时会被这些 tokenizer 状态"染上"。

## 续写断点定位 SOP

1. 被「cut off」重启后，首要工具调用应是 `search_files target='files' pattern='ln0*第*章.md'` 获取当前章节文件的清单与修改时间。最近修改的文件即为中断所在文件。
2. 之后 `read_file` 该文件——从第 1 行至文件末——以确定是「局部截断」还是「中段污染」。
3. 如果文件中最后一段中文叙事不可读（相邻 script / 语义错乱 / 残缺的 markdown 结构），这段叙事往往就是断流时正在生成的那段——它是"半截生成"的产物，必须整章覆写。
4. 如果文件末尾是一个完整的段落或完整的 `---` 分隔符但缺少 `## 章末钩子`，属于"结构尾部缺失"。可用 `patch` 在正文后追加 `---\n\n## 章末钩子\n\n<内容>`，无需整章覆写。

## 何时直接整章 `write_file` 优于 `patch` 补救

- `write_file` 的 `content` 参数在 LLM 生成过程中会携带所有相邻的 tokenizer 状态。当章节中段已经显示出肌理退化时，从退化点续写的 `patch` 会继承退化状态——这是断流续写时最常见陷阱：agent 试图"接着写"，但模型在续写时已经从前段的损坏处中获得了错误的中英混搭 prior，导致新内容继续退化。
- **实测结论**：直接 `write_file` 整章覆写比"续写的 patch"更稳——覆写时 LLM 从章节标题 `# 第X章 章名` 重新生成，tokenizer 状态从头初始化，不继承中段退化。代价是调用 token 多，但比 patch dedupe + 后处理的调用链简洁。

## 与 SKILL.md 现有 SOP 的关系

本 ref 补充 SKILL.md 模式六 note 8（写入后自检 SOP）+ note 12（章节正文写入路径）+ v1.19.1 段落级损坏条目，在断流重启场景下推荐的具体操作。这些做法都可由现有 SOP 覆盖，本文件只是把"agent 遇到断流重启"这一会话状态下的决策序列显式化。

不需要修改 SKILL.md 的 SOP 主体——note 8/v1.19.1 的损坏描述与自检五项已涵盖本会话出现的所有退化类型。本 ref 给将来在断流续写场景下操作时优先选用哪种工具的决策指引。

## 读到这里时的检查清单

- [ ] `search_files target='files'` 确认最新章节文件
- [ ] `read_file` 全文（不是只看末尾）确定文件状态
- [ ] 如果中段乱码/叙事退化：整章 `write_file` 覆写
- [ ] 如果只是尾部 `## 章末钩子` 缺失：`patch` 追加
- [ ] 覆写/chapter 写完后立即跑七项 ASCII / Cyrillic / Hebrew / pseudo-marker 自检
- [ ] 确认 `<!-- ILLUST_N -->` 数量 == 预期（破坏时往往少一张）
- [ ] 确认 `## 章末钩子` 存在且唯一
- [ ] 通读首尾 200 行——这是机械自检的最后一道，断流续写的损坏最可能在"衔接段"出现
