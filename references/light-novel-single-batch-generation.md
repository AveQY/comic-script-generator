# 轻小说单批生成模式与字段隔离规则（2026-07-08）

## 背景

用户要求为《赛博2047》一次性生成完整项目（角色档案、全书设定、伏笔追踪、前3章正文，每章 ≥2500 字）。本次没有用户纠正，但暴露出两个可复用的执行模式，补足 `light-novel-batch-generation-lessons-2026-07-07.md` 侧重批量/扩写场景之外的单次完整项目生成场景。

后续在同日补了《DemoProjectK》《DemoProjectC》《DemoProjectL》《DemoProjectM》四个项目，依次沉淀了已初始化骨架的覆写工作流、章纲 beat 块先于正文、对白格式验证陷阱、heredoc 残留检测、段级补足循环五条规则。各条按发现顺序在下方归类。

## 执行模式

### 模式一：元数据集中脚本 + 章节逐文件写入

第一次单批项目（《赛博2047》）把 `characters.md`、`summary.md`、`foreshadowing.md`、`style_guide.md`、`config.json` 用**一个** Python 脚本一次性写入（每个文件用 `pathlib.Path.write_text`，约 11KB 脚本），然后**逐章**用 `write_file` 工具调用单独写入 `light_novel/ln*.md`。

为什么这样拆：
- 元数据集中在一个脚本里，因为它们之间有共同基础（角色/伏笔/章纲互相引用），放一个脚本里可以保证一致性，且总量约 11KB 远低于工具截断阈值。
- 正文逐章 `write_file` 而非塞进同一个 Python 脚本：每章 7-9KB 占 8000+ tokens，三家合起来一个工具参数就会严重膨胀，触发 `light-novel-batch-generation-lessons-2026-07-07.md` 第 4 条警告的大块参数风险。

适用边界：≥3 章、单章 ≥2500 字、元数据与正文互相引用时用此模式。单章或短测可直接 `write_file` 一次过。

### 已初始化骨架的覆写工作流（2026-07-08 第二次单批项目：《DemoProjectK》）

本次《DemoProjectK》开局：`init_project.py` 之前已建好骨架（`config.json` 已含 `content_mode=light_novel`、`category="都市日常"`、`target_total_chars`、`planned_chapters` 等；`characters.md` 是占位 `「（待生成）」`；`light_novel/` 为空）。此时**不要重跑 `init_project.py`**（会重建/覆盖目录），走"元数据集中脚本直接覆写"路径：

1. `write_file` 一个临时脚本（如 `/tmp/gen_meta_<书名>.py`），把 `characters.md` / `summary.md` / `foreshadowing.md` 用 `pathlib.Path.write_text` 一次性覆写占位内容，再 `json.load`→patch→`json.dump(ensure_ascii=False, indent=2)` 更新 `config.json` 的 `updated_at` 与 `generation_status`，然后 `python3` 执行它。
2. 脚本最后 print 每文件 byte/char 数做自检，确认无空写；删除临时脚本，进入逐章正文写入。
3. 适用边界：骨架已存在且 `config.json` 字段齐全、本章需要满量填充 5+ 角色档 / 7+ summary 键 / 多章伏笔时——脚本集中写比逐文件 patch 占位快得多且一致性更稳。

### 模式二：字数与格式自检（一条 Python 命令）

生成后立即用一条 Python 命令核对所有章节，避免目测误判（参考 `light-novel-batch-generation-lessons-2026-07-07.md` 第 3 条）：

```python
import pathlib
base = pathlib.Path(os.environ.get('COMIC_PROJECTS_ROOT', os.path.expanduser('~/comic-projects/projects'))) / '<书名>'
for f in sorted((base/'light_novel').glob('ln*.md')):
    t = f.read_text(encoding='utf-8')
    ws = len(''.join(t.split()))   # 无空白字符数 = 有效字数
    illust = t.count('ILLUST_')
    has_hook = '## 章末钩子' in t
    print(f.name, ws, 'illusts=', illust, 'hook=', has_hook)
```

关键点：
- 用户把 ≥2500 字定义为「字」而不是「字符」，无空白 `len(''.join(t.split()))` 是较保守的解释，覆盖中文字符、标点、对白符号。
- 同时检查 `## 章末钩子` 字符串存在即可，不是按正则严格匹配标题级别——降低误报。

## 章纲 beat 块先于正文（2026-07-08 第二次单批项目：《DemoProjectK》验证，强制技术）

之前"验收清单"只写"章节间衔接：第 N 章末钩子在 N+1 章前段承接"，但没说**怎么稳定做到**。本次《DemoProjectK》的稳定方法是：**每章正文开头先写一个 `## 章纲 beat` 块，再写正文。** beat 块结构：

```
## 章纲 beat
- **开场钩子**：一句话抓人
- **日常/场景建立**：地点、时间、氛围
- **触发事件**：打破日常的小事件
- **互动推进**：至少 2 次角色互动/对话反转
- **情绪转折**：误会、心动、发现、危机或温暖点
- **章末钩子**：让读者想点下一章
- **关键插图**：3-7 个插图点（实际 `<!-- ILLUST_N -->` 散在正文中）
```

好处：
- 写正文前先把 N+1 章应该承接的钩子写成 beat 字段，强迫章末钩子和下一章开头耦合。本次 ch1 灰鼠键绳/十六进制纹身 → ch2 开头周野拆行李时键绳落地；ch2 许宁电话漏保研 → ch3 林默醒来先去客厅确认那句话"还停在空气里"——三处衔接均一次到位，无重改。
- beat 块本身代价 200-400 中文字符，摊到 2700+ 的章里完全可吸收，但让"续写衔接"从"靠记忆"变成"靠字段"。
- 写作时心里数 beat 的推进节奏，自然避免"40+ 段重复同一画面模板"那一类轻小说版的模板句污染。

**注意**：beat 块属元信息，不在 `validate_light_novel.py` 的字数/对白/插图统计中作主体，但其中的 `## 章纲 beat` / `## 正文` 行会被计入 ws 字符（不影响 cn 字符判断）。本次用户未要求精简，beat 块保留已通过 `validate_light_novel.py`；若用户要求"纯正文无元信息块"，把 beat 块降级为生成时草稿（不写入最终 `.md`），但保留下章承接字段到代码生成器逻辑里。

## 字段隔离规则（"禁止漫画格式"）

用户在本会话开头明确写：「小说正文格式…禁止漫画格式」。这条早已存在于 SKILL.md 模式六「正文写作格式」段，但属于用户优先级指令，应在正文写入前先标识。本次的实现是：
- 正文逐章用 `write_file` 单独写入，每个文件开头留清晰的「正文写作格式」block，然后只写正文段落/对白/插图/钩子。
- 禁止出现在正文中的漫画字段清单（每章校验时也应扫）：
  - `**格子**`、`**构图**`、`**气泡**`、`**旁白**`、`**拟声**`、`**转场**`、`**AI 提示词**`
  - `## Page`、`### Panel`、`## Scene`
  - 表格 `| 字段 | 内容 |`

元数据文件（`characters.md`、`summary.md`、`foreshadowing.md`）则**无此限制**——它们可以包含表格、列表、结构化字段。只有 `light_novel/ln*.md` 正文文件必须严格隔离。

## 对白格式与验证脚本正则匹配（2026-07-08 第三次单批项目补充）

第三次单批项目（《DemoProjectL》，2026-07-08 晚间）暴露一个对白格式陷阱：

`validate_light_novel.py` 用正则 `^「.+?」——.+$` 统计对白数量。这意味着：
- ✅ `「你就是陆时行？」——沈柏舟` ← 匹配，计入对白数
- ❌ `「你就是陆时行？」他问。` ← 不匹配，不计入
- ❌ `「你就是陆时行？」\n他问。` ← 不匹配（跨行），不计入

**风险**：如果正文中大量使用叙述式归因（`「」他说。`）而非 `——角色名` 格式，对白数可能低于 8 轮阈值而验证失败，即使实际对话量充足。

**实测数据**：本次三章对白统计（`content.count('「')`）分别为 24/8/41，但第二章仅 8 条——如果其中有 1-2 条不是 `——` 格式，就会跌破阈值。这是因为第一章和第三章混合使用了两种格式（部分 `——角色名`，部分 `他问。`），而第二章恰好以叙述式归因为主。

**防御措施**：
1. 写完每章后，自检时不仅数 `「` 出现次数，还要数 `^「.+?」——.+$` 匹配次数（即验证脚本的同款正则）。
2. 如果两种口径差距大，说明格式不统一——统一改为 `——角色名` 格式。
3. 自检命令：
```python
import re
matches = re.findall(r'^「.+?」——.+$', text, re.M)
print(f'dialogue_count: {len(matches)}')
```

**写作时最常犯的错误**：LLM 初稿常常全部使用叙述式归因（`「闭嘴。」陆沉打断了它。`），导致后续需要对每章数处对白逐条 `patch` 补改为 `「闭嘴。」——陆沉\n\n陆沉打断了它。` 才能通过验证。**预防方法**：在写正文时，每写一段对白就立即决定该句是否需要 `——角色名` 归属格式（每章至少 3-8 处）；对于独立的短对白、角色名独占行尾的台词、不接叙述的对话，优先使用 `「台词。」——角色名` 独占一行或段首的格式。不要等全章写完再批量补改——补改时需要把叙述句从对白行拆出、重新分段，极易引入重复或错位文本。

### 章末自检：零计数陷阱与整章重写辨析（2026-07-09 第N+1次单批项目补充，《DemoProjectE》验证）

即便熟记上面的"预防方法"，仍会出现整章 `content.count('「')` = 25+ 但 `validate_light_novel.py` 的 `dialogues < 8` 误报——根因是初稿通篇叙述式归因（`「」他说。`），验证脚本的同款正则 `^「.+?」——.+$` 一条也匹配不上。**关键**：`「」——角色名` 的 `——` 必须与对白同行，且对白须以 `「` 开头、`」` 收束、`——` 紧接、`角色名` 紧随——这条格式一旦全章缺位，对白数会直接归零（不是"少几条"）。

**单条自检命令**（写完每章立刻跑，可在投入写下一章前抓到陷阱，避免多章累积返工）：

```python
import re, pathlib
t = pathlib.Path('light_novel/lnXXX_<章名>.md').read_text(encoding='utf-8')
n_open = t.count('「')
n_fmt = len(re.findall(r'^「.+?」——.+$', t, re.M))
print(f'open_braces={n_open} dialogue-formatted={n_fmt}')
if n_fmt < 8 and n_open > n_fmt: print('!! 对白未被正则统计：全章叙述式归因，需重写.')
```

**"全章零计数 ≠ 整章重写"的辨析（修正之前类似的表述）**：当 `n_fmt == 0`（或远低于 `n_open`）时，应是**全章 write_file 一次覆写** `——角色名` 格式，而**不是**逐条 `patch`——逐条 patch 一条对白需把 `「」他说。` 拆成两行重排，一章二十余条做下来触发易错/重复/段错位的概率逼近于全章重写，且耗时更长。本节此前的"禁止整章重写"**仅适用于字数不足时的段级 patch 增补**，**不适用于对白格式整体缺位**——后者整章 `write_file` 一次过本日实测（《DemoProjectE》Ch1）三口径一次性全过：cjk=2980 / nonws=3516 / dialogues=21，对白格式一改全达，免于逐条补改。

落地基线（2026-07-09 三章一次性达标）：M1=2980/3516/21、M2=2861/3440/29、M3=2981/3535/28（cjk_chars / nonws / dialogue-formatted），三章零近重复、零漫画字段、零乱码污染，`validate_light_novel.py passed:true` 一次过——证明只要"写前预设好对白格式 + 单条自检"双防，零计数陷阱可以代际终结而非每次重蹈。

## heredoc 残留检测（2026-07-08 第四次单批项目补充）

第四次单批项目（《DemoProjectM》）暴露一个 `validate_light_novel.py` 检测不到的污染源：用 shell heredoc（`python3 << 'PYEOF'` + `r"""…"""`）写中文正文时，文件会残留 `]=''/''`、`isVisible`、`jar勤`、`Visibility(true)`、`yesterday,.` 等碎片，整章不可用。详见 `light-novel-heredoc-pitfall-2026-07-08.md`。

**预防**：全部正文逐章用 `write_file` 写入，禁用任何形式 shell heredoc；写入后用同款正则扫描确认 `residue == 0`：

```python
import re
residue = re.findall(r"\]='''|\\\\''|isVisible|jar勤|Visibility\(true\)|yesterday,\.", t)
```

若 `residue > 0`，丢弃重写，**不要**逐句 patch——损坏范围太大。

## 字数统计口径差异（同次补充）

自检常用 `sum(1 for c in text if '\u4e00' <= c <= '\u9fff')` 只数中文字符，但 `validate_light_novel.py` 用 `len(re.sub(r'\s+', '', text))` 数所有非空白字符。两者差距约 15-25%。

| 口径 | 第一章 | 第二章 | 第三章 |
|------|--------|--------|--------|
| 中文字符（`\u4e00-\u9fff`，《DemoProjectK》） | 2633 | 2869 | 2933 |
| 中文字符（`\u4e00-\u9fff`，《赛博2047》） | 2678 | 2360→2844(patch后) | 3610 |
| 非空白字符（脚本口径，《赛博2047》） | ~3306 | ~2886→3440(patch后) | ~4517 |

结论：如果用户要求"≥2500字"，用中文字符口径是最保守的；用脚本口径则 ≥3000 才稳定。报告字数时必须注明口径。

## 段级补足循环（2026-07-08 第二次单批项目：《DemoProjectC》验证）

第二次单批项目（《DemoProjectC》，2026-07-08 下午）暴露一个高频后处理模式：章节一次性写完，自检发现 `len(''.join(t.split()))` 离 2500 阈值差 30-250 字（本次三章初稿分别为 2458 / 2423 / 2277）。这是常态，不是异常——LLM单稿自然落点往往在 2400 上下。

**正确补足流程**（每个补丁再跑一次自检；本流程重复三次都成功，未触发一次重写）：

1. 对短差章节用 `patch` 模式（不是 `edit`/重写），定位一段**已有的中间对白或心理描写**做向内增补。两种安全位置：
   - **对白前的心理/环境铺垫**：在「角色台词。」——角色名 前面插一段 80-180 字的心理/感官描写，仍属于原 beat。
   - **对白后的余韵**：在某个情绪转折段后追加一段 80-180 字的动作/环境余韵。
2. `patch` 的 `old_string` 必须取**唯一的多行块**（含对白行），避免误替换；`new_string` = `旧块 + \n\n + 新段`，新段保持原章语气风格不变。
3. 补后立即再跑一次自检命令，三项达标再进下一步。
4. 全部章节自检通过后再跑 `validate_light_novel.py` 作为权威收尾。

**禁止做法**（实测会埋雷）：

- ❌ 在 `## 章末钩子` 后追加水段——`章末钩子`必须是正文最后一块，后面加段会让钩子失效。
- ❌ 在多个章节叠加高相似度段落（例如同一句"窗外的风吹过梧桐"复用）——`validate_light_novel.py` 的 `adjacent_similarity` 检查（默认阈值 0.82）会触发 `adjacent chapters too similar`。
- ❌ 把补足段写成元描述（"接下来发生的事……"）——`repetition_stats` 会把含大量相似虚词的段落判为 `near_duplicate` (>0.88)。
- ❌ 整章重写——成本高且容易丢失伏笔/对白编号，patch 段级增补的成本仅 ~1 个工具调用。

**最小化补足模板**（patch `new_string` 例）：

```text
<原段落最后一句>。

<新段子——80-180字，承接上一句的人物动作或环境细节，不引入新人物，不复用其他章节句式>。

「对白。」——角色名
```

三次实测落地值：2458→2706、2423→2545、2277→2609，均为单次 patch，无重试，则 `validate_light_novel.py` 一次过。

## 角色名漂移陷阱（2026-07-08 第七次单批项目补充，《AI女友已下线》验证）

多章一次生成时，`characters.md` 里写定的角色名会在正文章节里**漂移成视觉相似但不同的字**——这是 `validate_light_novel.py`、旧 `verify_light_novel_delivery.py`、`scan_garbled()` **都检测不到**的污染类型，只有人工 `grep` 才能发现。

**本次实测**：`characters.md` 写定主角 AI 女友名"沈檬"，但三章正文先后出现"沈柠"和"沈冬青"两种漂移变体——"檬/柠"是同音近形字漂移（LLM 在长上下文里把不常用的"檬"替换成更常见的"柠"），"沈冬青"则是 LLM 在 ch3 写到"沈檬的离线缓存"时把缓存名当成了角色全名展开。两种漂移都不影响字数/对白/插图统计，但读者读到时会立刻出戏。

**根因**：LLM 在多章生成中，对专有名词的"记忆"靠的是注意力而非硬约束。当 `characters.md` 里的名字包含不常用字（檬/淼/珩/谌/隼）或形近字（柠/檬、清/青、舟/丹）时，后续章节会不自觉地替换成更"顺眼"的变体。名字越长、越不常见，漂移概率越高。

**防御措施（按优先级）**：

1. **写完每章后立即跑 `verify_light_novel_delivery.py`（已在 2026-07-08 更新加入 `--check-role-drift`）**。它会从 `characters.md` 的 `## Name` 头提取规范化角色名，然后扫描每章 `「...」——<name>` 归属行里是否有同名一字之差的变体。本次 ch2 的"沈柠"、ch3 的"沈冬青"都会被这条检查命中。
2. **修复用 `replace_all=true` 的 `patch`**，不要逐条改——漂移往往是全章性的，逐条 patch 容易漏。本次三章的"沈柠"→"沈檬"、"沈冬青"→"沈檬"各一次 `replace_all` 即可全清。
3. **预防**：在 `characters.md` 写定名字后，写第一章前先把每个角色名在心里过一遍——如果名字含不常用字或形近字，在后续章节的 prompt 里（如果是分批生成）显式重申"角色名 = 沈檬，不要写成沈柠/沈盟/沈蒙"。一次生成多章时这条预防无法在 prompt 层面做，只能靠 `verify_light_novel_delivery.py` 在交付前抓。
4. **名字漂移 ≠ 乱码**：不要把它归入 `scan_garbled()` 的"英文混入"或"乱码碎片"——它是纯中文的一字之差，乱码扫描的字符类正则不会命中。它需要的是"对照 characters.md 角色名表"的语义级检查，这正是 `--check-role-drift` 做的事。

**与既有检查的关系**：`--check-role-drift` 只检查 `「」——<name>` 归属行里的名字，不检查正文叙述中提到的角色名（如"沈檬说"）。叙述中的漂移仍需人工 grep。但归属行是读者最敏感的位置，先堵住这里能抓到 80% 的漂移。

## 投递级验证脚本（2026-07-08 第二次单批项目补充，2026-07-08 第七次更新）

`scripts/verify_light_novel_delivery.py` 在 `validate_light_novel.py`（只验章节）之上补三块：①元数据文件（`characters.md` 角色数、`foreshadowing.md` 未回收条数、`summary.md` 关键字段命中）；②heredoc 残留扫描 + 严格对白正则 + 漫画字段污染一次性全扫；③**新增（2026-07-08）**：ASCII-in-CJK 扫描（抓"队47人"这类阿拉伯数字混入中文叙述、"ProjectCode: jixia"这类英文标识符混入中文）+ 角色名漂移检测（见上节）。默认阈值（来自《DemoProjectK》实测基线）：`--min-chars 2500`（纯 CJK 口径）、`--min-roles 4`、`--min-threads 3`、`--min-dialogues 8`、`--min-illust 3`、`--check-role-drift yes`。跑在标准 `validate_light_novel.py` 之后作为"投递前最后一道闸"，或在汇报项目完成前自己先跑一遍。

```bash
python3 scripts/validate_light_novel.py projects/<书名>
python3 scripts/verify_light_novel_delivery.py projects/<书名>
```

**2026-07-08 第七次单批项目教训（重要）**：本次《AI女友已下线》生成时，作者**没有跑 `verify_light_novel_delivery.py`**，而是手写了一个临时自检脚本。后果：自检脚本虽然抓到了字数不足和 ASCII 污染，但**完全漏掉了角色名漂移**——因为自检脚本不知道 `characters.md` 里的规范名是什么，只做了"字符类正则扫描"。直到最后做章节间一致性 grep 时才偶然发现"沈柠""沈冬青"。**教训**：投递级验证不要手写临时脚本，直接跑 `verify_light_novel_delivery.py`——它的角色名漂移检查需要读取 `characters.md` 提取规范名，这是手写自检最容易漏的环节。如果 `verify_light_novel_delivery.py` 的检查项不满足当前项目需求，**扩展它**（往里加 case），而不是另起炉灶——否则每次手写都会重新踩一遍"我没想到要检查 X"的坑。

## 验收清单（单批项目专属）

- [ ] `config.json` 包含 `content_mode=light_novel`、`category`、`test_project`、`planned_chapters`
- [ ] `characters.md` 角色档案涵盖至少 3 人，包含说话风格/欲望/恐惧/秘密/首次登场章
- [ ] `summary.md` 含一句话卖点、主副类型、目标读者、基调、世界设定、主线目标、情感线、章节摘要
- [ ] `foreshadowing.md` 区分未回收/已回收两组，每条含埋下章节
- [ ] 每章 `light_novel/ln*.md`：字数 ≥2500（无空白统计）、`## 章末钩子`存在、`<!-- ILLUST_-->` ≥3 个
- [ ] 正文文件不存在任何漫画技术字段
- [ ] 正文无 heredoc 残留（`residue == 0`，详见 `light-novel-heredoc-pitfall-2026-07-08.md`）
- [ ] 正文无 ASCII-in-CJK 污染（`ascii_in_cjk == 0`，`verify_light_novel_delivery.py` 检查）
- [ ] 正文无角色名漂移（`role_drifts == 0`，`verify_light_novel_delivery.py --check-role-drift` 检查）
- [ ] 章节间衔接：第 N 章末钩子在 N+1 章前段承接或显式转场（参考模式六节 5 「章节 beat 表」）；推荐用**章纲 beat 块先于正文**技术稳定做到（见上方专节）
- [ ] **跑过 `verify_light_novel_delivery.py` 且全部通过**（不要用手写自检脚本替代——它会漏掉角色名漂移等需要跨文件比对的检查）

## 投递级验证脚本（2026-07-08 第二次单批项目补充）

`scripts/verify_light_novel_delivery.py` 在 `validate_light_novel.py`（只验章节）之上补两块：①元数据文件（`characters.md` 角色数、`foreshadowing.md` 未回收条数、`summary.md` 关键字段命中）；②heredoc 残留扫描 + 严格对白正则 + 漫画字段污染一次性 ROI 全扫。默认阈值（来自《DemoProjectK》实测基线）：`--min-chars 2500`（纯 CJK 口径）、`--min-roles 4`、`--min-threads 3`、`--min-dialogues 8`、`--min-illust 3`。跑在标准 `validate_light_novel.py` 之后作为"投递前最后一道闸"，或在汇报项目完成前自己先跑一遍。

```bash
python3 scripts/validate_light_novel.py projects/<书名>
python3 scripts/verify_light_novel_delivery.py projects/<书名>
```

## 优先用 bundled 验证脚本，不要手写扫描器（2026-07-09 补丁，强制工作流）

第七次单批项目（《校广播站的午夜频率》）即便已有上面"投递级验证脚本"段落，仍因 agent 在模式六 note 8 长段验证文字里**没注意到** `verify_light_novel_delivery.py` 已存在，改用 `write_file` 在 `/tmp/scan_ln.py` 手写了一份等价扫描器，浪费 1 个工具调用，且手写版本因少一个查表分支而漏掉了一个新污染类别。

**强制工作流修正**：
1. 任何"前 N 章 + 设定"轻小说单批项目在跑验证前，**先列 `scripts/` 下与 light_novel 有关的所有脚本**（`ls scripts/ | grep -iE 'scan|verif|garble|light_novel'`），确认是否已有 bundled 投递脚本可直接调用。
2. **优先调用 `scripts/verify_light_novel_delivery.py <项目目录>`**——它一次性覆盖 validate + heredoc + 对白格式 + 漫画字段 + heredoc 残留 + 多数乱码模式。只有当它漏掉某个具体污染类别（如本会话的 ASCII `--` 代 `——`、单字母 ASCII、`|tag` 段尾标记），才在手写 `/tmp/scan_ln.py` 脚本里**仅补漏的那个类别**，跑完即丢。
3. **禁止**：在同一次会话里，对同一个项目目录手写一份"覆盖所有类别"的扫描脚本——这是对 bundled 脚本的无谓重复，且每次手写都漏不同子类，没有任何复用沉淀。

## `python3 -c` 内联脚本中 CJK 全角括号与 Python 半角括号混淆（2026-07-09 补丁）

第七次单批项目验证时命中一个 Python-via-shell 的低频但难诊断的陷阱：用 `terminal` 工具跑 `python3 -c "...含 CJK 的 inline 代码..."` 时，若 inline 代码里同时出现 Python 列表字面量 `[...]` 与紧跟其后的中文右括号 `）`（例如注释或在打印字符串里），Python 解析器有时会因为 CJK 段与 ASCII 段的字符宽度判别差异报 `SyntaxError: closing parenthesis ')' does not match opening parenthesis '['`。实际报错是 shell 把 CJK 全角字符误展开/截断到引号边界之外。

**修复**：避免用 `python3 -c` 跑任何**含全角括号 + 中文字符串 + 正则字面量**混合的 inline 脚本。改为：
1. 用 `write_file` 工具把整段验证代码写到 `/tmp/scan_<something>.py`，再 `python3 /tmp/scan_<something>.py <文件路径参数>`。
2. 写文件时 рецепты 用三引号字符串避免转义；正文 regex 字面量用 `r"..."` raw 字符串。

这条陷阱此前未在 skill 中记录，因为它跟 SKILL.md note 7「禁用 Shell heredoc 写中文正文」是**不同维度**的问题——那是写入路径损坏文件内容，这是运行时 Python 解析失败无输出。两者都属于"避免在 shell 层混入 CJK"的总主题，但触发条件和修复方法不同。

**导入后必须验证**：跑 heredoc 残留扫描（`re.findall(r"\]='''|\\\\''|isVisible|jar勤", t)`）+ 标准四项（中文字符 ≥2500、`<!-- ILLUST_\d+ -->` ≥3、`## 章末钩子` 存在、无 `**格子**`/`### Panel` 等漫画字段污染）+ 对白格式 `「.*?」——[^\n]+` ≥8 条。残留 >0 即丢弃重写，不要逐句修。详见 `references/light-novel-heredoc-pitfall-2026-07-08.md`。
