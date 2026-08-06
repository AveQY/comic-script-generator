---
name: csg-mode6-light-novel
description: >-
  独立的轻小说/网文生产线：番茄小说风格正文 + 每章关键插图 + 角色档案 + 伏笔追踪 + 长篇上下文压缩。
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, terminal
---

## 模式六：轻小说 / 网文生成 + 关键场景插图（独立小说路线）

**触发条件**：用户要求“生成小说”“写轻小说”“走小说路线”“批量生成小说题材”，或故事类型明显是对话/情感/日常驱动，不适合逐格漫画渲染。

**核心定位**：模式六不是“漫画稿的附属导出”，而是一条与 Page/Panel 漫画线并列的完整生产线。它保留漫画 skill 的项目管理、角色档案、伏笔追踪、关键插图、Reader 展示，但正文单位从 `Page → Panel` 改为 `卷/章 → 段落/对白/心理/钩子`。

### 生成前路线选择（强制）

当用户只说“生成故事/稿子/项目”但没有指定漫画或小说时，先给出选择：

```text
请选择生成路线：
1. 🖼 漫画分镜路线：Page/Panel 脚本 + 逐格渲染/漫画页
2. 📖 小说路线：番茄小说风正文 + 每章关键插图（推荐日常/恋爱/治愈/职场/轻推理）
```

用户明确说“小说”“轻小说”“番茄”“书架”“阅读正文”时，直接进入模式六，不再询问漫画分镜密度 A/B/C。

### 小说题材/频道分类

**初始化陷阱（2026-07-20 实测）**：`init_project.py --mode LN` 会报错——`--mode` 只接受 A/B/C，LN 是 `config.json` 里的 `density_mode` 值而非 CLI 参数。小说项目**不走 init_project.py**，直接用 Python 建目录骨架：

```python
from pathlib import Path
import json
pdir = Path(projects_root) / book_name
(pdir / "light_novel").mkdir(parents=True, exist_ok=True)
(pdir / "long_novel_context").mkdir(exist_ok=True)
(pdir / "render_input").mkdir(exist_ok=True)
# 再写 config.json（content_mode/script_unit/density_mode/category/target_total_chars/planned_chapters）
```

**大纲风格维度确认（2026-07-20 实测，强制前置）**：用户热点选题后要完整大纲时，**先确认 5 个风格维度再动笔**——类型强度、爽文色彩、智斗密度、结局基调、多线融合。《替考AI》未做前置确认，用户连续 5 轮追加（悬疑→爽文→三线融合→开放结局→智斗），每轮重写整份卷纲。五维度模板+爽文元素库+智斗层级设计+多线融合技法+开放式结局模式见 `references/novel-outline-style-dimensions.md`。用户说「就按这个大纲完整写完」才是开工信号，此前只维护大纲文档。**补充（2026-07-21）**：该参考文档是《替考AI》项目的已确认决策源（目标 32 章 × 13 万字、教育悬疑、三线融合、开放结局）——大纲会话中断后，正文生成必须从该文档读取规划，不要在正文章节里另立章节数/字数目标。

生成小说项目时必须写入 `config.json`：

```json
{
  "content_mode": "light_novel",
  "script_unit": "light_novel",
  "density_mode": "LN",
  "category": "都市日常 / 校园恋爱 / 古风奇幻 / 赛博悬疑 / 职场喜剧 / 美食治愈 / 末日公路 / 星际冒险 / 民俗怪谈 / 轻推理"
}
```

Reader 首页书架会读取 `category` 和 `content_mode` 做分类展示。

### 小说项目结构

```text
projects/<小说名>/
├── config.json
├── summary.md              # 全书设定 + 每章摘要/钩子
├── characters.md           # 角色档案
├── foreshadowing.md        # 伏笔追踪
├── style_guide.md          # 插图风格
├── light_novel/
│   ├── ln001_<章名>.md
│   ├── ln002_<章名>.md
│   └── ...
├── long_novel_context/       # 长篇续写压缩上下文，禁止每次加载全文
│   ├── chapter_index.json    # 每章字数/摘要/钩子/出场角色
│   ├── running_summary.md    # 全书滚动摘要
│   ├── recent_continuity.md  # 最近5章连续性
│   ├── character_state.md    # 角色状态/关系/口癖
│   └── open_threads.md       # 未回收伏笔/章末钩子
└── render_input/
    ├── key_scenes001_<章名>.json
    └── ...
```

**变体：平铺结构**——章节文件也可直接放在项目根目录，使用`第一章_入场券.md`命名，对白格式使用`角色名「台词」`前缀模式。详见`references/light-novel-flat-structure.md`。

**根级文件一致性维护（重要）**：当项目已通过 `init_project.py` 初始化（根级存在 `characters.md`/`foreshadowing.md`/`summary.md` 占位文件，内容如"（待生成）"），前 N 章+设定交付时必须**同步更新根级文件**，不得只在 `light_novel/` 下创建综合文件而保留根级占位。三种正确做法按优先级：
  - **推荐**：直接更新根级 `characters.md`、`summary.md`、`foreshadowing.md`，不在 `light_novel/` 下另建 `chars.md` 等综合副本，保持 Reader/脚本读取路径一致。
  - **次选**：若在 `light_novel/chars.md` 中写综合内容（全书设定+角色+伏笔合并在一个文件），则必须同步更新根级文件：`characters.md` 改为一行引用 `> 完整角色档案见 light_novel/chars.md`，`foreshadowing.md` 同理，确保只读根级文件的流程不拿到"（待生成）"。
  - **不推荐**：根级留空占位 + 仅在 `light_novel/chars.md` 放内容——这会形成隐藏陷阱：Reader 展示靠根级文件判断，看到的是"待生成"；后续续写 agent 先读根级文件，以为角色/伏笔未建立可能重写覆盖。交付后必须验证根级文件内容不再是占位文本。

### 小说生成流程

1. **确定书名和频道**
   - 项目名就是书名，尽量使用面向读者的标题，而不是技术目录名。
   - 频道必须明确，例如“都市日常”“校园恋爱”“轻推理”。

2. **先写全书设定**
   写入 `summary.md`，包含：
   - 一句话卖点
   - 主类型/副类型
   - 目标读者
   - 故事基调（甜/暖/悬疑/爆笑/治愈/爽感）
   - 主线目标
   - 情感线或关系变化
   - 章节目录（长篇目标默认至少 40-60 章，总字数不少于 20 万；短测项目必须显式标注“短测”）

3. **角色档案**
   写入 `characters.md`，每个主要角色包含：
   - 年龄/身份/外貌
   - 性格矛盾点
   - 说话风格
   - 欲望/恐惧/秘密
   - 与主角关系
   - 首次登场章

4. **章节 beat 表（强制）**
   每章正文前必须先规划 beat：
   ```markdown
   ## 第X章：章名
   - **开场钩子**：一句话抓人
   - **日常/场景建立**：地点、时间、氛围
   - **触发事件**：打破日常的小事件
   - **互动推进**：至少 2 次角色互动/对话反转
   - **情绪转折**：误会、心动、发现、危机或温暖点
   - **章末钩子**：让读者想点下一章
   - **关键插图**：3-7 个插图点
   ```

5. **正文写作格式**
   轻小说正文必须写到 `light_novel/lnXXX_<章名>.md`：
   ```markdown
   # 第X章：章名

   ---

   正文段落。每段 80-180 字左右，移动端阅读友好。

   「角色台词。」——角色名

   角色的动作、表情、心理变化。

   <!-- ILLUST_1 -->

   > 少量旁白/章节情绪句（可选）

   ---

   ## 章末钩子
   <一句强钩子或一个未解决动作>
   ```

   **禁止**在小说正文中出现漫画技术字段：`**格子**`、`**构图**`、`**转场**`、`### Panel`、`## Page`、表格 `| 字段 | 内容 |`。用户明确说"禁止漫画格式"时，写入正文前先在脑海中过一遍字段隔离清单（见 `references/light-novel-single-batch-generation.md`）。注意：此限制只针对 `light_novel/ln*.md` 正文文件；`characters.md`/`summary.md`/`foreshadowing.md` 等元数据文件可自由使用表格和结构化字段。

   **对白格式陷阱（重要）**：`validate_light_novel.py` 用正则 `^「.+?」——.+$` 统计对白数量，要求 `——角色名` 紧跟在 `「」` 之后且在同一行。如果使用叙述式归因（如 `「台词。」他说。` 或 `「台词」\n他问。`），验证脚本将不计入对白数量，导致 `too few dialogues` 误报。**强制规则**：所有需要被脚本统计的对白必须写成 `「台词」——角色名` 同行格式。叙述式归因可以存在于正文中但不能替代 `——` 格式，否则对白数可能不足 8 轮而验证失败。
   - **写作时最常犯的错误（2026-07-08 实测）**：LLM 初稿常常全部使用叙述式归因（`「闭嘴。」陆沉打断了它。`），导致后续需要对每章数处对白逐条 `patch` 补改为 `「闭嘴。」——陆沉\n\n陆沉打断了它。` 才能通过验证。**预防方法**：在写正文时，每写一段对白就立即决定该句是否需要 `——角色名` 归属格式（每章至少 3-8 处）；对于独立的短对白、角色名独占行尾的台词、不接叙述的对话，优先使用 `「台词。」——角色名` 独占一行或段首的格式。不要等全章写完再批量补改——补改时需要把叙述句从对白行拆出、重新分段，极易引入重复或错位文本。
   - **章末零计数自检（2026-07-09 实测）**：写完每章立即跑 `n_fmt = len(re.findall(r'^「.+?」——.+$', t, re.M))` 与 `n_open = t.count('「')` 对比——若 `n_fmt == 0`（或远低于 `n_open`），说明全章叙述式归因，验证脚本同款正则一条也匹配不上，对白数直接归零。**修复方式不是逐条 patch，而是整章 `write_file` 一次覆写**（一次调用改完全章，比逐条拆行重排省时且更不易错位）。注意：本节"禁止整章重写"仅适用于**字数不足时的段级 patch 增补**——对白格式整体缺位时整章重写才是正解。详见 `references/light-novel-single-batch-generation.md` §章末自检：零计数陷阱与整章重写辨析。
   - **角色名漂移陷阱（2026-07-08 实测，强制）**：多章一次生成时，`characters.md` 里写定的角色名会在正文章节里**漂移成视觉相似但不同的字**（如同音近形字 柠/檬、清/青，或把名字误展开成全名）。这是 `validate_light_novel.py`、`scan_garbled()` 都检测不到的污染类型，只有跨文件比对才能发现。**强制做法**：交付前跑 `scripts/verify_light_novel_delivery.py`（含 `--check-role-drift yes`，默认开），它会从 `characters.md` 提取规范化角色名并扫描每章 `「...」——<name>` 归属行里的一字之差变体。发现漂移用 `patch` `replace_all=true` 一次修复全章，不要逐条改。详见 `references/light-novel-single-batch-generation.md` §角色名漂移陷阱。

6. **篇幅规则（长篇小说强制）**
   - 正式小说目标：**不少于 20 万中文字符**。
   - 默认结构：40-60 章，每章 4000-6000 字；也可 80-100 章，每章 2500-3500 字。
   - 短测项目允许每章 2500-4000 字、3章起，但必须在项目名或 `config.json` 标注 `test_project: true`，不得当作正式小说交付。
   - 对话密集章节：对话不少于 8 轮；每章至少 1 个心理/情绪转折。
   - 每章至少 3 个 `<!-- ILLUST_N -->` 插图标记；推荐 4-7 个。
   - 用户说“生成一篇小说/完整小说”时，默认按 20 万字长篇规划，不要只生成 3 章样稿。

7. **关键插图清单**
   每章生成 `render_input/key_scenesXXX_<章名>.json`：
   ```json
   {
     "episode": "ln001_章名",
     "category": "都市日常",
     "key_scenes": [
       {
         "index": 1,
         "scene": "具体画面描述",
         "prompt": "固定风格 + 具体画面 + no text/no letters"
       }
     ]
   }
   ```
   插图只画关键情绪/场景，不承担叙事完整性。正文必须独立可读。

8. **验证与维护**
   - 写完每章后运行：
     ```bash
     python scripts/validate_light_novel.py projects/<小说名>
     ```
   - 检查项：H1标题、字数、对白数、插图标记、是否混入漫画字段。
   - **跨章钩子承接校验（重要，漫画线 note 10 的轻小说等价）**：漫画模式强制"N集末钩子被N+1集前1-3个Panel承接"，轻小说同样需要——第N章的`## 章末钩子`应被第N+1章开头几段承接（人物、物件、悬念或情绪延续）。多章一批生成后，跑一次跨章承接脚本确认，避免上下文断裂：
     ```python
     import re
     for i in range(1, N):
         prev = open(f"light_novel/ln00{i}_*.md").read()
         curr = open(f"light_novel/ln00{i+1}_*.md").read()
         hook = re.search(r'## 章末钩子\s*\n(.+)', prev)
         opening = curr.split('---\n', 2)[-1][:200]
         # 检查hook中提到的角色/物件是否出现在opening中
     ```
     2026-07-08 实测《DemoProjectF》前3章：第1章末"陆行舟登门"→第2章开头"陆行舟进门"✓；第2章末"陆行舟离开+归墟引"→第3章来找信→章末脚步声回归✓。单批生成时可顺手合在同一次校验脚本里。
   - 更新 `summary.md`、`characters.md`、`foreshadowing.md`：新增伏笔要记录，回收伏笔要移动到已回收。
   - **根级文件一致性自检（强制）**：交付前必须验证根级 `characters.md`、`foreshadowing.md`、`summary.md` 不再包含占位文本。最常见的错误是：项目已通过 `init_project.py` 初始化（根级文件内容为"（待生成）"），但后续写稿时创建了 `chars.md` 或 `light_novel/chars.md` 等新文件，而忘记更新根级文件。运行以下检查：
     ```bash
     cd projects/<项目名>
     grep -l "待生成" characters.md foreshadowing.md summary.md 2>/dev/null || echo "OK 无占位残留"
     ```
     如果 grep 返回了文件名（即该文件仍含"待生成"），说明根级文件未被正确更新——此时必须直接写入根级文件，而不是再创建一个 `chars.md`。Reader 展示和后续续写 agent 都依赖根级文件路径，占位残留会导致它们读到空内容。
   - **2026-07-09 新增：`write_file` 工具自身的静默字符损坏（强制，区别于 heredoc）**：用 `write_file` 工具直接写轻小说章节正文（非 Shell heredoc 路径）也会出现静默字符损坏，且 `validate_light_novel.py` 报 PASS、`scan_garbled()` 现有五类正则不全覆盖、`scan_unicode_contamination.py` 不报错。本次《DemoProjectI》ln005–ln013 续写 9 章中 2 章首稿落入此陷阱，均靠写入当轮立即跑的自检 Python 命令即时捕获并 `patch` 修复。**根因不是 heredoc**——这是 `write_file` 工具调用传输层的偶发损坏，与 note 7/12 记录的 Shell heredoc 损坏是两类问题；heredoc 被禁不代表 `write_file` 可信。已实测的三种子类污染：
     - **(a) 内部伪标记泄漏 `_XXX_`**：ln007 出现 `生_ENC_之相`（应为「渐失之相」）。`_ENC_` 是下划线包裹的大写 token，比 garbled-ref §5a 的 `\|<lowercase>` 多了一对下划线包裹。追加正则 `re.findall(r'_[A-Z]{3,}_', t)` 检测。
     - **(b) 整词英文替换中文语素**：ln008 章末钩子出现 `他要Selectable他把`（应为「他要把」）。一个完整英文词（疑似 Selection 提示被模型转成 Selectable）被整词替换进中文句子中间，不是插入而是替换——最接近 garbled-ref §2 英文混入但属"替换"而非"插入"，且位于章末钩子段（污染最集中段之一）。现有 `[a-zA-Z]{3,}` 正则可捕获（删去 HTML 注释后跑）。
     - **(c) U+FFFD 替换字符损坏整字**：ln008 出现 `沈令�`（应为「沈令川」）。整字 token 在传输/编码层被换为 replacement char U+FFFD。正则扫不到，只能靠通读上下文、发现"这个角色名缺了一个字"时定位。用 `t.count('\ufffd')` 可机械检测 U+FFFD 的存在（但不会告诉你本来该是什么字）。
   - **强制写入后自检 SOP（写入当轮必跑，不只靠 validate）**：每次 `write_file` 写完一章正文后，必须在**当次**对话轮内跑一次 Python 自检命令（不是事后跑 `validate_light_novel.py`，那是第二道闸不是第一道）。自检要同时做七项（2026-07-08 实测五项漏报 Hiragana/Katakana/Latin-1 Supp/繁简混排/Python-标识符泄漏，2026-07-09《DemoProjectC》6 章续写实测补两验收）：
     ```python
     import re
     t = open('lnXXX_第X章.md', encoding='utf-8').read()
     cjk = sum(1 for c in t if '\u4e00' <= c <= '\u9fff')
     body = t.split('## 章末钩子')[0]; cjk_body = sum(1 for c in body if '\u4e00' <= c <= '\u9fff')
     fmt = len(re.findall(r'^「.+?」——.+$', t, re.M))          # 对白格式计数（严格 ——角色名 同行）
     illust = len(re.findall(r'<!--\s*ILLUST_\d+\s*-->', t))    # 插图标记（严格格式，不含 —描述）
     sep = len(re.findall(r'^---$', t, re.M))                   # --- 分隔符（## 章末钩子 之前必须为 1）
     cleaned = re.sub(r'<!--.*?-->', '', t)                     # 删 HTML 注释再扫英文
     en = [g for g in re.findall(r'[a-zA-Z]{3,}', cleaned)]     # 捕获 Selectable / Sync 整词
     pseudo = re.findall(r'_[A-Z]{3,}_', t)                     # _ENC_ 类下划线伪标记
     u_fffd = t.count('\ufffd')                                 # U+FFFD 替换字符
     cyr = re.findall(r'[\u0400-\u04ff]{2,}', t)                # Cyrillic 块越界（дневного 一类）
     cjk_en = re.findall(r'[\u4e00-\u9fff]{1,3}[a-zA-Z]{2,}[\u4e00-\u9fff]{1,3}', t)  # 汉字夹英文再接汉字（izando/FileSync/n异）
     manga = re.findall(r'\*\*格子\*\*|\*\*构图\*\*|\*\*转场\*\*|###\s*Panel|##\s+Page|^\|.*\|.*\|', t, re.M)
     print(f'CJK={cjk}/body={cjk_body} 对白={fmt} 插图={illust} 分隔={sep}\n英文={en[:6]} _X_={pseudo} U+FFFD={u_fffd} Cyr={cyr} 汉夹英={cjk_en[:6]} 漫画={manga}')
     ```
     **期望值**（每章）：`cjk_body ≥2500`、`对白 ≥8`（严格 `——角色名` 同行）、`插图 ≥3`（严格 `<!-- ILLUST_N -->` 无描述）、`分隔 = 1`、`_X_/U+FFFD/Cyr/漫画/汉夹英` 全为空/`[]`，`英文` 仅含故事中出现的技术专名（`QEMA`/`Echo`/`Dr. Shadow`/`arXiv` 等可接受）。**`illust` 正则必须用严格格式 `<!--\s*ILLUST_\d+\s*-->`**——`t.count('<!-- ILLUST_')` 会误计含破折号描述的旧样式 `<!-- ILLUST_1 — … -->` 为通过，而 `validate_light_novel.py` 同款正则要求精确无描述，自检宽松即漏报。
     也推荐一站式扫描 `scripts/scan_cjk_prose_pollution.py`，覆盖上列后三项扩展块盲区（Hiragana/Katakana/Latin-1 Supp/Python-ident 泄漏/繁简混排），可与 `scan_unicode_contamination.py` 并行运行。2026-07-09《DemoProjectC》续写 ln004–ln006 共 3 章实测：当轮自检已捕获并 `patch` 修复 4 处乱码（`ríos` Latin-1 Supp í / `ちゃぁ` Hiragana / `.ObjectMeta` Python 泄漏 / `३` Devanagari）与 2 处繁简混排（`頭`）。**不跑这条自检，污染会一路留到下游 Reader/读者**。验字通过 ≠ 正文干净；`validate_light_novel.py` 报 PASS、`scan_unicode_contamination.py` 报 0、`scan_garbled()` 报 0 也都不代表无污染——三者全不覆盖 Hiragana/Katakana/Latin-1 Supp/繁简混排/对白前缀 Python 泄漏这五类。
   - **工具调用预算与模式选择（2026-07-09 实测，强制）**：批量续写前先评估章节总数——当 N≥6 章时，逐章 `write_file`（整章正文）+ 逐章五项自检 + 逐章 patch 修污染/补字数的总开销为 **3-7 次调用/章**（`write_file` 1 + `terminal` 自检 1 + `patch` 修污染 1-3 + `patch` 补字 0-1 + 重自检 0-1），9章即 27-63 次调用，会撞上会话工具调用上限。强制改为**模式三（单脚本全落盘）**——2 调用写全部文件，再批量 patch 修污染（patch 无需配套 write_file），总开销约 12 调用覆盖 9 章。详见 `references/light-novel-single-script-generation.md`「工具调用预算与模式选择」段，含单章开销明细表、模式选择规则表、预判检查清单。
   - **字数统计口径差异（重要）**：`validate_light_novel.py` 用 `len(re.sub(r'\s+', '', text))` 统计——这是**所有非空白字符**（含中文、标点、英文、Markdown 语法等），不是纯中文字符。
   - **body-only 口径（2026-07-08 补充）**：用户的"正文 ≥2500 字"指**章节正文本体**，不含 `## 章末钩子` 段、H1 标题、`---`、`<!-- ILLUST_N -->`、引用块等结构性脚手架。bundled `validate_light_novel.py` 却整文计数（含钩子），与 body-only 口径差几十到一两百个汉字。当字数卡在阈值附近、用 `validate_light_novel.py` "通过"却在 body-only 自检下"不过"时，以 body-only 为准——用 `references/light-novel-batch-generation.md` §3 的 `count_cjk(path, body_only=True)` 复核 `cjk_only`，确认无误即交付。安全做法：直接按"纯 CJK 汉字 ≥2600（body-only）"为目标写，比 bundled 脚本阈值留足裕量。
   - **批次生成钩子字数吞噬陷阱（2026-07-08 实测）**：单脚本批量生成多章时，`## 章末钩子` 段落往往写得较长（200-500 CJK 字符），导致 body-only 字数大幅缩水。本章实测三章的首稿 body CJK 分别为 2108/1816/3003——前两章均不达标，不得不后续用 `patch` 逐段补写。**预防建议**：在单脚本中写多章时，目标设为 body CJK ≥2800（即留出 300+ 字符缓冲给钩子段），而非贴着 2600 写。同时钩子段落应控制简练，关键悬念信息放在正文最后一段而非钩子段内；这样即使钩子写得长，正文字数也不会被连带吃掉。
   - **字数经常单稿落在 2400-2500 之间**——这是常态。先跑自检（详见 `references/light-novel-single-batch-generation.md` 的"单条 Python 自检命令"段），差 30-250 字时用 `patch` 做**段级增补**（在对白前补心理/环境铺垫，或在对白后补余韵，禁止在 `## 章末钩子` 后追加），补后再自检再跑 `validate_light_novel.py`。三次实测从 2458/2423/2277 增到 2706/2545/2609，单次 patch 全部一次过，无需整章重写。
   - **`patch` 工具增补中文正文的三重陷阱（重要，2026-07-08 实测）**：用 `patch` 对已写好的轻小说章节做字数增补时，必须遵守以下安全流程，否则会产生文件损坏而 `validate_light_novel.py` 不报错。三种已知失败模式：
     1. **隐式误替换**：LLM 在 `new_string` 中"重写"了而非"复制"了 `old_string`，导致相邻段被省略，文件中丢段却无报错。防御：构造 `new_string` 时先完整复制 `old_string` 原文，再在合适位置插入新段；`patch` 是 replace，不是 rewrite。
     2. **phantom 字符注入**：`patch` 的 `new_string` 中混入 `];`、`}`、`</...>` 等代码碎片（前一段在改 Python 脚本，下一段在改正文，LLM 未完全切换模式）。`validate_light_novel.py` 不检测这类污染。防御：每个 `patch` 后立即跑 phantom 扫描（`re.search(r'\];|\}\s*$|\\]=\'', text)`），见 `references/patch-intext-pitfall.md`。
     3. **连续 patch 状态脱节**：连续多个 patch 修同一个文件时，第二个 patch 基于的是 LLM 内存中的版本而非文件真实状态。防御：每个 `patch` 前若不确定，先 `read_file` 对齐当前内容；patch 后立即 `read_file` 验证相邻段未删除。
     完整安全 SOP 见 `references/patch-intext-pitfall.md`。简短流程：read → patch → read_validate → 自检字数 → phantom 扫描 → 漫画字段扫描 → validate_light_novel.py。
   - **跨语言乱码污染检查（强制）**：用 LLM 生成中文长篇正文时，输出中常混入英文碎片、蛇形命名标记、ASCII数字混用，以及 Cyrillic/Hebrew/扩展 Latin 等 Unicode 块越界字符等现象——对话标记后缀残留（`——陆远舟_joint`、`——苏晴_narrow her eyes_free-narrow`）、英文单词混入中文句子（`校园-olds安防服务器`）、乱码拼音/非自然语言碎片（`九年前-1同扫过全盘y天服`）、纯阿拉伯数字代替中文数字（`10年前他13岁`）、Cyrillic/Hebrew 段落混入（`ото外面走廊`、U+05BA 粘到 CJK 字符）、自插 HTML 工件（`<table end>`）、Latin 借词句中混入（`就call一张画面`）。这些不会被 `validate_light_novel.py` 的字数/对白/插图检查捕获，其中 Unicode 块越界类污染甚至**绕过** `scan_garbled()` 中的 ASCII 正则 `[a-zA-Z]{3,}`，但会严重损害可读性。写完每章后**必须**运行一次乱码扫描——推荐用 `scripts/scan_unicode_contamination.py`（覆盖 Unicode 块 + Latin 借词 + HTML 工件）作为投递前最后一道闸，再或并行运行 `references/light-novel-garbled-text-cleanup.md` 的 `scan_garbled()`（覆盖对话标记后缀/阿拉伯数字代中文）。检测到时用 Python `str.replace` 列表批量修复，修复后再重新验证字数。详细扫描脚本、修复列表模板和新发现的 Unicode 块越界类型见 `references/light-novel-garbled-text-cleanup.md`。

9. **长篇上下文压缩续写流程（避免上下文爆炸，强制）**
   - 长篇小说禁止每次续写加载所有 `light_novel/ln*.md` 全文。
   - 每完成 1-3 章，运行：
     ```bash
     python scripts/update_long_novel_context.py projects/<小说名>
     ```
   - 后续生成下一批章节时，只读取：
     1. `summary.md`（全书设定/卷纲）
     2. `characters.md`（角色档案）
     3. `foreshadowing.md`（正式伏笔表）
     4. `long_novel_context/running_summary.md`（滚动摘要）
     5. `long_novel_context/recent_continuity.md`（最近5章连续性）
     6. `long_novel_context/character_state.md`（角色状态）
     7. `long_novel_context/open_threads.md`（未回收钩子）
   - 只在修复具体章节时读取目标章节全文；不要为了续写读取全书。
   - 批次生成建议：每批 3-5 章；生成后立即压缩上下文，再进入下一批。
   - 每卷结束时，手动/自动整理 `volume_summary.md`：卷主线、已回收伏笔、未回收伏笔、角色关系变化。
   - **首次续写（long_novel_context/ 尚不存在）**：对于 ≤20 章且未生成 `long_novel_context/` 的项目，**必须读取全部已有章节正文（`light_novel/ln*.md`）+ 项目元数据文件（`characters.md`、`foreshadowing.md`、`summary.md`）** 后再规划续写章节。不要只读 summary.md 就开写——轻小说的多线剧情（角色关系、伏笔递进、情绪节奏）在元数据摘要中被严重压缩，只读摘要会丢失大量连续性信息。续写5章以上的批次时，推荐「通读全文 → 逐章规划 beat → 逐章/批量写入 → 批量验证」的模式。读完已有章节后，如果项目合成为一整体、无中断点，可以先写一个跨章 beat 表（每章1-2行核心事件+情感方向），再落笔正文，避免中途发现伏笔矛盾需整章重写。
   - **空壳项目陷阱（2026-07-21 实测，强制）**：用户说"续写/生成第 N-M 章"时，**先验证第 1 到 N-1 章在磁盘上真实存在**，不要信 `config.json` 的 `generation_status: in_progress` 或用户口中的章节编号。实测《替考AI》：config.json 写着 32 章规划、in_progress，用户要求"生成第 5-8 章"，但项目目录里只有 config.json——`light_novel/` 目录、根级元数据文件全缺，第 1-4 章从未落盘（早期会话在写完骨架后被切断）。验证三步：①`find <项目目录> -type f | sort` 看真实文件清单；②有元数据文件时 `grep -l "待生成" characters.md summary.md foreshadowing.md` 查占位残留；③`session_search` 查书名的历史生成记录，确认前序章节是否真的写过。确认空壳后：**先补齐前序基础（元数据 + 缺失章节正文），再写用户要的章节**，并在回复中明确告知"前 N-1 章磁盘上不存在，已重建"。禁止假装前章存在直接写第 N 章（角色、伏笔、章末钩子全部悬空），也禁止只补元数据就声称续写完成。本规则同样适用于漫画线的"续写第 N 集"（episodes/ 为空但 config 声称已生成）。另外注意：config.json 可能记录了用户在前序会话中口头确认过的频道/风格维度决策（如《替考AI》的 `category: 教育悬疑`），重建时保留这些已确认字段，不要回退到默认值。

10. **长篇验收**
   - 完成长篇后运行：
     ```bash
     python scripts/validate_long_novel.py projects/<小说名> --target-chars 200000 --min-chapters 40
     ```
   - 通过条件：总字数 ≥20万、章节数达标、单章字数达标、`long_novel_context/` 文件齐全。

11. **Reader 接入**
   - Reader 首页显示为书架，而非直接项目详情。
   - `/light-novels?project=<name>` 列出 `light_novel/ln*.md`。
   - 小说项目的 `config.json` 必须包含 `content_mode: light_novel` 和 `category`，否则首页分类可能不准确。

12. **正文写入路径（重要，与漫画稿同禁 heredoc）**
   - 轻小说每章正文（≥2500 中文字符、含 `<!-- ILLUST_N -->` 对白与章末钩子）同样**禁止用 Shell heredoc（`cat << EOF`、`python3 << PYEOF` + `r"""…"""`）写入**。2026-07-08 实测：用 `python3 << 'PYEOF'` + `r"""多段中文正文"""` 写 `ln003` 时，raw 三引号字符串与 shell heredoc 嵌套导致 Python 报 `SyntaxError: unterminated triple-quoted string literal`，即使不报错也会在文件中残留 `]='\''`、`isVisible`、`jar勤` 等损坏碎片，整章不可用。这与 note 7「禁止 Shell heredoc 写入漫画脚本」是同一类问题的小说路线等价——小说正文即便只有全角标点和 `「'勿忘我'」` 式单引号对白，heredoc 仍会损坏。
   - **首选**：用 `write_file` 工具单次写入整章（已验证 11.7KB 中文小说正文一次成功，无损坏无截断）。
   - **批量落盘（≤6 文件）**：把元数据 + 全部章节正文塞进同一个 Python 脚本，用 `write_file` 写脚本 + 一次 `terminal` 执行——2 个工具调用覆盖全部文件，末尾附内联验证段。2026-07-08 实测 50.8KB 脚本一次成功，3 元数据 + 3 章节共 6 文件全部落盘。详见 `references/light-novel-single-script-generation.md`。
   - **写入轮的专注性（2026-07-08 实测，强制）**：发 `write_file` 写章节正文的回复轮中，`tool call` 之前的助手文本应简短克制——**不要在 `write_file` 调用前夹带 200+ 字的章节规划散文**（「我得评估…」「他大概需要做一个这样的…」类）。长段规划散文后紧接 `write_file` 流式中文 `content` 会显著增加段落级肌理损坏概率（见 `references/write_file-paragraph-level-corruption.md` §预防 SOP 第 1 条）。规划段应在前一轮写完、或者充分沉默后再发 `write_file`。如果需要在当轮做规划与写入并存，规划段不超过 3-5 句，并且**最后一句必须是明确转向**（如「现在开始写第X章。」），让模型样本生成在情景切换时回到正文语态。
   - **降级**：把 `content = """…"""` 放在独立 `.py` 文件里（用 `write_file` 创建该脚本），再 `python3 gen_chapter.py` 执行——字符串从文件读入，绕开 heredoc 定界层；用普通 `"""…"""` 不要用 `r"""…"""`。
   - **写入后必须验证**：跑 heredoc 残留扫描（`re.findall(r"\]='''|\\\\''|isVisible|jar勤", t)`）+ 标准四项（中文字符 ≥2500、`<!-- ILLUST_\d+ -->` ≥3、`## 章末钩子` 存在、无 `**格子**`/`### Panel` 等漫画字段污染）+ 对白格式 `「.*?」——[^\n]+` ≥8 条。残留 >0 即丢弃重写，不要逐句修。详见 `references/light-novel-heredoc-pitfall.md`。

### 批量小说生成规则

当用户要求“一次生成 N 本小说/10 个题材不同的小说”：

1. 题材必须尽量分散：都市日常、赛博悬疑、古风奇幻、校园恋爱、职场喜剧、美食治愈、末日公路、星际冒险、民俗怪谈、轻推理等。
2. 每本书必须独立项目目录，书名面向读者。
3. 每本至少生成：`config.json`、`summary.md`、`characters.md`、`foreshadowing.md`、`style_guide.md`、`light_novel/ln001~`、`render_input/key_scenes*.json`、`long_novel_context/`。
4. 不要只生成占位简介；每章必须是可阅读正文。
5. 如果用户要求“正式小说/完整小说”，每本按 20 万字规划；如果一次生成多本，可先生成每本前 3-5 章作为第一批，但必须在 `config.json` 写入 `target_total_chars: 200000`、`planned_chapters` 和 `generation_status: in_progress`，不能汇报为已完成长篇。
6. 每批完成后运行 `update_long_novel_context.py`，下一批只读取压缩上下文续写。
7. 完成后必须验证 `/projects` 和 `/light-novels?project=` 能读到新书；正式长篇还要跑 `validate_long_novel.py`。

### 批量小说并发生产模式（delegate_task 驱动）

**适用场景**：用户要求一次生成 10+ 本小说，每本需要角色档案 + 全书设定 + 前 N 章正文。

**为什么不直接用 batch_generate.py**：该脚本仅支持漫画模式（A/B/C），不支持轻小说路线。轻小说批量需用 delegate_task 多 agent 并发驱动。

**执行流程**：

1. **准备题材清单**：预先定义 20 本书的 title/category/premise，确保题材分散，避免连续多本同类。

2. **初始化骨架**（一次工具调用）：
   ```python
   for t in topics:
       projects_root = os.environ.get('COMIC_PROJECTS_ROOT', os.path.expanduser('~/comic-projects/projects'))
       pdir = Path(projects_root) / t['title']
       pdir.mkdir(parents=True, exist_ok=True)
       (pdir / 'light_novel').mkdir(exist_ok=True)
       (pdir / 'long_novel_context').mkdir(exist_ok=True)
       # config.json with content_mode: light_novel + category
       # summary.md, characters.md, foreshadowing.md 占位
   ```

3. **并发 dispatch**（每批 3 本，受 max_concurrent_children=3 限制）：
   ```python
   delegate_task(tasks=[
     {"goal": "生成《书A》角色档案+全书设定+前3章", "role": "leaf"},
     {"goal": "生成《书B》角色档案+全书设定+前3章", "role": "leaf"},
     {"goal": "生成《书C》角色档案+全书设定+前3章", "role": "leaf"},
   ])
   ```
   每本子任务交付 6 文件（chars.md + summary.md + foreshadowing.md + light_novel/ln*.md×3）。

4. **失败恢复**：delegate_task 可能因 HTTP 522/超时中断（status=interrupted），表现为主进程收不到子任务结果。检测到中断后重新 dispatch 同一批即可——已写入的文件不会被覆盖。

5. **后处理规范化**：子任务生成的章节文件可能不在标准路径，或使用非标准命名（chapter_01.md、第1章.md 等）。用 Python 扫描每个项目目录，将章节文件复制/移入 light_novel/ 并重命名为 lnXXX_ 格式。

6. **API 验证**：不依赖 filesystem ls，而是通过 Reader API 验证：
   ```bash
   curl -s http://<reader>:8081/projects | python3 -c "check episodes>=3"
   curl -s 'http://<reader>:8081/light-novels?project=<书>' | python3 -c "check count>=3"
   ```

**注意事项**：
- 每本子任务用 write_file 或 Python 脚本写入，禁止 Shell heredoc。
- 子任务 context 必须包含完整设定 + 格式要求，否则 output 格式不统一。
- 每批 3 本并发，勿超出 max_concurrent_children（默认 3）。
- 20 本 × 3 章每章 ≥2500 字，总字数约 15-20 万字（骨架阶段）。
- 本模式只生产小说正文，不涉及图片/渲染输出。
- **⚠️ 大纲漂移红线（2026-07-21《替考AI》32 章实测）**：子代理只适合「素材已在、格式刚性」的转换型任务（小说→分镜）；**不适合「只有大纲、需原创」的正文创作**——3 个子代理带完整大纲 context 仍各自写出 3 个完全不同的故事（自创主角/自创设定/meta 回复冒充交付）。章节正文创作必须主会话直接 write_file 逐章写。决策树、验证三件套（防 meta 回复/防自创主角/防缺钩子）、主会话直写节奏见 `references/delegate-outline-drift.md`。

### 从漫画稿转小说（兼容分支）

如果项目已经有 Page/Panel 漫画稿，可以使用：

```bash
python scripts/export_light_novel.py episodes/epXXX_xxx.md --project-dir projects/<项目名> --illustrations 7
```

这个分支只用于“已有漫画稿转轻小说”，不应替代原生小说生成流程。
