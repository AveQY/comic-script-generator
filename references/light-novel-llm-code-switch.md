# 轻小说 LLM 生成中途"语码切换"注入（2026-07-08）

## 现象

与 `light-novel-garbled-text-cleanup-2026-07-08.md` 的乱码类不同，本类**不是** heredoc 损坏，也**不是** tokenizer 把相邻 Unicode 块拼错——而是 LLM 在写一段较长的中文叙事时，"中途切了语言"：句子语法仍是中文，但中间夹了一两个非中文词，像是模型在预测下一个词时短暂漂进了别的语料域。

2026-07-08《我在精神病院当厨子》批量续写实测：

| 实际输出 | 应为 | 类型 |
|---|---|---|
| `像抱了一整个十年的重量—— maniera像抱了一整个` | `像抱了一整个十年的重量——像抱了一整个` | 意大利语副词 `maniera` |
| `他 Stato把那份东西塞进外套` | `他把那份东西塞进外套` | 意大利语 `Stato`（状态） |
| `这份重量，比他炸十五年鱼还要沉—— weighs more than fish。` | `这份重量，比他炸十五年鱼还要沉。` | 英语短语 `weighs more than fish` |
| `因为他们第——log——第四天会盘库` | `因为他们——第四天会盘库` | 英语 `log` |
| `不是为了"CCTV餐饮大会"` | `不是为了"上电视出名"` | 英文缩写 `CCTV` |
| `indefinite leave——就是那种不说回来日期的"家事假"` | `无期限事假——就是那种不说回来日期的"家事假"` | 英语短语 `indefinite leave` |

**共同特征**：
- 词性以**副词/名词/常用动词**为主，不是技术术语或专有名词——像是模型在找"下个意象"时跨进了英语/意大利语的高频词区。
- 位置**不固定**：出现在叙事句中、角色口头语中、对白归因句中、章末钩子段中均有出现。
- 每个**注入点独立**——一次会话里可能多次出现，但每次的词不同、语言也不同（意大利语和英语可以同章混出）。
- 上下文越长的段落、悬念越浓厚的段尾、跨"两段叙述一件事"的中段，出现概率越高。

## 与既有污染类的关系

| 类别 | 来源 | 检测 |
|---|---|---|
| heredoc 残留（`]='`/`isVisible`） | Shell `<<PYEOF` + 原始字符串损坏 | `verify_light_novel_delivery.py` 的 HEREDOC_RESIDUE |
| Cyrillic/Hebrew 块越界 | tokenizer 解码跨 Unicode 块 | `scan_unicode_contamination.py` |
| 对话标记蛇形后缀（`——陆远舟_joint`） | LLM 把英文动作描述贴在角色名后 | `verify_light_novel_delivery.py` 的 attribution_residue |
| **本类：叙事内语码切换** | LLM 生成中预测下一词时跨语料域漂移 | `verify_light_novel_delivery.py` 的 ASCII_IN_CJK 能抓 3 字母以上，但 2 字母词（如 `log`）需其紧邻 CJK 才命中 |

**重要**：`verify_light_novel_delivery.py` 的 `ASCII_IN_CJK` 正则要求 ASCII 前后紧邻 CJK 字符。一个被中文破折号或中文标点夹住的英文短词（`——log——`、`"CCTV餐饮大会"`）可能因边界字符不全是 CJK 而漏检。投递前**额外手扫一次** `[a-zA-Z]{2,}` 排除 `ILLUST` 这种合法标记，是最后一道闸。

## 缓解建议

### 生成阶段（最有效）

- **单章分块生成**：观察到 10–12KB / ~2600 CJK 的单章 `write_file` 直写，污染点集中在章末高潮段（ chase / fight / 揭秘段）的后 1/3。把"日常铺垫"和"高潮揭秘"分两次 prompt 生成、再在终端里拼接，比一次性 12KB 直写更稳——因为高潮段是 LLM "跃迁到别的语料"的高发段。
- **prompt 里只用中文意象**：用户/角色特性描述里别夹英文 phrase。本类污染与 prompt 里是否含英文无强关联，但含英文意象（如 `narrow her eyes`）会显著放大漂移概率（同 `light-novel-garbled-text-cleanup-2026-07-08.md` §3.2 的教训一致）。
- **章末钩子段单独 prompt**：章末钩子是叙事密度最高的一段，独立用一轮 prompt 生成可显著降污染率。

### 验证阶段

- 每章写完立刻跑一次 `verify_light_novel_delivery.py`（含 ASCII_IN_CJK 扫描），不要等整批写完再扫——污染最易发生在最后写的两章，整批扫可能让你漏掉"已经覆盖的章节也受伤"。
- 对 `verify_light_novel_delivery.py` 跑过仍不放心的章节，追加一个"剥离合法 ILLUST 标记后的任意 2+ 字母 ASCII 残留"扫描：

```python
import re
t = open(path, encoding='utf-8').read()
# 去掉合法的 ILLUST 插图标记和 fenced ```text``` 块
t_clean = re.sub(r'<!-- ILLUST_\d+ -->', '', t)
t_clean = re.sub(r'```text.*?```', '', t_clean, flags=re.S)
ascii_runs = re.findall(r'[a-zA-Z]{2,}', t_clean)
print('non-ILLUST ASCII runs:', ascii_runs)  # 任何输出都需人工判断
```

### 修复阶段

- 单词级污染用 `patch` 工具一次性替换（`old_string` = 污染短句、`new_string` = 修复短句）即可，无需 `str.replace` 列表——因为本类污染是**离散点**，不是**模式批量**。
- 修复后回到"验证阶段"再扫一遍，确认本章已无 ASCII 残留。

## 本次实测数据

项目：《我在精神病院当厨子》第 4–11 章批量续写（2026-07-08）。
- 8 章 `write_file` 直写（每章 10–12KB），全部无 heredoc 残留（因为用的就是 `write_file`，源头上没有 heredoc 层）。
- 4 章出现语码切换注入（ch9 三处意大利语 + 一处英语、ch10 两处 lowercase 关键词、ch11 一处 `indefinite leave`），共 7 处，全部被 `[a-zA-Z]{2,}` 后处理正则抓到。
- 每处用 `patch` 单次替换修复，零误伤、零状态脱节（因为 `patch` 的 `old_string` 用了较长上下文锚定，未触发隐式误替换）。
- 修复后所有章节 `ASCII whole (excl ILLUST)` 返回空列表。

## 给上游脚本的建议（未来集成）

`verify_light_novel_delivery.py` 增加一个 `narrative_code_switch` 检查：
- 扫描去掉 `<!-- ILLUST_N -->` 和 ` ```text...``` ` 之后的正文，
- 报告所有 `[a-zA-Z]{2,}` 序列（不只 ASCII_IN_CJK 的"夹在 CJK 中间"情形），
- 列出后让人工/LLM 判断哪些是合法的（如"AI"、"5G"缩写）哪些是污染。
- 这是对现有 `ascii_in_cjk` 的增量，不是替换——后者对"夹在 CJK 中间"的英文最准，但对前后是中文标点的短英文漏检。
