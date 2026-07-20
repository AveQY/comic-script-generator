# Novel Generation + Bookshelf Reader Lessons (2026-07-07)

## Context
During a comic-script-generator session, the user concluded that dialogue-heavy daily-life stories worked better as novels than as fully rendered comics. The workflow evolved from Page/Panel manga generation into an independent light-novel / web-novel pipeline with a Tomato-Novel-style Reader homepage.

## Durable lessons

### 1. Novel route must be independent, not only a conversion step
Mode 6 should support two branches:
- **Native novel generation**: title/category → full-book setup → characters → chapter beats → chapter prose → key-scene illustration manifest → validation → Reader shelf.
- **Compatibility conversion**: existing Page/Panel episodes → `export_light_novel.py` → light novel text + key scene manifest.

Do not treat native novel generation as “write a short placeholder and call it done.” For batch novel requests, each book must have reader-facing substance.

### 2. Required native novel project structure
Each novel project should include:
```text
projects/<book-title>/
├── config.json              # content_mode=light_novel, script_unit=light_novel, density_mode=LN, category=<channel>
├── summary.md               # premise, audience, tone, chapter list, chapter beats
├── characters.md            # age, identity, speech style, contradiction, desire/fear/secret
├── foreshadowing.md         # unresolved/resolved plot hooks
├── style_guide.md           # key illustration style
├── light_novel/ln001_<chapter>.md ...
└── render_input/key_scenes001_<chapter>.json ...
```

### 3. Native chapter format
Use mobile-readable prose, not manga technical fields:
```markdown
# 第X章：章名

---

正文段落。每段 80-180 字左右，移动端阅读友好。

「角色台词。」——角色名

角色动作、表情、心理变化。

<!-- ILLUST_1 -->

## 章末钩子
一句强钩子或一个未解决动作。
```

Forbidden in native novel chapters:
- `**格子**`
- `**构图**`
- `**转场**`
- `### Panel`
- `## Page`
- table format `| 字段 | 内容 |`
- raw empty markers like `> 无`

### 4. Validation thresholds
Use `scripts/validate_light_novel.py` for novel projects.
Recommended thresholds:
- Short test: 2500-4000 Chinese chars/chapter, at least 8 dialogue lines, at least 3 illustration markers.
- Formal project: 4000-8000 Chinese chars/chapter, 6-12 chapters minimum.

The session’s first 10-book batch produced ~900-char chapters; that is acceptable only as a prototype, not as final “generated novels.” Future batches should use the new thresholds.

### 5. Reader UX preference
The user rejected a single project-detail-first interface. Reader should open to a **homepage** first:
1. Home / banner
2. Category channels
3. Bookshelf with book cards
4. Click book → chapter list / reading view

The Reader should resemble Tomato Novel style:
- light theme
- tomato-red gradient accents
- book shelf cards
- categories such as 日常 / 恋爱 / 治愈 / 搞笑 / 漫画
- serif-style warm reading page, beige paper background
- font-size controls, progress bar, prev/next chapter navigation

### 6. Reader/API implementation notes
- `/projects` should count `light_novel/ln*.md` as episodes/chapters when no `episodes/` directory exists.
- Novel `config.json` must include `content_mode: light_novel` and `category`, or homepage classification will be weak.
- `/light-novels?project=<name>` lists `light_novel/ln*.md` and returns `file`, `title`, `chars`, `url`.
- When modifying the single-file Reader, always extract the `<script>` block and run a JS syntax check (`node --check`) before declaring success. A single stray `}` caused an infinite “loading” page.
- Preserve properly URL-encoded Chinese project/file paths. Raw unencoded Chinese in `/file?project=...&path=...` can produce HTTP 400 under Python’s basic HTTP server.

### 7. Batch generation channels used as examples
Useful channel spread for “10 different novel topics”:
- 都市日常
- 赛博悬疑
- 古风奇幻
- 校园恋爱
- 职场喜剧
- 美食治愈
- 末日公路
- 星际冒险
- 民俗怪谈
- 轻推理
