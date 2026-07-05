---
name: comic-script-generator
description: 根据大纲或热点生成漫画分镜稿，支持项目管理、角色档案、伏笔追踪
version: 1.8.1
tags: [creative, comic, screenplay, storyboard]
---

# 漫画脚本生成器

为漫画、图片故事生成详细分镜脚本的工作流程。核心输出单位为 Page → Panel → 气泡/旁白/拟声/转场，而不是影视化 Scene。支持从用户大纲或热点话题生成内容，维护项目结构、角色档案、风格指南和伏笔追踪。同时提供在线接口，允许外部系统远程调用生成脚本。

## 使用场景

- 用户提供故事大纲，生成详细分镜脚本
- 抓取热点话题，生成相关创意内容
- 管理长篇连载项目，追踪角色和伏笔

## 更新地址

源仓库：https://github.com/YOUR_GITHUB_USERNAME/comic-script-generator

## 更新检查（每次使用前）

**每次启动该 skill 前，必须先检查是否有更新：**

1. 运行 `python scripts/check_update.py`
2. 脚本会自动：
   - 检测 GitHub 网络连通性
   - 比对本地与远程 `origin/main` 的 commit SHA
   - 输出 JSON 结果（`network_available`、`update_available`、`action`）
3. 如果网络不通或无法获取 commit，脚本返回 `action: "skip"`，继续正常使用当前 skill
4. 如果 `action: "update_needed"`，先执行 `git pull origin main` 更新 skill，再继续使用

**注意：** 只有这个 skill 目录下包含完整的 git 历史，`check_update.py` 依赖 git 命令正常工作。

## 初始化流程

**首次使用必须初始化：**

1. 询问用户项目保存位置（默认：`~/comic-projects/`）
2. 询问稿子源：
   - [1] 本地文件（从用户电脑选择脚本文件）
   - [2] 在线接口（从远程 API 获取脚本内容）
3. 运行初始化脚本创建项目骨架：
   ```bash
   python scripts/init_project.py "<项目名>" --output <保存位置> --mode B --episodes 6
   ```
   脚本会创建完整目录结构和配置文件：
   ```
   projects/<项目名>/
   ├── config.json          # 项目配置（分镜模式、集数、风格等）
   ├── summary.md           # 每集摘要索引
   ├── characters.md        # 角色档案
   ├── foreshadowing.md     # 伏笔追踪
   └── episodes/            # 分集稿子
       ├── ep001_<标题>.md
       ├── ep002_<标题>.md
       └── ...
   ```
3. 如果选择在线接口，收集接口配置：
   - 接口地址（如 `https://api.example.com/v1/generate`）
   - API Key
   - 请求方法（POST/GET）
   - 请求体格式（参考 `references/script-api-spec.md`）
   - 测试接口连通性
4. 将 config.json 内容展示给用户确认，允许修改：
   - `density_mode`：A（对话多镜头少）/ B（平衡）/ C（电影短剧风）
   - `total_episodes`：计划总集数
   - `art_style`：AI 绘图风格描述
5. 配置文件 schema 详见 `references/config-schema.md`

## 工作流程

### 模式一：用户提供大纲

1. **接收大纲**
   - 用户提供故事大纲、主题、角色设定等
   - 确认项目名称（新项目 or 续写现有项目）

2. **项目结构检查**
   - 如果是现有项目，读取：
     - `项目名/summary.md`：每集摘要
     - `项目名/characters.md`：角色档案
     - `项目名/foreshadowing.md`：未回收伏笔
   - 如果是新项目，创建目录：
     ```
     projects/<项目名>/
     ├── summary.md          # 每集摘要索引
     ├── characters.md       # 角色档案
     ├── foreshadowing.md    # 伏笔追踪
     └── episodes/           # 分集稿子
         ├── ep001_<标题>.md
         ├── ep002_<标题>.md
         └── ...
     ```

3. **分镜密度选择（重要）**
   - 如果用户未在初始化时选择，现在必须询问：
   ```
   请选择分镜密度模式：
   1. 对话多，镜头少（传统漫画风，每集30-40场景）
   2. 一个对话对应一个镜头（平衡模式，每集50-60场景）
   3. 一段对话多个镜头（电影短剧风，每集150-250场景）
   ```
   - 将选择更新到项目 `config.json`

4. **生成分镜脚本**
   - 根据大纲 + 项目上下文 + 分镜密度模式生成详细分镜
   - **每个场景必须附带 AI 绘图提示词**，格式详见 `references/ai-prompt-template.md`
   - 每个场景包含：
     - **页码与格号**：`## Page X` / `### Panel X`，禁止继续使用 `## Scene X`
     - **格子**：普通格/横向大格/竖向窄格/半页大格/跨页大格/三连小格/无边框格等
     - **画面**：人物表情、动作、环境细节、光线氛围、关键物件
     - **构图**：远景/中景/特写/俯拍/仰拍/过肩/双人构图等
     - **气泡**：角色、位置、气泡类型、台词
     - **旁白**：旁白框位置与内容；没有则写“无”
     - **拟声**：拟声字、位置、字体表现；没有则写“无”
     - **转场**：动作/视线/时间跳切/情绪/悬念/对比/场景/翻页钩子
     - **AI 提示词**：正向/反向提示词，风格部分只能来自 `style_guide.md`

5. **保存和维护**
   - 保存稿子到 `episodes/epXXX_<标题>.md`
   - 运行自动更新脚本提取结构化信息：
     ```bash
     python scripts/update_project.py episodes/ep001_xxx.md --project-dir projects/<项目名> --episode-num 1
     ```
     脚本自动完成：
     - 提取新角色 → 追加到 `characters.md`
     - 扫描伏笔关键词 → 追加到 `foreshadowing.md`
     - 生成摘要条目 → 追加到 `summary.md`
     - 更新 Panel 数/对话数 → 更新 `config.json`
   - 运行质量验证脚本检查生成质量：
     ```bash
     python scripts/validate_episode.py episodes/ep001_xxx.md --project-dir projects/<项目名>
     ```
   - 运行角色一致性检查：
     ```bash
     python scripts/consistency_check.py episodes/ep001_xxx.md --project-dir projects/<项目名>
     ```
   - 所有检查通过后，项目文件已自动更新完成

### 模式二：热点话题生成

1. **题材选择流程**
   - 询问用户：
     ```
     请选择创作方向：
     1. 提供具体题材（如：校园恋爱、科幻冒险、职场励志）
     2. 让我抓取热点话题 TOP10 供你选择
     ```

2. **抓取热点**
   - **平台访问限制（重要）**：
     - ✅ **百度热搜**（top.baidu.com/board?tab=realtime）：无需登录，可直接抓取，推荐优先使用
     - ❌ 微博热搜（s.weibo.com/top/summary）：需要登录，会重定向到访客系统
     - ❌ 知乎热榜（zhihu.com/hot）：需要登录，返回空页面
     - ⚠️ B站、抖音、豆瓣：访问受限或需特殊处理
   - **抓取策略**：
     1. 优先使用 `browser_navigate` 访问百度热搜
     2. 提取热点标题、排名信息
     3. 根据话题内容分类（社会、科技、娱乐、体育等）
     4. 筛选出适合创作的话题（排除纯时政、过于严肃的内容）
   - 时效性：15天内
   - 类型：全类型
   - 保存热点记录到 `hotspots/YYYY-MM-DD.md`

3. **展示 TOP10**
   - 从抓取结果中筛选适合创作的话题（排除纯时政、灾难等不适合漫画的内容）
   - 按热度排序，展示：
     ```
     1. 【类型/风格】<话题标题>
        创作方向：<简要说明改编思路>
     2. ...
     ```
   - 用户选择后，生成创意大纲

4. **生成流程**
   - 基于热点生成故事大纲
   - 确认后进入"模式一"的生成流程

### 模式三：续写与修改

当用户要求继续写作或修改现有内容时，遵循 `references/editing-workflow.md`：

1. **读取上下文**
   - 读取 `summary.md` 了解整体进度
   - **强制读取上一集最后 3 个 Panel**，确保动作、台词、情绪和钩子衔接
   - 检查 `foreshadowing.md` 中的伏笔状态

2. **局部修改**
   - 用户指定场景：定位到具体场景，只修改该部分
   - 用户指定情节：检查相关伏笔，必要时新增记录
   - 修改后检查对话连贯性和角色一致性

3. **伏笔管理**
   - 新增伏笔：添加到 `foreshadowing.md` 未回收部分
   - 回收伏笔：从"未回收"移动到"已回收"，标注回收位置
   - 冲突检查：是否有长期未回收的伏笔需要处理

4. **写作风格延续**
   - 保持与已写集数相同的对话风格和分镜密度
   - 同一项目不能中途改变密度模式
   - **图片风格统一（强制）**：同一项目的所有集必须使用相同的 AI 绘图风格
     - 生成时只能从 `style_guide.md` 读取固定正向/反向提示词，注入每个 Panel
     - 如果 `style_guide.md` 缺失，禁止生成，先运行 `init_project.py` 初始化
     - 禁止 LLM 根据剧情临时拼接主画风、线条风格、上色方式、人物比例、负面提示词
     - 允许变化的只有：人物动作、表情、构图、光线、场景物件、情绪氛围
     - 续写时校验新增集数的 AI 提示词是否与 `style_guide.md` 一致
     - 在线接口传入 `style_guide` 字段时，优先级高于 `art_style`

### 模式四：批量生成（热点驱动）

**触发条件**：用户明确要求"批量生成"或指定了故事数量。

**前置选择（只选一次）**：
- 分镜密度模式：A / B / C（后续所有项目统一遵循）
- 每集集数：默认 5 集
- AI 绘图风格：可选
- 自动模式：`--auto` 参数表示全自动，不加则每完成一个项目暂停等待用户确认

**执行流程**：

1. **抓取热点**（只执行一次）
   - 调用 `fetch_baidu_hotspots()` 获取百度热搜
   - 如果抓取失败，回退到 `fallback_hot_topics()` 用 LLM 生成候选话题
   - 过滤掉时政、灾难、暴力等不适合漫画的内容

2. **循环生成**（独立项目，不保留上下文）
   - 从候选话题中轮流选择（避免重复）
   - 每个项目：
     a. 调用 `init_project.py` 创建独立项目骨架和 `style_guide.md`
     b. 调用 LLM 生成大纲 + Page/Panel 格式的分集漫画脚本
     c. 运行 `update_project.py` 自动更新项目文件
     d. 运行 `validate_episode.py` + `consistency_check.py` 验证
     e. 保存汇总结果，**清空上下文**，继续下一个
   - 脚本通过 `batch_generate.py` 驱动，不依赖 Hermes 会话记忆

3. **输出汇总**
   - 控制台输出每个项目的状态（✓ / ⚠ / ✗）
   - 生成 `batch_report_YYYYMMDD_HHMMSS.json` 报告文件

**运行命令**：
```bash
python scripts/batch_generate.py --count 5 --mode B --auto
python scripts/batch_generate.py --count 3 --mode C --episodes 4 --art-style "宫崎骏风格"
python scripts/batch_generate.py -n 2 -m A -o ./my-comics
```

**参数说明**：
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--count` / `-n` | 生成故事数量（必填） | — |
| `--mode` / `-m` | 分镜密度 A/B/C | B |
| `--episodes` / `-e` | 每故事集数 | 5 |
| `--output` / `-o` | 输出目录 | ~/comic-projects |
| `--art-style` / `-a` | AI 绘图风格描述，支持预设 key 或自定义描述 | `japanese-modern` |
| `--auto` | 全自动模式，不暂停确认 | false |

**设计要点**：
- 每个项目完全独立，生成完成后不保留 LLM 上下文
- 热点话题只抓取一次，轮换使用
- 失败的项目跳过并记录，不影响其他项目
- 验证不通过标记为 WARN 而非终止

## 分镜密度模式

生成前必须让用户选择以下三种模式之一：

### 模式 A：对话多，镜头少（传统漫画风）

**特点**：以对话推进剧情，镜头数量少但信息量大，类似少年漫画/少女漫画的风格。

**每集规格**：
- Panel 数：30-40 个
- 每个 Panel 包含：格子、画面、构图、气泡/旁白/拟声/转场、AI 提示词
- 总对话量：每集约 200-300 段
- 适合类型：恋爱、日常、推理对话密集型

**模板**：
```markdown
### Panel 1
**构图**：全景  
**画面**：教室窗外樱花飘落，阿明坐在座位上发呆。阳光透过窗户洒在课桌上。  
**对话**：
- 旁白："那天的风，和往常一样温柔。"
- 阿明（心理独白）："为什么她说那句话的时候，眼神在躲闪？"
- 同桌："喂，想什么呢？老师叫你呢。"
- 阿明："啊？……"（慌乱地站起来，碰倒了课本）
- 老师："李明，你又在发呆！"
- 阿明（内心）："完了完了，这下糗大了。"
```

### 模式 B：一个对话对应一个镜头（平衡模式）

**特点**：对话与镜头一一对应，节奏适中，最接近传统漫画分镜。
## Page/Panel 漫画脚本格式模板

```markdown
# 第X集：<标题>

**故事梗概**：<简要说明本集内容>
**分镜模式**：A / B / C
**预计页数**：X页
**预计 Panel 数**：X个
**本集核心情绪**：<紧张/甜/悬疑/爆笑/反转>
**本集钩子**：<本集最后让读者想继续看的悬念>

---

### Panel 1
**构图**：远景
**画面**：<人物表情、动作、环境细节、光线氛围>
**对话**：
- <角色/旁白>："<台词>"
**AI 提示词**：

正向：
```
masterpiece, best quality, [画面描述], [镜头角度], [艺术风格], cinematic lighting
```

反向：
```
worst quality, low quality, blurry, deformed, bad anatomy, extra limbs
```

---

*本集完*

**生成统计**：
- 总 Panel 数：X
- 总对话数：X
- 验证状态：✓ 通过
```
### Panel 1
**构图**：全景  
**画面**：黄昏的城市天台，夕阳将天空染成橙红色。主角阿明站在栏杆边，背对镜头。

---

### Panel 2
**构图**：中景  
**画面**：风吹起阿明的短发和校服衣摆。他双手插兜，侧脸若有所思。

---

### Panel 3
**构图**：特写  
**画面**：阿明的眼睛特写，眼神坚定但带着一丝迷茫。

---

### Panel 4
**构图**：全景  
**画面**：天台门突然打开，女主小雨跑进来。

---

### Panel 5
**构图**：中景  
**画面**：小雨喘着气，脸颊微红，马尾辫在身后晃动。

---

### Panel 6
**构图**：双人镜头  
**画面**：阿明转身，表情惊讶地看着小雨。

---

### Panel 7
**构图**：特写（小雨）  
**画面**：小雨的眼神闪烁，似乎在犹豫要不要说出口。
**对话**：
- 小雨："阿明！你还在这里啊！"

---

### Panel 8
**构图**：特写（阿明）  
**画面**：阿明微微皱眉，露出疑惑的表情。
**对话**：
- 阿明："小雨？你怎么……"
```



## 标准 Page/Panel 模板（强制）

每一集必须使用 Page → Panel 结构。`Scene` 是影视场景单位，漫画脚本中禁止继续使用 `## Scene X`。

```markdown
# 第X集：<标题>

**故事梗概**：<简要说明本集内容>
**分镜模式**：A / B / C
**预计页数**：X页
**预计 Panel 数**：X个
**本集核心情绪**：紧张 / 甜 / 悬疑 / 爆笑 / 反转
**本集钩子**：<本集最后让读者继续看的悬念>

---

## Page 1

### Panel 1

**格子**：普通格 / 横向大格 / 竖向窄格 / 半页大格 / 跨页大格 / 三连小格 / 无边框格
**画面**：<人物、动作、表情、环境、光线、关键物件>
**构图**：<远景/中景/特写/俯拍/仰拍/过肩/双人构图>，<视觉重点说明>

**气泡**：
- <角色名>（<位置>，<气泡类型>）："<台词>"

**旁白**：
- 旁白框（<位置>）："<旁白内容>"

**拟声**：
- `<拟声词>`：<字体大小、位置、表现方式>

**转场**：<动作转场/视线转场/时间跳切/情绪转场/悬念转场/对比转场/场景转场/翻页钩子>

**AI 提示词**：
正向：
```text
<来自 style_guide.md 的固定风格>, <本 Panel 画面>, <构图>, <光线>, <情绪>
```
反向：
```text
<来自 style_guide.md 的固定反向提示词>
```

---

## 本集结尾钩子

**钩子类型**：身份反转 / 情感悬念 / 危机升级 / 信息揭露 / 误会加深
**画面设计**：<最后一个 Panel 的具体画面>
**钩子台词**："<一句强钩子台词>"

## 下集提示

下一集将揭示：<一句话说明>
读者期待点：<让读者想看的东西>

---

*本集完*
```

### Panel 必填字段

每个 Panel 必须包含：`格子`、`画面`、`构图`、`气泡`、`旁白`、`拟声`、`转场`、`AI 提示词`。没有气泡/旁白/拟声时也必须写“无”，方便脚本验证。

## 分镜通用模板

```markdown
# 第X集：<标题>

**故事梗概**：<简要说明本集内容>

---

### Panel 1
**构图**：远景
**画面**：<人物表情、动作、环境细节、光线氛围>
**对话**：
- <角色/旁白>："<台词>"

---

*本集完*
```

## 角色档案模板

```markdown
# 角色档案

## 阿明
- **全名**：李明
- **年龄**：17岁
- **外貌**：黑色短发，偏瘦，常穿校服。眼神锐利但温柔。
- **性格**：内向、细腻、责任感强，不善表达情感。
- **背景**：单亲家庭，父亲早逝，与母亲相依为命。
- **首次登场**：第1集
- **关键情节**：在天台遇见小雨（第1集）

## 小雨
- **全名**：陈雨欣
- **年龄**：16岁
- **外貌**：齐肩马尾辫，大眼睛，笑起来有酒窝。常穿白衬衫 + 格子裙。
- **性格**：开朗、主动、乐观，但内心敏感。
- **背景**：父母工作忙碌，常感到孤独。
- **首次登场**：第1集
- **关键情节**：向阿明表白（第1集）
```

## 伏笔追踪模板

```markdown
# 伏笔追踪

## 未回收
- [ ] 阿明父亲的遗物（第2集埋下）
- [ ] 小雨手机里的神秘短信（第3集埋下）
- [ ] 天台栏杆上的涂鸦（第1集埋下）

## 已回收
- [x] 阿明的转学原因（第5集埋下，第8集回收）
- [x] 小雨的家庭矛盾（第4集埋下，第7集回收）
```

## 摘要索引模板

```markdown
# 项目摘要

## 第1集：天台相遇
- **主要情节**：阿明在天台遇见小雨，小雨向他表白。
- **关键转折**：阿明没有立即回应，留下悬念。
- **新增角色**：阿明、小雨
- **伏笔**：天台栏杆上的涂鸦

## 第2集：回忆往昔
- **主要情节**：阿明回想父亲去世的往事。
- **关键转折**：发现父亲遗物中的神秘信件。
- **新增角色**：阿明母亲（回忆）
- **伏笔**：父亲的遗物
```

## 注意事项

1. **上下文管理**
   - 读取 `summary.md` 而非完整稿子，避免上下文过长
   - 每集摘要控制在 100-200 字
   - 角色档案只记录核心信息

2. **伏笔管理**
   - 新增伏笔时标注集数
   - 回收时移除并注明回收位置
   - 提醒用户长期未回收的伏笔
   - 详见 `references/editing-workflow.md`

3. **分镜细节**
   - 画面描述要具象化（颜色、光线、动作、表情）
   - 镜头角度明确（远景/中景/特写/俯拍/仰拍）
   - 对话自然，符合角色性格
   - **每个场景必须附带 AI 绘图提示词**，格式详见 `references/ai-prompt-template.md`

4. **质量验证**
   - 每集生成后必须运行验证脚本：
     ```bash
     python scripts/validate_episode.py episodes/epXXX_xxx.md --project-dir projects/<项目名>
     ```
   - 检查项：Panel 数是否符合模式要求、Page/Panel 格式是否正确、必填字段是否完整、AI 提示词是否来自 style_guide、伏笔是否一致
   - 验证不通过时必须修复后再继续

5. **文件命名**
   - 集数用三位数：ep001, ep002, ep010, ep100
   - 标题用故事核心：`ep001_天台相遇.md`

6. **热点抓取限制**
   - **优先使用百度热搜**（top.baidu.com/board?tab=realtime），无需登录
   - 微博、知乎需要登录，会访问失败，不要浪费时间重试
   - 详细平台可访问性参见 `references/hotspot-scraping.md`
   - 每次抓取后询问用户是否继续

7. **超长内容写入（重要）**
   - `write_file` 工具对含中文的超长内容（>5000字符）可能因 stream timeout 失败
   - **解决方案**：使用 `execute_code` + Python `open().write()` 分批写入文件
   - 每批3000-4500字符，用 `'a'` 模式追加后续部分
   - 示例：
     ```python
     # 第一批：创建文件
     with open(ep_path, 'w', encoding='utf-8') as f:
         f.write(part1)
     # 后续批：追加
     with open(ep_path, 'a', encoding='utf-8') as f:
         f.write(part2)
     ```
   - 长篇连载每集写到文件后统计场景数，确保完整性

8. **配置文件管理**
   - 项目配置存储在 `config.json`，schema 详见 `references/config-schema.md`
   - 每次更新项目状态后同步修改 `config.json`
   - 续写时必须读取 `config.json` 获取当前模式和进度

9. **篇幅规划**
   - 根据用户选择的模式调整每集场景数
   - 模式 A（对话多，镜头少）：3-4集 × 30-40场景 = 总90-160场景
   - 模式 B（平衡模式）：3-6集 × 50-60场景 = 总150-360场景
   - 模式 C（电影短剧风）：3-4集 × 150-250场景 = 总450-1000场景
   - 用户未指定时，默认使用模式 B



10. **漫画脚本质量规则（重要）**
   - 每页建议 3-7 个 Panel，超过 8 个需提醒页面可能过密
   - 单个气泡建议 20-35 字，超过 50 字需提醒台词过长
   - 连续 5 个 Panel 构图完全相同需提醒画面变化不足
   - 连续 5 个 Panel 没有气泡/旁白/拟声需提醒节奏可能过空
   - 每集必须包含 `## 本集结尾钩子` 与 `## 下集提示`
   - 续写时新一集前 1-3 个 Panel 必须承接上一集最后 3 个 Panel 的动作、台词或悬念；若跳切，必须在 `转场` 字段明确标注

11. **完整项目生成验收（强制）**
   - 生成“完整项目”不能只创建目录和通过格式校验，必须检查故事是否连贯
   - 验收顺序：
     1. 跑 `validate_episode.py`、`update_project.py`、`consistency_check.py`
     2. 人工/LLM 读取 `summary.md`、`characters.md`、`foreshadowing.md` 和每集前 3 个/后 3 个 Panel
     3. 检查每集标题是否真的被剧情兑现，不能三集套同一段模板
     4. 检查第 N 集结尾钩子是否被第 N+1 集前 1-3 个 Panel 承接
     5. 检查 `summary.md` 是否仍有“待补充”，有则不算完成
     6. 检查 `foreshadowing.md` 是否被 `**画面**`、AI prompt、拟声、统计行污染
   - 如果只是为了测试格式，项目名/回复中必须明确标注“格式验证项目”；不要把它描述成正式可用漫画稿
   - 正式漫画稿必须先有每集 beat 表（开场→异常→反应→线索→危机→反转钩子），再展开成 Panel，避免 40+ 个 Panel 重复同一画面模板
   - GitHub 同步规则：本地修改和双副本同步可以执行，但 commit/push 必须等用户明确说“push”后再做

## 示例对话

**用户**：\"帮我写一个校园恋爱故事的第一集\"

**AI**：
```
好的！这是新项目还是续写现有项目？

如果是新项目，请告诉我：
1. 项目名称
2. 故事大纲或核心设定
3. 主要角色（可选，我可以根据大纲创建）
4. 分镜密度模式：
   - 模式A：对话多，镜头少（传统漫画风，每集30-40场景）
   - 模式B：一个对话对应一个镜头（平衡模式，每集50-60场景）
   - 模式C：一段对话多个镜头（电影短剧风，每集150-250场景）
5. 计划总集数（默认6集）

我会自动创建项目结构和配置文件。
```

---

**用户**："继续写第二集"

**AI**：
```
好的！让我先读取项目上下文...

[读取 summary.md、characters.md、foreshadowing.md]
[读取 ep001_天台相遇.md 的最后几个场景]

项目状态：
- 当前模式：B（平衡模式）
- 已完成：第1集
- 未回收伏笔：2个
- 下一步：第2集

继续生成第2集...
[生成分镜脚本]
[运行 update_project.py 自动更新项目文件]
[运行 validate_episode.py 验证质量]
[运行 consistency_check.py 检查角色一致性]
```

---

**用户**："生成第一集后自动整理项目文件"

**AI**：
```
生成分镜脚本后，自动运行：

1. python scripts/update_project.py episodes/ep001_xxx.md --project-dir projects/<项目名> --episode-num 1
   → 自动提取角色、伏笔、摘要，更新 summary.md / characters.md / foreshadowing.md / config.json

2. python scripts/validate_episode.py episodes/ep001_xxx.md --project-dir projects/<项目名>
   → 验证场景数、AI 提示词完整性

3. python scripts/consistency_check.py episodes/ep001_xxx.md --project-dir projects/<项目名>
   → 检查角色一致性，识别未记录的角色
```

---

**用户**：\"我没有灵感，帮我找热点\"

**AI**：
```
好的！我现在去抓取最近15天的热点话题...

[抓取中...]

以下是 TOP10 热点话题：
1. 《XXX》电影票房破10亿 - 微博/豆瓣 - 热度98
2. AI绘画版权争议 - 知乎 - 热度95
3. ...

请选择一个话题，或告诉我你想要的题材方向。
```

 d2c77e4 (feat: add update check, references, and scripts)
## 参考资料
- `references/ai-prompt-template.md` — AI 绘图提示词模板（SD/Midjourney/DALL-E 格式）
- `references/config-schema.md` — 项目配置文件 schema
- `references/editing-workflow.md` — 续写与修改工作流
- `references/hotspot-scraping.md` — 热点抓取平台可访问性指南
- `references/script-api-spec.md` — 在线接口规范（端点定义、请求/响应格式、错误码），所有在线接口必须遵循此规范
- `references/online-reader-deployment.md` — 线上 Reader/API 部署记录：`comic-script-generator.YOUR_DOMAIN/reader` 与服务器-叶 `<user-home>/comic-script-generator-api`、Nginx、systemd 的关系，以及推荐配套 skills
- `references/batch-generation.md` — 批量生成架构设计与常见问题
- `references/panel-format-generation-lessons.md` — Page/Panel 漫画脚本生成实战经验：格式通过不等于故事连贯、先写 episode beats、保守提取伏笔、6 集连载递进链样例

- `references/export-for-render.md` — 从现有漫画稿提取 Panel 并转换为 story-renderer 输入脚本的桥接规范

## 脚本工具

- `scripts/init_project.py` — 项目初始化脚本，自动创建目录结构和配置文件
- `scripts/update_project.py` — 自动更新项目文件，从分镜稿提取角色/伏笔/摘要并更新到对应文件
- `scripts/validate_episode.py` — 分集验证脚本，检查场景数、AI 提示词、伏笔一致性
- `scripts/consistency_check.py` — 角色一致性检查脚本，验证对话风格和外貌描述是否与档案一致
- `scripts/check_update.py` — 更新检查脚本，检测远程仓库是否有新提交（网络不通时自动跳过）
- `scripts/batch_generate.py` — 批量生成脚本，自动抓取热点并生成多个独立漫画项目
- `references/batch-generation.md` — 批量生成架构设计与常见问题
- `scripts/batch_generate.py` — 批量生成脚本，自动抓取热点并生成多个独立漫画项目

## 批量生成实现要点

基于 `batch_generate.py` 的实际运行经验，以下坑点必须在 skill 中约束：

1. **跨平台配置路径**
   - 禁止硬编码 `C:\\Users\\...` 或 `~/.hermes/`
   - 必须按优先级搜索：环境变量 `HERMES_CONFIG` → CWD `./config.yaml` → skill 目录 → 平台标准目录
   - 全部缺失时回退环境变量，绝不能假设本机路径

2. **大纲完整传递**
   - 禁止截断 outline（如 `outline[:2000]`）
   - 每个 episode 必须传入完整 outline，否则后续分集失忆、伏笔断裂

3. **LLM 重试与退避**
   - 网络错误、429、5xx 必须自动重试（推荐 3 次）
   - 退避公式：`base * 2^attempt + random jitter`
   - 单次失败不能丢弃整个项目

4. **速率限制**
   - episode 之间插入 1.5-3 秒延迟
   - 故事之间插入 2-5 秒冷却
   - 避免触发 API rate limit 导致批量失败

5. **断点续传**
   - 必须生成 `.batch_checkpoint.json` 记录已完成项目
   - 支持 Ctrl+C 安全中断，重新执行时跳过已完成项

6. **项目名唯一性**
   - 使用 `timestamp + index + UUID` 确保不冲突
   - 禁止仅用时间戳，同秒启动会覆盖

7. **配置解析健壮性**
   - 跳过注释行和空行
   - 正确处理带引号的值
   - 失败时回退环境变量，不抛异常

8. **验证容错**
   - 每个验证脚本独立 try/except，超时 60 秒自动跳过
   - 失败标记 WARN 而非终止整个批次

9. **话题来源兜底**
   - 百度抓取失败 → LLM 生成 20 个话题
   - LLM 也失败 → 20 个硬编码安全话题
   - 话题不足时循环轮换，不中断

10. **成本估算**
    - 启动时输出 LLM 调用次数、token 估算、预计耗时
    - 非 auto 模式必须先问 "Proceed? [Y/n]"

## 脚本调试经验

### 验证脚本常见问题

1. **Scene 正则分割的偏移问题**
   - `re.split(r'^## Scene \\d+', content)` 的第一个元素是标题/头部，不是场景
   - 必须跳过第一个元素：`scenes[1:] if len(scenes) > 1 else scenes`
   - 否则 AI 提示词检测会误报第一个场景缺失

2. **Python f-string 多行语法**
   - 含中文的多行 f-string 容易触发 `SyntaxError: unterminated f-string`
   - 修复方案：改用字符串拼接 `"# " + project_name + " - 项目摘要\n\n..."`
   - 或使用 `textwrap.dedent()` + 普通字符串

3. **缺失 import**
   - 脚本中用到 `argparse` 时必须显式 `import argparse`
   - 不要假设全局已导入

## 桥接渲染（story-renderer）集成说明

**触发条件**：用户要求先写稿，再挑稿生成漫画图片或视频时，进入此分支。

**前置条件**：
- 项目已通过 `comic-script-generator` 初始化并生成了至少一集稿子
- `story-renderer` skill 已安装且初始化（配置了图片生成 API）
- 项目的 `style_guide.md` 存在且完整

**桥接脚本**：
- `scripts/export_for_render.py`：从 episode 的 `## Page X` / `### Panel X` 提取内容，生成 story-renderer 兼容输入脚本
- 输出到 `projects/<项目名>/render_input/<剧集>_render.md`

**注意事项**：
- 同一个 Panel 可能因对话量大而拆分为多个渲染镜头，由 `export_for_render.py` 自动处理
- 渲染使用的 API 配置来自 `story-renderer` 的 `config.json`，不与 comic-script-generator 冲突
- 如果 story-renderer 未初始化，引导用户先运行“初始化 story-renderer”

## 本地与远端版本对比经验

### 版本号可能 misleading
- 本地 skill 的 `version:` 可能高于 GitHub 最新 tag，说明本地有未 push 改动
- 远端 `main` 最新提交不一定等于最新 tag，需以 tag 版本号为准
- 对比时优先检查：
  1. 本地 SKILL.md 的 `version:` 字段
  2. GitHub repo 的 latest release/tag
  3. `main` 分支最新 commit message 是否已打 tag

### 终端失效时的降级策略
- Windows 上 `terminal` 工具可能因工作目录异常持续失败（表现为 `cd: ... No such file or directory` 循环）
- 此时不要继续 retry terminal，改用：
  1. `read_file` / `search_files` 读本地文件
  2. `browser_navigate` 访问 `https://raw.githubusercontent.com/<user>/<repo>/main/<path>` 获取远端文件
  3. `browser_navigate` 访问 `https://github.com/<user>/<repo>/commits/main.atom` 获取提交历史
  4. `browser_navigate` 访问 commit 详情页查看变更文件树
- 这些降级手段对纯文本文件有效；二进制文件需另寻方案

## 用户工作流偏好

- **先确认再执行**：涉及多步修改、设计方案、或可能影响现有文件的变更时，先向用户说明方案并等待确认，再执行具体操作。不要跳过说明直接开始修改。
- **风格统一优先**：同一项目的所有集必须使用相同的 AI 绘图风格，生成时以 `style_guide.md` 为准，不得让 LLM 自由拼凑风格词。
- **双副本同步**：修改 skill 文件后必须同时更新 Desktop 开发副本和 AppData 已安装副本。默认只做本地同步和验证；**禁止自动 commit/push**，只有当用户明确说“commit”或“push”时才执行对应 Git 操作。
- **分阶段交付**：优先分“生成稿子”和“渲染漫画”两个阶段；不要默认一步出图/视频。用户确认稿子后，再进入渲染。
- **只审格式，不审剧情**：若用户只要求格式/规范审核，不要评价剧情好坏，只检查 Page/Panel 结构、必填字段、风格一致性、钩子承接。

## 模式五：脚本生成后渲染为漫画图片（集成 story-renderer）

**触发条件**：用户已有 comic-script-generator 项目，想将某集分镜稿渲染为漫画图片或视频。

**前置条件**：
- 项目已通过 comic-script-generator 初始化并生成了至少一集稿子
- story-renderer skill 已安装且初始化（配置了图片生成 API）
- 项目的 style_guide.md 存在且完整

**工作流程**：

1. **选择项目与剧集**
   - 展示已有项目列表，用户选择目标项目
   - 展示该项目下已完成的剧集，用户选择要渲染的剧集
   - 用户可选择渲染全部集数或指定集数

2. **生成 story-renderer 输入脚本**
   - 运行脚本从 episode 稿子提取可渲染内容：
     python scripts/export_for_render.py episodes/epXXX_xxx.md --project-dir projects/<项目名> --style-guide projects/<项目名>/style_guide.md
   - 脚本自动完成：
     - 读取每集 Page X / Panel X 结构
     - 提取每个 Panel 的画面、构图、AI 提示词字段
     - 注入 style_guide.md 的固定正向/反向提示词
     - 生成 story-renderer 兼容的输入脚本（镜头 N 格式）
     - 如果有气泡台词，自动转为旁白字段
     - 输出到 projects/<项目名>/render_input/epXXX_<标题>_render.md

3. **预览与确认**
   - 展示提取的镜头数和 Estimated 成本（基于 story-renderer 的 API 定价）
   - 用户可编辑、跳过、或调整单个镜头的提示词
   - 确认后调用 story-renderer 的渲染流程

4. **调用 story-renderer 渲染**
   - 使用 story-renderer 的 render 命令（或等效流程）
   - 传入生成好的输入脚本
   - 渲染参数：
     - 默认宽高比：9:16（竖屏漫画）
     - 一致性策略：固定 seed + 角色指纹（从 style_guide.md 和 characters.md 提取）
     - 负面提示词：来自 style_guide.md
   - 生成图片保存到 projects/<项目名>/rendered/epXXX/ 目录
   - 支持断点续传：已渲染的 Panel 不重复生成

5. **结果回写**
   - 渲染完成后，将图片路径回写到 episode 稿子的对应 Panel 下
   - 格式：在 Panel 末尾追加 渲染图：rendered/ep003/scene_05.png
   - 运行 update_project.py 更新项目状态

**参数说明**：
- --episodes / -e：要渲染的集数（如 1,2,3 或 all）
- --panels / -p：指定 Panel 范围（如 1-10）
- --width / -W：图片宽度，默认 1024
- --height / -H：图片高度，默认 1792
- --no-confirm：跳过确认直接生成

**注意事项**：
- 渲染前必须确认 style_guide.md 存在，否则终止并提示先生成
- 同一个 Panel 可能因对话量大而拆分为多个渲染镜头，由 export_for_render.py 自动处理
- 渲染使用的 API 配置来自 story-renderer 的 config.json，不与 comic-script-generator 冲突
- 如果 story-renderer 未初始化，引导用户先运行“初始化 story-renderer”


## 部署与访问说明

### 线上 Reader/API

- 站点域名：`comic-script-generator.YOUR_DOMAIN`
- Reader 页面路由：`/reader`（不是 `/reader.html`）
- 根路径 `/` 也会返回 Reader 页面
- API 统一通过 Nginx 反代到 `127.0.0.1:8081`
- 认证方式：请求参数 `api_key=<KEY>` 或请求头 `X-API-Key`
- 前端登录逻辑：调用 `/projects?api_key=...`，若返回 401 则提示“密钥无效”
- **注意**：直接访问 IP 或省略 `Host: comic-script-generator.YOUR_DOMAIN` 请求头时，Nginx default site 可能返回 404。浏览器正常访问域名通常没问题；如遇 404，优先检查 Cloudflare SSL 模式与 Nginx `server_name` 匹配。

### 前端优化记录

详见 `references/frontend-optimization.md`。已实现：
- 项目列表、分集列表、漫画列表、热点记录、搜索结果分页（默认 20 条/页）
- 图片懒加载（`loading="lazy"` + IntersectionObserver）
- 搜索结果上下文限制（`max-height: 200px` 滚动）
- 后端 `/projects`、`/projects/<name>/episodes`、`/comics`、`/hotspots`、`/search` 支持 `page`/`page_size`，返回 `count`/`page`/`page_size`/`total_pages`

## 更新日志

- v1.8.1：修正 export_for_render.py 输出为 story-renderer 手动分镜标准 `## 镜头 N`；README 徽章改为通用静态徽章
- v1.8.0：集成 story-renderer 渲染流程；新增 export_for_render.py 桥接脚本；支持稿子生成后直接渲染漫画图片
- v1.7.0：漫画脚本格式升级为 Page/Panel；新增格子/气泡/旁白/拟声/转场、结尾钩子、下集提示；脚本验证适配 Panel；续写强制读取上集末3个Panel；风格只读 style_guide
- v1.5.0：前端分页与懒加载优化；新增部署访问说明；reader 路由说明
- v1.4.0：新增在线脚本生成接口规范、config.json script_source 配置
- v1.3.0：新增自动更新项目文件脚本、角色一致性检查脚本
- v1.2.0：新增 AI 绘图提示词、初始化脚本、验证脚本、编辑工作流
- v1.1.0：新增三种分镜密度模式（对话多/平衡/电影短剧风）
- v1.0.0：初始版本，支持分镜生成、项目管理、热点抓取
