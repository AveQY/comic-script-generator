---
name: comic-script-generator
description: 根据大纲或热点生成漫画分镜稿/小说/短剧分镜脚本，支持项目管理、角色档案、伏笔追踪
version: 1.25.0
tags: [creative, comic, screenplay, storyboard]
---

# 漫画脚本生成器

为漫画、图片故事生成详细分镜脚本的工作流程。核心输出单位为 Page → Panel → 气泡/旁白/拟声/转场，而不是影视化 Scene。支持从用户大纲或热点话题生成内容，维护项目结构、角色档案、风格指南和伏笔追踪。同时提供在线接口，允许外部系统远程调用生成脚本。

## 隐私与本地敏感配置（强制）

- 真实 API token、Authorization/Bearer、Cookie、私有域名、服务器公网 IP、VPN/代理订阅、数据库密码等敏感信息，**只能保存在本地私有配置文件**，不能写入 `SKILL.md`、README、references、示例文件、项目稿件或任何准备提交/发布的文件。
- 生图接口配置优先读取：`--config` → `$COMIC_IMAGE_CONFIG` → `~/.config/comic-script-generator/image_config.json`。
- 推荐私有配置路径：`~/.config/comic-script-generator/image_config.json`，权限设置为 `600`。
- skill 目录内只允许保留 `config.example.json` 占位模板；真实 `config.json` 即使被 `.gitignore` 忽略，也不作为推荐存放位置。
- 发布、同步、打包 skill 前必须运行 `python3 scripts/privacy_check.py`，确认没有真实 token、私有 IP/域名或本机路径泄漏。

## 文件命名与隐私规则（强制）

### 引用文件命名
- reference 文件必须使用**主题命名**，禁止包含日期（日期暗示临时文件，埋没关键内容）。
- 正确：`references/reader-route-ordering.md`、`references/light-novel-garbled-text-cleanup.md`
- 错误：`references/reader-route-ordering-2026-07-19.md`
- 更新日志（`## 更新日志` 节）可以使用日期标注版本，但文件名本身不能带日期。

### 隐私红线
- 禁止在 SKILL.md、references、templates、scripts 中写入：
  - 真实服务器路径（如 `home/ubuntu/...`）
  - 公网 IP 地址
  - 真实项目名（中文小说名、项目代号）
  - 代理端口、订阅链接、API Key
- 示例/贴士中使用通用占位：`<user-home>/`、`<reader-deploy-dir>/`、`DemoProjectA`。
- 每次清理后运行：
  ```bash
  grep -rn 'home/ubuntu\|110\.42\.\|8\.141\.124\.\|/root/comic-projects\|tokenkey' references/ SKILL.md
  ```
  确认无泄漏。

## 文件命名与隐私规则（强制）

### 引用文件命名
- reference 文件必须使用**主题命名**，禁止包含日期（日期暗示临时文件，埋没关键内容）。
- 正确：`references/reader-route-ordering.md`、`references/light-novel-garbled-text-cleanup.md`
- 错误：`references/reader-route-ordering-2026-07-19.md`、`references/light-novel-garbled-text-cleanup-2026-07-08.md`
- 更新日志（`## 更新日志` 节）可以使用日期标注版本，但文件名本身不能带日期。
- **备份文件禁止上传**：`.gitignore` 必须包含 `*.bak*`、`*.backup*` 模式，防止 `.html.bak` 等文件被误提交到 GitHub。

### 隐私红线
- 禁止在 SKILL.md、references、templates、scripts 中写入：
  - 真实服务器路径（如 `<user-home>/...`）
  - 公网 IP 地址
  - 真实项目名（中文小说名、项目代号）
  - 代理端口、订阅链接、API Key
- 示例/贴士中使用通用占位：`<user-home>/`、`<reader-deploy-dir>/`、`<projects-dir>/`、`DemoProjectA`。
- 每次清理后运行：
  ```bash
  grep -rn 'home/ubuntu\\|110\\.42\\.48\\.\\|8\\.141\\.124\\.\\|/root/comic-projects\\|tokenkey' references/ SKILL.md
  ```
  确认无泄漏。

### 隐私清理工具
- `scripts/privacy_check.py` — 发布/同步前隐私扫描脚本，检查真实 token、私有 IP/域名、本机路径和误放的 `config.json`。

## 更新检查（每次使用前）

- 真实 API token、Authorization/Bearer、Cookie、私有域名、服务器公网 IP、VPN/代理订阅、数据库密码等敏感信息，**只能保存在本地私有配置文件**，不能写入 `SKILL.md`、README、references、示例文件、项目稿件或任何准备提交/发布的文件。
- 生图接口配置优先读取：`--config` → `$COMIC_IMAGE_CONFIG` → `~/.config/comic-script-generator/image_config.json`。
- 推荐私有配置路径：`~/.config/comic-script-generator/image_config.json`，权限设置为 `600`。
- skill 目录内只允许保留 `config.example.json` 占位模板；真实 `config.json` 即使被 `.gitignore` 忽略，也不作为推荐存放位置。
- 发布、同步、打包 skill 前必须运行 `python3 scripts/privacy_check.py`，确认没有真实 token、私有 IP/域名或本机路径泄漏。

## 使用场景

- 用户提供故事大纲，生成详细分镜脚本
- 抓取热点话题，生成相关创意内容
- 管理长篇连载项目，追踪角色和伏笔

## 更新地址

源仓库：https://github.com/AveQY/comic-script-generator

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
   **路径注意：** 当前脚本会在 `<保存位置>/projects/<项目名>/` 下创建项目，而不是直接创建到 `<保存位置>/<项目名>/`。初始化后验证文件时应以脚本输出的 `Project created: ...` 为准，再读取对应路径的 `config.json` / `style_guide.md`。
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
**示例**：
```
**AI 提示词**：
正向：
```text
masterpiece, best quality, [画面描述], [镜头角度], [艺术风格], cinematic lighting, no text, no letters, leave empty space for speech bubbles
```

反向：
```text
worst quality, low quality, blurry, deformed, bad anatomy, extra limbs, no text, no letters
```

---

*本集完*
```markdown
### Panel 1

**格子**：横向大格（开场环境格）
**画面**：整栋公寓楼的外景，深夜2点。除了506号房间有一扇窗户亮着灯，其他窗户全是暗的。
**构图**：远景，从街对面仰拍整栋楼，突出506那扇亮灯的窗户
**气泡**：
- 无
**旁白**：
- 旁白框（左上角）："凌晨两点。整座城市都在沉睡——但有些人，才刚刚进入工作状态。"
**拟声**：
- `虫鸣……`：极小的背景字，夏夜环境音
**转场**：开场场景
**AI 提示词**：
正向：
```text
masterpiece, best quality, modern manga style, bold lines, screentone, dynamic angles, sharp details, anime aesthetic, apartment building exterior at night, 2am, only one window lit on 5th floor, moonlight, empty street, streetlamp, wide shot, cinematic lighting, quiet night atmosphere
```
反向：
```text
worst quality, low quality, blurry, deformed, bad anatomy, extra limbs, watermark, text, signature
```
```

**关键点**：
- 正向提示词以 `masterpiece, best quality, <project_style_keywords>` 开头，然后是 Panel 具体场景描述，以 `cinematic lighting` 结尾
- 反向提示词固定不变，含 `watermark, text, signature` 防止生图模型添加文字
- No bubble/narration/sound effects → 明确写"无"
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
   - 画面描述必须在生成稿子阶段就具象化，不能依赖后处理修复：每个 Panel 的 `画面` 字段必须写清角色姓名/外貌、关键物件、动作前后顺序、地点、光线、表情和画面焦点。
   - 禁止使用抽象模板句作为画面：如“普通日常场景”“异常事件突然出现”“主角靠近异常源”“关键配角登场”“世界观第一次展开”“危机升级”“情感冲突爆发”“关键线索出现”“结合本作设定”等。出现这些词时应视为不合格稿。
   - 每个 Panel 必须承接上一格的动作、视线、物件位置或情绪变化，保证图片按顺序看能读懂漫画逻辑。
   - AI 生图提示词只负责干净无字漫画画面：必须包含 `no text/no letters/leave empty space for speech bubbles`；中文对白、拟声由 `overlay_comic_text.py` 后期叠加，禁止指望生图模型生成中文气泡文字。
   - 画面描述要具象化（颜色、光线、动作、表情）
   - 镜头角度明确（远景/中景/特写/俯拍/仰拍）
   - 对话自然，符合角色性格
   - **每个场景必须附带 AI 绘图提示词**，格式详见 `references/ai-prompt-template.md`
   - **AI 提示词必须使用 fenced code block 格式（````text ... ````）**，不能使用 inline `- **AI正向提示词**：` 单行格式。validation 脚本按 ````text` 和 ```` 之间的内容解析提示词，inline 格式会导致解析失败/漏检。

4. **质量验证**
   - 每集生成后必须运行验证脚本：
     ```bash
     python scripts/validate_episode.py episodes/epXXX_xxx.md --project-dir projects/<项目名>
     ```
   - 检查项：Panel 数是否符合模式要求、Page/Panel 格式是否正确、必填字段是否完整、AI 提示词是否来自 style_guide、伏笔是否一致、`画面` 字段是否具体可画、是否含抽象模板句。
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
   - **两种不同的失败模式**：
     - **内容大小**：`write_file` 已验证可稳定处理 48KB+ 的中文 Markdown（约 720 行），内容本身大小通常不是瓶颈
     - **工具参数 token 上限（~8K tokens）**：大段中文文本在 tool call 参数中序列化后，token 计数远超磁盘字节数，导致流传输超时。触发阈值约 **content 中含 >4K 中文字符**。详见 `references/write_file-stream-timeout.md`
   - **防线**：优先尝试 `write_file`（简短配置/元数据可直写）；含大量中文的章节正文推荐用 Python 生成器脚本方案（见 `references/write_file-stream-timeout.md` 方案 A）
   - **禁止使用 Shell heredoc（任何形式）写入漫画脚本文件**：脚本内容包含反引号（AI 提示词 fenced code block）、中文标点、Markdown 粗体标记（`**`）、日语拟声词等特殊字符，heredoc 可能无声截断或损坏内容。
     - ❌ `cat >> << 'EOF'`（追加模式）——2026-07-06 实测追加 Pages 6-10 后导致 Pages 1-5 内容丢失（文件从 24335 字节缩至 23696 字节），无任何错误提示
     - ❌ `cat > << 'EOF'`（覆盖模式）——2026-07-06 实测写 1657 行虽未显式损坏，但全角字符 + 反引号的混合内容在 shell 流中仍不可靠
     - ✅ 正确方案：使用 `terminal` 工具运行 Python `open().write()` 或直接用 `write_file` 单次写入完整文件
   - **正确方案**：使用 `terminal` 工具运行 Python `open().write()` 或直接用 `write_file` 单次写入完整文件
   - 分批量参考：
        - 单次写入 48KB（约 720 行）已验证可稳定工作
        - 如需分批，首批用 `'w'` 模式，后续用 `'a'` 模式追加
        - **追加写入风险**：`write_file` 首批 + Python `'a'` 追加可能引入内容重复/错位（`---## Page X` 连在一起无换行、Page/Panel 章节被重复插入），根因可能与 sibling subagent 文件状态不同步有关。为防止追加污染，每批追加后立即用 `grep "^## Page"` 和 `grep "^### Panel"` 验证结构，不要等到全部写完再检查
        - **如果已污染**：用 Python 提取干净段（通过行号切片）并重新写入，详见 `references/file-writing-and-fallback.md` 第 4 节
        - 不要用 shell heredoc 替代 Python 写入
      - **写入后必须验证完整性**：用 `wc -l -c <file>` 检查行数和字节数，再用 `grep "^### Panel" | wc -l` 统计 Panel 数是否与预期一致（`^### Panel` 严格匹配行首开头的 Panel 标记，避免误匹配到 AI 提示词代码块内的文字；不用 `-c` 而用 `| wc -l` 是为了保留视觉确认顺序的能力）
   - 示例：
     ```python
     # 方案A：单次写入（推荐，已验证 48KB 以内）
     with open(ep_path, 'w', encoding='utf-8') as f:
         f.write(full_content)
     
     # 方案B：分批写入
     # 第一批：创建文件（w模式）
     with open(ep_path, 'w', encoding='utf-8') as f:
         f.write(part1)
     # 后续批：追加（a模式）
     with open(ep_path, 'a', encoding='utf-8') as f:
         f.write(part2)
     ```
   - 写入完成后，必须用 Python 或 shell 命令验证文件完整性：统计 Page 数、Panel 数、必填字段完整性、结尾钩子/下集提示是否存在
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

11. **系列大结局/最终集规则（重要）**
   - 大结局的 `## 下集提示` 应改为 `## 下集提示（系列完结提示）`，内容改为系列状态说明 + 读者寄语 + 下季预告（如有），而非制造新悬念
   - 大结局的 `## 本集结尾钩子` 的「钩子类型」改为"系列完结"，重点在于宣告伏笔回收而非制造新悬念
   - 写大结局前必须读取 `foreshadowing.md` 检查所有"未回收"条目，确保最终页逐条回收；在 `## 本集结尾钩子` 中明确标注每条伏笔的回收位置
   - 大结局建议结构：1页开场设定（天台/聚餐等温馨场景）→ 1页回忆蒙太奇（闪回回收伏笔）→ 2-3页当下剧情（角色弧线收束）→ 1页尾声+伏笔回扣。每页功能明确
   - 最终页必须包含一个"伏笔回扣"格：回到第一集的名场面/物件/台词，展示"变化"（如第一集的"三个月试用期"字条被划掉改为"续约通过"；第一集的草稿变成完成品）
   - 如果是连载系列（非彻底完结），最终页旁白应使用"故事才刚刚开始/未完待续"而非"全剧终"
   - 最终页最后一个 Panel 应使用横向大格，构图宽幅明亮，传达"生活继续"的温暖感
   - 大结局的 AI 提示词应避免灰暗/离别的负面情绪词，除非故事本身是悲剧结局

12. **完整项目生成验收（强制）**
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

13. **结构字段遗漏自检（2026-07-09 实测，强制）** — `write_file` 写入大章节正文（≥8KB）时，LLM 可能在正文末尾"忘记"结构字段：`<!-- ILLUST_N -->` 标记数量不足、`## 章末钩子` 段缺失、或结尾 `---` 分隔符被吞。这不是 `write_file` 的 bug（文件本身完整写入），而是 LLM 在长文本生成时注意力衰减导致的尾部遗漏——同样会发生在 main-session 直接生成（非 delegate_task 子任务）中。**强制做法**：每次 `write_file` 写入后立即在终端跑结构自检三件套：
   ```bash
   f="light_novel/lnXXX_章名.md"
   echo "ILLUST: $(grep -c '<!-- ILLUST_' "$f")"
   echo "HOOK:   $(grep -c '## 章末钩子' "$f")"
   echo "SEP:    $(grep -c '^---$' "$f")"
   ```
   三项任一不符预期（ILLUST <3 / HOOK !=1 / SEP 缺失）则用 `patch` 补齐——补 ILLUST 在最后一个情感/动作转折点后插入；补钩子段附 `---\n\n## 章末钩子\n<内容>` 追加到正文末。**不要等全部章节写完再统一检查**——长批次中越往后遗漏概率越高，逐章检查能定位到具体哪一章缺什么。2026-07-09《DemoProjectG》续写 9 章实测：ln011 首稿缺 ILLUST_4 和 `## 章末钩子`，逐章检查时当场捕获并 `patch` 修复。

14. **正文段级增补的"主题锚点"技巧（2026-07-09 实测）** — 当 body-only CJK 字数差 50-200 字时，用 `patch` 在章节中**已有的自然情感转折点**前后插入一段主题延续的段落，而非在章末硬凑。锚点选择：①角色内心独白段（如"他忽然想起一件事"）——在后面补 100-150 字的情感延伸；②环境描写段（如"窗外是夜景"）——补 80-120 字的感官/回忆细节；③角色沉默后——补 100 字的"她不说话但身体语言在说"的刻画。**禁止**在 `## 章末钩子` 之后增补（那不算 body）；**禁止**插入与本章主题无关的凑字段落——增补必须延续该段已有的情感方向。2026-07-09 实测 ln004/005/006 各 `patch` 一次即从 2455/2452/2489 增至 2621/2684/2817，全部一次过验证，无需整章重写。该技巧补充 note 8「字数经常单稿落在 2400-2500 之间」段的补救方法——之前只记录了"在对白前补心理/环境铺垫，或在对白后补余韵"，"主题锚点"是更具体的可操作版本。

15. **Cyrillic 污染在 main-session 直接生成中仍会发生（2026-07-09 确认）** — 已知 `scan_unicode_contamination.py` 覆盖 Cyrillic/Hebrew/Latin Extended 块越界（见 note「非 Latin Unicode 块越界」段 + `references/light-novel-garbled-text-cleanup.md` §5），但之前的实测记录全部来自 delegate_task 子任务输出。2026-07-09《DemoProjectG》ln010 续写实测：main-session 直接 `write_file` 生成的正文中也出现了 1 个 Cyrillic 词 `тариф`（混入中文叙述段中间），`validate_light_novel.py` 报 PASS、`scan_garbled()` 的 `[a-zA-Z]{3,}` 正则抓不到。**确认结论**：tokenizer 误输出相邻 script 字符的根因不分 main-session vs delegate_task——只要有中英文混生成场景就可能发生。**强制做法**：main-session 直接 `write_file` 写章节后，与 note「强制写入后自检 SOP」的五项 Python 自检同批执行 `re.findall(r'[\u0400-\u04ff]{2,}', t)` 扫描 Cyrillic 块；发现后用 `patch` 精确替换为正确中文。该扫描已包含在 `scripts/scan_unicode_contamination.py` 中，但手写五项自检脚本中也应加上这一行（不依赖外部脚本即可当场捕获）。

16. **始终加载 skill 后再写稿/写小说（强制）**
   - 只要涉及漫画脚本生成或轻小说生成（写稿、续写、修改、批量、前N章+设定交付），必须先通过 `skill_view(name='comic-script-generator')` 加载本 skill，再开始任何操作。
   - 即使项目已存在且之前的手动写稿未走 skill 流程，也要先加载 skill 读取注意事项和模板，不要跳过直接写。缺少加载步骤可能遗漏重要规则（如根级文件一致性维护、对白格式限制、写入路径限制）而导致交付物不合格。
   - 用户为单集提供的显式格式指令（如特定字段排列、气泡格式简化、AI 提示词格式）优先于 skill 的默认模板——记录用户指定的格式变化，但保留 skill 的必填字段完整性（格子/画面/构图/气泡/旁白/拟声/转场/AI提示词）
   - 同一项目不同集可能使用不同格式（表格 vs 多行字段），取决于用户当次指令；尊重当次指令，不需要强制跨集格式统一

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
- `references/online-reader-deployment.md` — 线上 Reader/API 部署记录：`<your-reader-domain>/reader` 与服务器 `/path/to/comic-script-generator-api`、Nginx、certbot 的关系，以及 Cloudflare/DNS-only 注意事项
- `references/batch-generation.md` — 批量生成架构设计与常见问题
- `references/panel-format-generation-lessons.md` — Page/Panel 漫画脚本生成实战经验：格式通过不等于故事连贯、先写 episode beats、保守提取伏笔、6 集连载递进链样例
- `references/light-novel-interrupted-session-continuation.md` — 逐章生成因"网络错误 cut off"框架级重启后的续写策略：先 `read_file` 全文确认文件状态；中段叙事已退化时整章 `write_file` 覆写优于 `patch` 续写（后者继承退化 tokenizer 状态）；只有尾部 `## 章末钩子` 缺失时用 `patch` 追加。含断点定位 SOP、整章覆写 vs patch 补救的决策树、强制自检清单。补充 SKILL.md 模式六 note 8 在"被系统打断重启"会话状态下的操作序列。
- `references/manga-rendering-lessons.md` — 漫画渲染与 Reader 前端实战经验：不要依赖生图模型生成中文文字；先出无字图再脚本叠加对白/拟声；少用旁白；重制连贯漫画时先写 page beats；Reader 点击图片应展示对应稿子用于对比
- `references/manga-generation-pipeline.md` — 本次“生成稿子→统一画风→多线程渲染→Reader 调试”的经验沉淀：生成阶段禁止抽象模板句、角色视觉指纹/一致性锁、中文对白后期叠加、`--workers 5` 并发渲染、加载更多与缩略图缓存修复。
- `references/logic-style-rendering-and-reader-debug.md` — 本次实战总结：生成阶段避免抽象模板画面、用角色视觉指纹/CONSISTENCY LOCK 提升画风统一、`render_images.py --workers 5` 并发渲染、Reader 加载更多与缩略图缓存修复。
- `references/generation-logic-and-style-consistency.md` — 生成阶段避免抽象模板镜头、确保图片符合正常漫画逻辑与统一画风的实战规则；包括 validate/export/style_guide 的修改要点。
- `references/full-manga-production.md` — 完整漫画一话生产经验：正式交付默认 8 页/48 Panel 而非 12 Panel 样片；`--workers 5` 并发渲染；内容策略误判时只用安全短 prompt 补失败镜头；Reader 加载更多游标与缩略图缓存失效修复。
- `references/market-manga-validation.md` — 市场向漫画验收标准与自动化报告模板
- `references/file-writing-and-fallback.md` — 文件写入实战经验：Shell heredoc 不可用于漫画脚本、`write_file` 实测 48KB 稳定、格式变体记录、AI 提示词格式差异、缺少流程步骤的教训

- `references/light-novel-delegate-batch-pattern.md` — 轻小说批量生成并发模式（跳过 batch_generate.py，直接用 delegate_task 每批 3 本驱动 40+ 本并行生产）；含失败恢复（HTTP 522 重新 dispatch）和交付后章节文件规范化步骤
- `references/light-novel-batch-generation.md` — 轻小说批量生成与 Reader 书架实战经验：不达标旧项目删除重建、每章 ≥2500 字验证、避免大块工具参数、用小脚本扩写现有章节、`/projects` 元数据按 `light_novel` 章数展示。2026-07-08 补充：§3 三口径验字脚本（纯汉字 / 汉字+中文标点 / 全非空白，三者差距可达 200-400 字/章，按纯 CJK ≥2600 为安全目标）、§1 交付"前 N 章加设定"可跳过 `init_project.py` 的直接落盘模式。
- `references/light-novel-single-batch-generation.md` — 轻小说单批生成模式：元数据集中 Python 脚本 + 章节逐文件 write_file、字数/格式自检命令、字段隔离规则（正文禁止漫画字段，元数据不受限）、单批项目验收清单、对白格式验证正则陷阱、字数统计口径差异、段级补足 loop。
- `references/light-novel-single-script-generation.md` — 轻小说全脚本单次落盘模式（模式三）：把元数据+全部章节正文塞进同一个 Python 脚本，用 write_file 写脚本 + 一次 terminal 执行，2 个工具调用覆盖 ≤6 文件。含脚本模板、内联验证段、三口径验字实测表、网络中断恢复方案。比 single-batch 的 1+N 模式更简洁，适合一次性完整生成场景。2026-07-08 续补**模式四（逐章生成器脚本）**：每章一个独立 gen_chN.py + 逐章 write_file/terminal 执行，适合 9+ 章、网络不稳定、需逐章验收的批量续写场景；含脚手架模板、中断韧性对比表、实测数据。2026-07-09 续补**「工具调用预算与模式选择」**：当 N≥6 章时强制评估逐章 write_file（3-7 调用/章）vs 模式三（2 调用）的总开销，含单章调用开销明细表、模式选择规则表、预判检查清单——避免因逐章自检循环累积调用而撞上会话工具调用上限之课（《DemoProjectD》9 章续写25 调用仅完成4章之课）。
- `references/write_file-paragraph-level-corruption.md` — 【新增 2026-07-08】`write_file` `content` 参数流式传输期间**段落级肌理损坏**——区别于已记录的字符级/整词级/单字级损坏，整段中文叙述/对话丧失可读性，现有正则和 Unicode 块扫描均不捕获。含预防 SOP（避免写入轮夹带长规划散文/整章 ≤4K CJK/分批写入）、恢复 SOP（确认落盘→整章 write_file 覆写→模式三降级→分批降级），以及对 note 17 七项自检的补充「通读首尾 200 行」。本类损坏级别最高，机械验证不能替代通读。
- `references/light-novel-garbled-text-cleanup.md` — 轻小说跨语言乱码污染检查与修复：扫描脚本（检测对话标记后缀残留/英文混入中文/乱码碎片/阿拉伯数字代中文数字）、`str.replace` 列表批量修复流程、生成阶段预防建议。`validate_light_novel.py` 不检测此类污染，必须在标准验证后追加扫描。
- `references/light-novel-heredoc-pitfall.md` — 轻小说正文写入路径：Shell heredoc（`python3 << PYEOF` + `r"""…"""`）会损坏中文正文（残留 `]='\\''`/`isVisible` 等碎片、`SyntaxError: unterminated triple-quoted string`）；首选 `write_file`，降级用独立 `.py` 文件；注入后必须扫描 heredoc 残留。
- `references/light-novel-quickstart-recipe.md` — 轻小说单项目快速生成实操食谱（"前N章+设定"从规划到验证的紧凑端到端流程，含字数不足时的整章重写策略表）。
- `references/patch-intext-pitfall.md` — `patch` 工具对中文长篇正文增补的三重陷阱：隐式误替换导致丢段、phantom 字符注入（`];`/`}`/`\\]='` 等）、连续 patch 状态脱节；完整安全 SOP（read → patch → read_validate → 自检 → phantom 扫描 → validate）。
- `references/reader-homepage-light-novel-ui.md` — Reader 前端首页/分类/书架与番茄小说式轻小说阅读模式的实现和调试经验；包含 `/light-novels` 接口、JS 语法检查、中文 URL 编码和首页结构规则。
- `references/reader-and-manga-logic.md` — Reader 前端调试、Service Worker/async/懒加载坑，以及“生成稿子阶段就必须产出具体可画连续漫画镜头”的经验归档
- `references/rendering-reader-lessons.md` — 本次完整调试沉淀：生成阶段避免抽象模板句、角色视觉指纹/风格锁、无字生图+叠字链路、`workers=5` 并发渲染参数、Reader 加载更多游标修复、Reader 显示名排查。
- `references/local-reader-api.md` — 本地 Reader/API 站点兜底实现记录：当独立前端项目缺失时，如何用 Python ThreadingHTTPServer 提供 `/reader`、`/projects`、完整正文、项目文档与图片画廊；包含浅色 UI、故事名目录命名和安全路径校验经验
- `references/light-novel-reader-debug.md` — 轻小说/番茄小说风 Reader 前端调试经验：`/light-novels` 接口、模式切换、番茄小说样式、JS 语法检查、插图占位符与中文 URL 编码坑。
- `references/novel-generation-and-bookshelf.md` — 轻小说生成与书架经验：原生小说项目结构、章节验证、`content_mode: light_novel` 元数据、Reader 首页/分类/书架要求。
- `references/long-novel-production-and-reader.md` — 本次小说路线升级经验：20万字长篇默认目标、分批生成+上下文压缩、长篇验证脚本、番茄小说书架首页，以及单文件 Reader JS 语法检查和大 payload 工具超时规避。
- `scripts/repair_manga_logic.py` — 将已生成但过于模板化的短篇漫画稿（如“异常事件突然出现/关键配角登场”）修复成具体可画的连续漫画动作镜头，再重导 `render_input`。适用于图片不符合正常漫画逻辑时的第一步修复。
- `scripts/export_for_render.py` — 从现有漫画稿提取 Panel 并转换为 story-renderer 输入脚本
- `references/light-novel-batch-continuation.md` — 轻小说批量续写模式六实战经验汇总
- `references/reader-route-ordering-and-by-update.md` — Reader 路由顺序陷阱（FastAPI `{name:path}` 吞掉 `by-update` 子路由）与线上 app.py vs skill reader_server.py 双实现注意事项；含 `/projects/by-update` 按 mtime 排序接口的完整实现、前端「最新」视图、部署验证三件套
- `references/reader-modal-vs-view.md` — Reader 单文件 SPA 的「模态框 vs 独立视图」选择规则：新功能默认走独立视图（`setNav` + `#main` 切换 + `window.scrollTo(0,0)`），不走路由级模态框；含从模态框迁移到独立视图的完整清理清单、HTML/JS/CSS 模板、移动端同步要点、线上+skill 模板双同步要求
- `references/reader-api-docs-self-describing.md` — 自描述 API 文档接口模式：`GET /api-docs?format=json|md` 让文档成为单一事实源；后端 `API_DOCS` 常量 + 前端动态 fetch 渲染，替代硬编码 HTML；含 `API_DOCS` 结构、Markdown 渲染函数、前端 `renderApiDocs` 模板、验证三件套、何时用何时不用的判断

## 脚本工具

- `references/long-novel-generation.md` — 长篇小说生成实战教训：20万字不能靠模板/补字数达标；必须分批生成、压缩上下文、检测重复段落和相邻章节相似度，失败样稿应删除或隔离。
- `scripts/export_light_novel.py` — 轻小说导出脚本，将 Page/Panel 稿子转为轻小说正文 + 关键场景渲染清单；每集只提取 5-8 张关键插图，大幅降低渲染成本
- `scripts/validate_light_novel.py` — 轻小说验证脚本，检查 H1 标题、正文长度、对白数量、插图标记、是否混入漫画分镜字段，并检测模板句、章节内重复段落、相邻章节相似度
- `scripts/verify_light_novel_delivery.py` — "前N章+设定"单批项目的投递级验证脚本，补 `validate_light_novel.py` 的盲区：①元数据文件（`characters.md` 角色数、`foreshadowing.md` 未回收条数、`summary.md` 关键字段命中，并提取 characters.md 的 `## Name` 规范化角色名）；②heredoc 残留扫描 + 严格对白正则 + 漫画字段污染一次性全扫；③ASCII-in-CJK 扫描（抓"队47人"阿拉伯数字混入中文叙述、"ProjectCode: jixia"英文标识符混入）；④**角色名漂移检测**（`--check-role-drift yes`，默认开）——扫描每章 `「...」——<name>` 归属行里是否有 characters.md 规范名的一字之差变体（如 柠/檬、冬青/檬），这是 LLM 多章生成时最高频、最隐蔽的污染类型，`validate_light_novel.py` 和 `scan_garbled()` 都检测不到。默认纯 CJK 口径 `--min-chars 2500`、`--min-roles 4`、`--min-threads 3`。推荐在 `validate_light_novel.py` 之后跑一遍作为"投递前最后一道闸"。详见 `references/light-novel-single-batch-generation.md` §角色名漂移陷阱 + §投递级验证脚本
- `scripts/update_long_novel_context.py` — 长篇小说上下文压缩脚本，自动生成 `long_novel_context/` 下的章节索引、全局摘要、最近5章连续性、角色状态和未回收伏笔，避免续写时加载20万字全文
- `scripts/validate_long_novel.py` — 长篇小说验收脚本，检查总字数（默认20万）、章节数、单章最低字数和压缩上下文文件是否齐全
- `scripts/init_project.py` — 项目初始化脚本，自动创建目录结构和配置文件
- `scripts/init_project.py` — 项目初始化脚本，自动创建目录结构和配置文件
- `scripts/update_project.py` — 自动更新项目文件，从分镜稿提取角色/伏笔/摘要并更新到对应文件
- `scripts/validate_episode.py` — 分集验证脚本，检查场景数、AI 提示词、伏笔一致性
- `scripts/consistency_check.py` — 角色一致性检查脚本，验证对话风格和外貌描述是否与档案一致
- `scripts/scan_unicode_contamination.py` — 轻小说正文 Unicode 块污染扫描：检测 Cyrillic/Hebrew/扩展 Latin 等非 CJK 块越界、Latin 借词混入中文、HTML 工件。补 `validate_light_novel.py` 和 `scan_garbled()` 的盲区（ASCII 正则抓不到 Cyrillic/Hebrew）。投递前最后一道闸，详见 `references/light-novel-garbled-text-cleanup.md` §5
- `scripts/check_update.py` — 更新检查脚本，检测远程仓库是否有新提交（网络不通时自动跳过）
- `scripts/privacy_check.py` — 发布/同步前隐私扫描脚本，检查真实 token、私有 IP/域名、本机路径和误放的 `config.json`
- `scripts/batch_generate.py` — 批量生成脚本，自动抓取热点并生成多个独立漫画项目
- `scripts/pregen_thumbs.py` — 批量预生成 WebP 缩略图到 `disk_cache/`，避免 `/thumb` 实时压缩
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

11. **批量脚本 LLM 调用失败时的兜底生成**
    - 如果 `batch_generate.py` 在“Generating outline/episodes”阶段因上游鉴权、403/503、provider auth、限流等问题失败，但当前 Hermes 会话仍可正常回复，不要把任务停在失败报告。
    - 兜底流程：由当前会话直接生成项目内容并写入磁盘：`config.json`、`style_guide.md`、`summary.md`、`characters.md`、`foreshadowing.md`、`episodes/ep001_*.md ...`。
    - 仍需遵守 Page/Panel 结构和必填字段：`格子`、`画面`、`构图`、`气泡`、`旁白`、`拟声`、`转场`、`AI 提示词`、`本集结尾钩子`、`下集提示`。
    - 完成后至少做基础验证：统计每个项目集数、每集 Page 数、Panel 数、必填字段是否存在，并在回复中报告 PASS/WARN。
    - 这个兜底是“继续完成用户要的稿子项目”，不是宣称批量脚本不可用；脚本环境恢复后仍优先使用脚本。
    - 详细兜底流程见 `references/batch-fallback-generation.md`。

## 脚本调试经验

### 气泡格式：update_project.py 的角色名解析规则必须遵守

**触发问题**：运行 `update_project.py` 后，`characters.md` 中出现"左格""右格""门内林默""王乐乐视频通话"等假角色名。

**根因**：`update_project.py` 用正则 `^\-\s+([^：:]+)[：:]` 解析气泡行 `- <角色名>："，把冒号前的所有文字当作角色名。

**必须遵守的格式规则**：

1. **布局注解不能放在角色名前**：
   - ❌ `- 左格：苏然："..."` → 解析出假角色"左格"
   - ❌ `- 中格：王乐乐："..."` → 解析出假角色"中格"
   - ✅ `- （左格）苏然："..."` → 正确解析为苏然
   - ✅ `- （中格）王乐乐："..."` → 正确解析为王乐乐

2. **场景/渠道标注不能拼接到角色名后**：
   - ❌ `- 王乐乐视频通话："..."` → 解析出假角色"王乐乐视频通话"
   - ❌ `- 门内林默："..."` → 解析出假角色"门内林默"
   - ❌ `- 画面外妈妈的语音："..."` → 解析出假角色"画面外妈妈的语音"
   - ✅ `- （视频通话）王乐乐："..."` → 正确解析为王乐乐
   - ✅ `- （门内）林默："..."` → 正确解析为林默
   - ✅ `- （画外音）妈妈："..."` → 正确解析为妈妈（如需新增角色）

3. **角色行为描述放在括号里，跟在角色名后**：
   - ✅ `- 王乐乐（咽下去）："真的！"` → 正确解析为王乐乐
   - ✅ `- 苏然（内心独白）："……"` → 正确解析为苏然

**经验法则**：`- ` 之后第一个连续的文本块（直到第一个不可见字符或 `（`）必须是真实角色名。所有布局、渠道、场景注解必须用 `（...）` 包裹，且要么跟在角色名后，要么放在角色名前但由括号包裹。

### terminal() workdir 工具的中文路径限制

- `terminal()` 的 `workdir` 参数**不兼容含中文的路径**（如 `DemoProjectA`），会报错 "Blocked: workdir contains disallowed character"。
- **解决方案**：不在 `workdir` 参数传含中文路径，改为在 `command` 中用 `cd <路径>` 进入目录。
- 示例：
  ```bash
  # ❌ 会失败
  terminal(command="python3 script.py", workdir="/projects/DemoProjectA")
  
  # ✅ 正确
  terminal(command="cd /projects/DemoProjectA && python3 script.py")
  ```

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
- `scripts/render_images.py`：调用配置的 OpenAI-compatible 生图接口，将 render 输入稿中的提示词渲染成图片
- 生图配置必须保存在本地私有文件中，优先使用 `COMIC_IMAGE_CONFIG` 或 `~/.config/comic-script-generator/image_config.json`（权限建议 `600`）；skill 目录只允许保留 `config.example.json` 示例，禁止把真实 API token、私有域名、服务器 IP、VPN/代理信息写入 SKILL.md、README、references 或任何可提交文件。
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
- **Reader 新功能用独立视图，不用模态框（2026-07-19 新增）**：在 Reader 单文件 SPA 里新增"功能入口"（API 文档、统计页、设置页等），默认走独立视图——切换 `#main` 内容 + `setNav()` 高亮 + `window.scrollTo(0,0)`，与 showHome/showRank/showRecent 一致。**不要**用 `position:fixed` 模态框 + mask 弹层，除非是短小确认/输入。详细实现模板与迁移清理清单见 `references/reader-modal-vs-view.md`。
- **API 文档走自描述接口，不硬编码 HTML（2026-07-19 新增）**：当用户要求"提供接口文档"或"在前端展示接口文档"时，**不要**把接口列表硬编码进前端 HTML——改为后端定义 `API_DOCS` 常量（dict），暴露 `GET /api-docs?format=json|md` 接口，前端 `showApiDoc()` 异步 fetch 后渲染。加新接口只改后端常量一处；`/api-docs` 自己也写进文档列表形成自描述。详细实现模板、`API_DOCS` 结构、Markdown 渲染函数、验证三件套见 `references/reader-api-docs-self-describing.md`。用户原话"你要有一个接口时获取接口文档内容的"明确记录了这条偏好。**补充（同日实测）**：当用户因接口 404/用法困惑发问时（如把 `/file?project=&path=` 误写成 `/files/{name}`），除了在对话里解答，还要把该易混点写进 `API_DOCS` 的 `note` 字段和 `guides` 数组（"常见错误 URL" 对照表、returns 结构示例、N+1 调用指南），让文档本身防呆——用户原话"你要在接口文档中详细说明，特别是获取文章内容这一块"。
- **双副本同步**：修改 skill 文件后必须同时更新 Desktop 开发副本和 AppData 已安装副本。默认只做本地同步和验证；**禁止自动 commit/push**，只有当用户明确说“commit”或“push”时才执行对应 Git 操作。**更新 skill 后立即向用户确认状态**：「已更新本地，未 commit/push」——不要等用户问"你没推送吧"。2026-07-19 实测：用户在我更新完 SKILL.md 和 templates/ 后主动追问"我还没说推送呢"，说明即使 skill 里有这条规则，也必须在动手后口头确认未推送，不能默默更新完就停。
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
- 渲染所需 API token/endpoint 必须来自本地私有配置：`--config`、`COMIC_IMAGE_CONFIG` 或 `~/.config/comic-script-generator/image_config.json`；禁止放入 skill 目录真实配置。
- 如果 story-renderer 未初始化，引导用户先运行“初始化 story-renderer”

### 出图路线选择

在启动渲染流程前，先判断故事类型：
- **对话密集/日常/情感类** → 推荐模式六（轻小说 + 关键场景插图），每集 5-8 张图，成本约 1/8。
- **动作/视觉驱动类** → 走本模式五完整漫画渲染。


## 市场向漫画验收标准

### 评分表（100 分）

| 维度 | 分值 |
|---|---:|
| 题材大众性 | 10 |
| 开场钩子 | 15 |
| 角色辨识度 | 10 |
| 剧情连贯性 | 15 |
| 镜头与分镜 | 10 |
| 对白可读性 | 10 |
| 页布局/条漫节奏 | 10 |
| 画面风格统一 | 8 |
| 情绪点/爽点 | 7 |
| 商业可读性 | 5 |

**通过线：**
- **85 分以上**：可进入大众市场测试/小规模投放。
- **75–84 分**：可发布但需优化节奏、钩子或角色。
- **60–74 分**：仅算完成稿，商业可读性不足。
- **60 分以下**：不建议作为正式漫画项目交付。

### 硬性检查项

1. **格式完整性**：每集必须具备 `Page → Panel` 结构，每个 Panel 必须包含：格子、画面、构图、气泡、旁白、拟声、转场、AI 提示词。没有气泡/旁白/拟声时必须写“无”。
2. **大众题材检查**：一句话能说清故事卖点；主类型明确；目标读者明确。
3. **开场钩子检查**：前 3 页或前 10 个 Panel 内必须出现至少一个危机/目标/悬念。
4. **单气泡长度**：建议 20-35 字，超过 50 字需提醒台词过长。
5. **页布局检查**：每页建议 3-7 个 Panel，超过 8 个需提醒页面可能过密。
6. **结尾钩子**：每集必须包含 `## 本集结尾钩子` 与 `## 下集提示`。

### 自动化验收脚本输出模板

每个项目应输出 `market_validation_report.json`：

```json
{
  "project": "项目名",
  "market_score": 96,
  "level": "通过",
  "checks": {
    "panels": 12,
    "images": 12,
    "comic_pages": 2,
    "localized_long_image": 1,
    "no_narration_default": true
  },
  "market_notes": [
    "开场3格内有异常钩子",
    "12格短篇结构完整",
    "对白较短，适合移动端阅读",
    "仍建议后续人工优化角色连续一致性"
  ]
}
```

## 漫画页优先规则（强制）

- 正式漫画项目必须先写每页 Page Beat：本页目标、情绪变化、视觉焦点、翻页钩子，再展开 Panel；禁止直接堆 40+ 个独立 Panel。
- 每页建议 5-7 个 Panel，并使用动态版式：横向开场/环境大格、反应小格、物件特写、竖向张力格、半页高潮或横向钩子格。
- `compose_manga_pages.py` 必须按动态漫画版式合成页面，不能使用固定 2×3 网格；固定网格只允许作为调试兜底。
- 如果用户说“不像漫画”，优先检查：页级节奏、版式、气泡位置、角色一致性，而不是只重跑生图。

## 完整漫画项目交付流水线

### 5. 非 Latin Unicode 块越界（Cyrillic / Hebrew / 扩展 Latin）

2026-07-08 实测《网游废柴逆袭记》前3章首稿出现，**bundled `validate_light_novel.py` 全部通过但人眼读卡壳**。本类污染**完全绕过** `scan_garbled()` 中的 `[a-zA-Z]{3,}` 正则——该正则只覆盖 ASCII Latin，Cyrillic / Hebrew 等块被当作"汉字外字符"忽略。

| 实际输出 | 应为 | 块 |
|---|---|---|
| `门`о`то外面走廊` | `门外走廊` | Cyrillic |
| `第三个ǣ是林昭` | `第三个是林昭` | Latin Extended (U+01E3) |
| `盯着自`֒`己看` | `盯着自己看` | Hebrew U+05BA (combining) |
| `<table end>` 自插 HTML | （删除） | HTML artifact |
| `就call一张画面` | `就调一张画面` | 拉丁借词混入（边界） |

**特征**：每个字符看上去还是"汉字"，但 CJK 句子中混入了 1-2 个相邻 Unicode 块的字符（多为 tokenizer/解码错误或 LLM 模式切换残留）。眼睛一扫还是会卡住。

**根因**：LLM 中英文混生成时 tokenizer 可能误输出相邻 script 的字符，而后端去重检查常只针对 ASCII Latin。

**修复**：单字符/单短语级别的，用 `patch` 工具精确替换；HTML 工件 `<table end>` 直接删除。修复后再扫一遍直到 `scan_unicode_contamination.py` 返回 0。

### 验证阶段

`validate_light_novel.py` 已有的检查（H1、字数、对白、插图、漫画字段）**不够**——它不检测英文混入、乱码碎片、Unicode 块越界、HTML 工件中的任何一类。必须在标准验证后追加扫描：
1. `scripts/scan_unicode_contamination.py`（覆盖 Unicode 块越界 + Latin 借词混入 + HTML 工件，推荐投递前最后一道闸）
2. 本文件中的 `scan_garbled()`（覆盖对话标记后缀/阿拉伯数字代中文数字，可与上一条顺序跑或合并）

两个脚本尚未集成为 `validate_light_novel.py` 的内置检查项（未来可集成）。
1. `scripts/scan_unicode_contamination.py`（覆盖 Unicode 块越界 + Latin 借词混入 + HTML 工件，推荐投递前最后一道闸）
2. 本文件中的 `scan_garbled()`（覆盖对话标记后缀/阿拉伯数字代中文数字，可与上一条顺序跑或合并）

两个脚本尚未集成为 `validate_light_novel.py` 的内置检查项（未来可集成）。
脚本生成/导入
→ export_for_render.py 导出渲染输入
→ render_images.py 并发生图（全局并发 3，单图最多重试 2 次）
→ overlay_comic_text.py 叠加中文对白气泡
→ compose_manga_pages.py 合成漫画页（必须使用动态漫画版式：横向开场大格、反应小格、竖向张力格、横向收束/钩子格；禁止回退到固定 2×3 插画网格）
→ stitch_localized_chapter.py 拼接完整汉化长图
→ 生成 market_validation_report.json
→ Reader 展示验证
```

### 断点续传策略

- 按 `project → episode → page → panel → raw_image → overlay_image → composed_page` 粒度记录状态
- 缺图不要阻塞整个项目，可先用占位图进入后续合成
- 最终验收再统一补齐缺图
- 只补失败 Panel，不需要重跑整集或整项目

### API 性能基线

- 当前生图接口 `/v1/images/generations` 实测单张耗时 **120-155 秒**（含 30 秒连接超时），返回格式为包含 `data[].url` 的 JSON（非 b64_json），脚本会自动从 URL 下载图片。
- `/v1/models` 返回 200（确认服务在运行），但 `/v1/images/generations` POST 请求可能因后排排队而极慢。这是代理型生图 API 的典型特征，不是本技能的问题。

### 重试策略

- **API 性能基线**：当前生图接口 `/v1/images/generations` 实测单张耗时 120-155 秒（含 30 秒连接超时），返回格式为包含 `data[].url` 的 JSON（非 b64_json），脚本会自动从 URL 下载图片。
- `render_images.py` 并发建议：当前图片接口已验证 `--workers 5 --retries 2 --sleep 0.2` 可稳定完成 12 张短篇漫画渲染；默认优先用 5 并发，若出现 429/401/5xx 再降到 3 或补单张。

- `render_images.py` 并发建议：当前图片接口已验证 `--workers 5 --retries 2 --sleep 0.2` 可稳定完成 12 张短篇漫画渲染；默认优先用 5 并发，若出现 429/401/5xx 再降到 3 或补单张。
- **`--limit` 默认值为 1**（安全控制），每次运行只渲染 1 张图。要渲染全部必须显式传 `--limit 999` 或 `--limit 0`（无限制）。
- **`--output-dir` 行为**：不指定 `--output-dir` 时，输出到 `<项目>/rendered/<prompt_file_stem>/`（每集独立子目录，不会覆盖）；指定 `--output-dir` 指向同一目录时，多集渲染会互相覆盖（`scene_001.png` 等文件名相同）。推荐做法：不传 `--output-dir`，让脚本自动创建每集独立目录。
- 第 1 次失败：等待 15-30 秒
- 第 2 次失败：等待 60 秒
- 第 3 次失败：等待 120 秒
- 仍失败：标记 missing_image，进入补图队列

### Reader 展示验证

- 列表页：`/projects`
- 详情页：`/projects/{项目名}`
- 文件访问：`/file?project=...&path=...`
- 分集正文：`/episode?project=...&file=...`
- 点击图片：页面下方显示“图片对照稿”区域，包含图片预览、路径、对应分集文件和完整稿子内容

## 多 agent 批量生产模式

当用户要求批量生产 5+ 个漫画项目时：

1. **并行分析**：同时启动多个子 agent 分别负责市场标准、项目方案、生产流程建议
2. **独立项目生成**：每个项目完全独立，不保留 LLM 上下文
3. **统一验证**：所有项目完成后统一运行市场验证脚本
4. **前端接入**：确保所有项目可通过 Reader 访问

**注意**：子代理模型不可在选择时指定；子代理继承父模型/系统配置。如需特定模型，需在父会话中先切换。

**关键陷阱：子 agent 文件路径** — 向子 agent 委托文件读取任务时，必须在 context 中给出**绝对路径**（如 `/root/comic-projects/projects/某项目/light_novel/ln009_第九章.md`），否则子 agent 可能因路径模糊搜索不到文件。详见 `references/light-novel-delegate-batch-pattern.md` §关键陷阱。

### 委托子任务（delegate_task）生成分镜稿的格式瓶颈（重要）

子任务（leaf agent）生成的漫画脚本**极容易使用错误格式**——目前观察到的错误格式包括：
- **表格格式**：`| 字段 | 内容 |`（三天内 3 次子任务独立复现此问题）
- **YAML/列表格式**：`- **字段**：值`（使用减号缩进+斜体字段名）

**后果**：这些格式无法通过 `validate_episode.py` 验证，也无法被 `update_project.py` 正确解析（0 dialogues / ✗ AI prompts），产生假角色名污染 `characters.md`。

**必须的应对策略**：

1. **首次委托时，提供精确到字符的格式模板**（不仅仅是描述），模板中完整包含 `## Page N` → `### Panel N` → `**格子**：` 等字段。
2. **明确禁止格式**：在 context 中写"禁止使用表格格式 `| 字段 | 内容 |`"和"禁止使用 YAML 列表 `- **字段**：`"
3. **设定最低 Panel 数**：模式 B 的 `validate_episode.py` 最低要求 **40 个 Panel**（非 50）。在 context 中写"每集至少 8 页 40 个 Panel"
4. **两次失败后不再重试子任务**：如果一个子任务连续两次生成错误格式，**不要第三次委托**——改为当前会话直接写该集稿子。转换成本低于兜底修复。
5. **立即验证**：子任务完成后，立即用 `grep "^### Panel"` 和 `grep "^\*\*格子\*\*"` 检查格式是否正确。如果 0 匹配，说明格式错误，立即进入直接写入模式。

## 部署与访问说明

### Reader 服务器（内置）

skill 内置了独立的 Reader API 服务器，用于浏览和阅读项目：

- **服务器脚本**：`scripts/reader_server.py`（FastAPI + uvicorn）
- **前端页面**：`templates/reader.html`（番茄小说风格单页 SPA）
- **配置方式**（环境变量）：
  | 变量 | 默认值 | 说明 |
  |------|--------|------|
  | `COMIC_PROJECTS_ROOT` | `~/comic-projects/projects` | 项目根目录 |
  | `COMIC_READER_PORT` | `8081` | 服务器端口 |
  | `COMIC_READER_API_KEY` | 空（不启用） | 可选 API 认证密钥 |

- **启动命令**：
  ```bash
  cd /path/to/skill && pip install fastapi uvicorn aiofiles Pillow
  COMIC_PROJECTS_ROOT=~/comic-projects/projects COMIC_READER_PORT=8081 uvicorn scripts.reader_server:app --host 0.0.0.0 --port 8081
  ```
- **路由**：
  - `/` — Reader 前端页面
  - `/projects` — 项目列表 API
  - `/projects/{name}` / `/project/{name}` — 项目详情
  - `/episode?project=&file=` — 分集正文
  - `/doc?project=&file=` — 项目文档
  - `/file?project=&path=` — 原图/文件
  - `/thumb?project=&path=&width=&height=&fit=` — 动态缩略图
  - `/light-novels?project=` — 轻小说章节列表
  - `/scripts?project=` — 短剧分镜脚本列表
  - `/script?project=&file=` — 单篇脚本内容
  - `/health` — 健康检查

- **路由顺序警告（2026-07-19 新增）**：FastAPI 按注册顺序匹配，`/projects/{name:path}` 会吞掉 `/projects/by-update`、`/projects/featured` 等具体子路径。**新增子路由必须放在 `{name:path}` 之前**。旧版 `app.py` 同理，`u.path.startswith('/projects/')` 兜底必须先让位给 `u.path == '/projects/by-update'` 这类精确匹配。详见 `references/reader-route-ordering-and-by-update.md`。
- **线上 vs skill 双实现警告（2026-07-19 新增）**：当前 `http://<IP>:8081` 跑的是 `<reader-deploy-dir>/app.py`（ThreadingHTTPServer 旧版，16KB），**不是** skill 的 `scripts/reader_server.py`（FastAPI 新版，24KB）。两份框架不同、路由写法不同，改接口前先 `ss -tlnp | grep 8081` + `cat /proc/<PID>/cmdline` 确认线上在跑哪份，再决定改哪个文件。长期建议迁移到 FastAPI 版本统一维护。

### 线上 Reader/API

- 站点域名：`comic-script-generator.YOUR_DOMAIN`
- Reader 页面路由：`/reader`（不是 `/reader.html`）
- 根路径 `/` 也会返回 Reader 页面
- API 统一通过 Nginx 反代到 `127.0.0.1:8081`
- 认证方式：请求参数 `api_key=<KEY>` 或请求头 `X-API-Key`
- 前端登录逻辑：调用 `/projects?api_key=...`，若返回 401 则提示“密钥无效”
- **注意**：直接访问 IP 或省略 `Host: comic-script-generator.YOUR_DOMAIN` 请求头时，Nginx default site 可能返回 404。浏览器正常访问域名通常没问题；如遇 404，优先检查 Cloudflare SSL 模式与 Nginx `server_name` 匹配。

### 备案限制下的访问方式

- 若域名未完成 ICP 备案，**不要继续配置 HTTPS 或域名白名单**。
- 此时应直接使用 `http://<服务器公网IP>:8081/reader` 访问。
- 用户若提供二级域名，也要先确认备案状态；未备案前只能用 IP+端口。

### 后端兼容路由

- `reader_server.py` 中除 `/projects/{name}` 外，还兼容 `/project/{name}`（`project_detail_alias` 函数），避免前端或其他调用方按单数形式访问时 404。
- `/light-novels?project=<name>` — 列出项目的轻小说文件（`light_novel/ln*.md`），返回标题、字符数、访问URL。详情见 `references/novel-reader-deployment.md`。

### 前端双模式阅读

Reader 支持「漫画」「轻小说」两种阅读模式切换，通过 Header 上的 `mode-toggle` 按钮切换：
- **漫画模式**：分集列表 + 渲染图库 + 漫画页 + 对照稿（原有功能）
- **轻小说模式**：章节列表 + 番茄小说风格正文阅读 + 嵌入插图 + 字号调节 + 阅读进度条

轻小说文件通过 `export_light_novel.py` 脚本生成，详见 `references/novel-reader-deployment.md`。

### 前端漫画化验收注意

- 用户对“像手绘漫画”的核心要求：分镜连贯、少旁白、主要靠对白气泡和拟声推进、优先生成完整汉化长图/漫画页。
- 若生成图片仍不符合正常漫画逻辑，应回头检查 `render_input` 的镜头描述、画面说明和 AI 提示词，而不是只重跑生图。
- 验收顺序建议：先看 `render_input` 稿子逻辑 → 再看单张图 → 再看漫画页 → 再看长图。

### Reader 静态服务与缩略图

**推荐方案**：使用 `scripts/reader_server.py`（FastAPI + uvicorn），详见上方「Reader 服务器（内置）」节。

**备用方案**（旧版 `app.py` / ThreadingHTTPServer，仅保留兼容）：
  - `/reader`：完整前端页面
  - `/projects`：项目列表
  - `/projects/<name>` 与 `/project/<name>`：项目详情
  - `/file?project=...&path=...`：原图/文档访问
  - `/thumb?project=...&path=...&width=...&height=...&fit=cover|inside`：Pillow 动态缩略图，输出 JPEG，质量 78，支持 cover/inside，默认缓存 1 天
- 详细静态服务实现见 `references/local-reader-api.md`
- 前端懒加载、分页、IndexedDB、Web Worker 优化记录见 `references/frontend-optimization.md`

### Reader 前端调试与稳定性经验

- **图片不显示的常见根因**：`innerHTML` 整体替换内容区后，旧的 `IntersectionObserver` 仍观察旧元素；新插入的 `.lazy-img` 永远不会被观察。修复：每次 `bindImages()` 前断开旧 observer，重建并重新 observe 新图片。
- **Service Worker 导致持续 404**：即使后端已修好，SW 可能还在分发旧缓存。调试阶段在前端加入主动 unregister 逻辑：`navigator.serviceWorker.getRegistrations().then(regs => regs.forEach(r => r.unregister()))`。
- **async/await 语法错误**：在非 async 函数体里写 `await` 会直接报语法错，且通常没有任何运行时日志。确保所有调用了 `await api(...)` 的函数都声明为 `async function`。
- **最稳前端架构**：单文件 SPA 优先用内联事件、`data-*` 属性、IntersectionObserver；复杂 Web Worker/IndexedDB 在单 HTML 中容易触发隐藏语法错误，保守回退更稳。
- **复制按钮陷阱（2026-07-20 实测）**：`navigator.clipboard.writeText()` 在 HTTP（非 HTTPS）环境下静默失败，用户点击无响应且不报错。**强制修复方案**：改用 `document.execCommand('copy')` 回退方案——创建临时 `<textarea>`，设 `position:fixed;left:-9999px`，`value=t`，`select()` 后 `execCommand('copy')`，再 `removeChild()`。该方法兼容 HTTP 和 HTTPS。详见 reader.html 中的 `copyText()` 函数。
- **图片加载兜底**：缩略图优先走 `/thumb`，但调试时可先回退到 `/file` 直接发原图，确认链路通后再加上缩略图参数。
- **番茄小说网风格要点**：浅色背景、顶部搜索、左侧项目卡片、右侧内容区、统计卡片、分集列表、图片画廊、对照稿、正文阅读分区；主题色用番茄红渐变按钮。

## Reader 加速栈

详见 `references/frontend-optimization.md`。当前 Reader 加速栈：
- 后端 `/thumb` 支持 AVIF/WebP/JPEG 内容协商 + `disk_cache/` 静态命中
- 前端懒加载：`IntersectionObserver` + skeleton shimmer
- 分批加载：渲染图按 12 张/批“加载更多”
- Service Worker：`reader.html` 用 `NetworkFirst`，API 用 `StaleWhileRevalidate`
- 前端 JS 保守化：去掉复杂 Web Worker/IndexedDB，保留可稳定运行的最小加速集
- 项目列表、分集列表、漫画列表、热点记录、搜索结果分页（默认 20 条/页）
- 图片懒加载（`loading="lazy"` + IntersectionObserver）
- 搜索结果上下文限制（`max-height: 200px` 滚动）
- 后端 `/projects`、`/projects/<name>/episodes`、`/comics`、`/hotspots`、`/search` 支持 `page`/`page_size`，返回 `count`/`page`/`page_size`/`total_pages`

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

### 从漫画稿转小说（兼容分支）

如果项目已经有 Page/Panel 漫画稿，可以使用：

```bash
python scripts/export_light_novel.py episodes/epXXX_xxx.md --project-dir projects/<项目名> --illustrations 7
```

这个分支只用于“已有漫画稿转轻小说”，不应替代原生小说生成流程。

## 模式七：短剧分镜脚本（Novel → Short Drama Storyboard）

**触发条件**：用户要求将已有小说章节转化为短剧分镜脚本，或要求"分镜脚本""拍摄脚本""短剧格式""△剧本"。

**核心定位**：模式七不是漫画 Page/Panel，也不是文字小说——它是**短视频/短剧的拍摄脚本**格式，以"场 → 镜头"为单位。完整工作流参考 `references/novel-to-drama-workflow.md`。

### 5 阶段工作流

每阶段有独立输出文件，用户确认后进入下一阶段。

#### 阶段 1：事件提取 → novel_events/events_XXX.md

从小说章提取事件图谱，每事件含冲突类型、情绪值（1-10）、是否主线、关键对白（原文逐字）：

```markdown
# 第X章 事件图谱

| 序号 | 事件 | 冲突 | 情绪值 | 是否主线 | 关键对白/动作 |
|------|------|------|--------|----------|--------------|
| E01 | 收到匿名信 | 外部冲突 | 7/10 | 是 | 「这是第三封了。」 |
| E02 | 决定调查 | 内心冲突 | 5/10 | 是 | 打开电脑搜索 |
```

- 每章至少 5-10 个事件，按时间排序
- 关键对白必须原文逐字，不得缩写
- 标注冲突类型（外部/内心/人际/社会）供改编决策

#### 阶段 2：改编策略 → adaptation_strategy.md

基于事件图谱做改编决策，先输出分集大纲给用户确认：

```markdown
# 改编策略

- **卖点锁定**：一句话卖点 + 核心爽点 + 目标观众
- **素材清单**：每章事件保留/删减/合并决策表，附决策理由
- **爆点分布**：每集黄金三秒 + 情绪拉扯 + 阶段打脸 + 结尾留钩
- **删减原则**：删支线、合并低情绪事件（≤4）、保留冲突事件（≥7）、保留关键对白
- **投流爆点约束**：第1集开头3秒必须有强冲突/强反差/强悬念
- **视觉风格**：写实/动画/水墨等（固定到 style_guide.md，由风格前缀统一）
```

#### 阶段 3：△ 镜头制剧本 → drama_scripts/epXXX_剧本.md

```markdown
第X集
X-X 夜 内 场景名
道具：麦克风、调音台、耳机
出场人物：主持人、同事

△ 【空镜】城市夜景航拍，万家灯火
△ 推镜头从窗外夜景缓缓推进，透过玻璃进入电台直播间
△ 中景：主持人坐麦克风前，头戴耳机，面带温暖微笑
主持人（温和轻柔）：各位听众，晚上好。
△ 特写：调音台指示灯闪烁
△ 切至办公室，灯光昏暗
```

**△ 剧本格式规则**（参考 Toonflow/Seedance2）：
- 每镜以 `△ ` 开头，后接景别+运镜+画面描述
- 首行格式：`X-X 昼/夜 内/外 场景名`
- 道具和出场人物独立列出
- 对白格式：`角色名（情绪）：对白`
- 特殊标注：`【字幕：文字】`、`【空镜】`、`【闪回】`/`【闪回结束】`
- 运镜必须具体：推/拉/摇/移/跟/环绕/升降 + 景别（远景/全景/中景/近景/特写）
- 每集结尾必须有钩子（未解决动作/暗示/悬念画面）

#### 阶段 4：资产清单 → assets.md

```markdown
# 资产清单

## 统一风格前缀
```
[从 style_guide.md 读取固定风格，如：电影级写实风格，城市夜景，暖色调灯光]
```

## 角色 (C01-C99)
### C01 — 主持人·正面全身
> **提示词**：风格前缀，30岁男性，178cm，偏瘦，黑框眼镜，深蓝衬衫，休闲西装，黑色长裤，棕色皮鞋，全身站立正面，纯白背景，表情中性

### C02 — 主持人·播音姿态
> **提示词**：风格前缀，30岁男性，戴耳机坐麦克风前，手指触调音台，专注温柔表情，半身近景

## 场景 (S01-S99)
### S01 — 电台直播间
> **正打**：风格前缀，专业电台直播间，调音台灯光闪烁，窗外城市夜景，暖光，无人
> **反打**：风格前缀，从麦克风角度看向座位，监听耳机，调音台面板，暖光，无人

## 道具 (P01-P99)
### P01 — 匿名信封
> **提示词**：风格前缀，暗红色信封，无邮票地址，中央手写「林」字，纯白背景
```

**资产生成规则**（来自 Seedance2）：
1. 角色 C01-C99：每人多角度（正面全身 + 特定动作/表情/姿态）
2. 场景 S01-S99：每场景正打/反打/侧面全景，画面中不得出现人物
3. 道具 P01-P99：纯白背景，单独展示
4. 风格前缀从 `style_guide.md` 固定读取，禁止临时拼凑
5. 角色提示词必须含身高/体型/年龄/服装/鞋子，不拿任何东西，表情中性

#### 阶段 5：分镜脚本 → storyboard/sbXXX_分镜.md（核心交付物）

两种格式二选一：

**格式 A：通用分镜表**

```markdown
| 镜号 | 时长 | 景别+运镜 | 画面 | 台词/VO | 音效 | @资产 |
|------|------|-----------|------|---------|------|-------|
| 1 | 0-3s | 远景推 | 城市夜景航拍，电台塔顶红灯闪烁 | 无 | 城市环境音 | S01 |
| 2 | 3-6s | 中景跟 | 主持人坐麦克风前，微笑，调整耳机 | 主持人：「各位听众，晚上好。」 | 播音室回音 | C02 |
| 3 | 6-9s | 特写固定 | 主持人嘴唇靠近麦克风，眼神温柔 | 主持人：「欢迎收听《深夜电台》。」 | 人声干净 | C02 |
| 4 | 9-12s | 中景拉远 | 主持人站起，摘下耳机，神情疲惫 | 无 | 椅子移动声 | C01 |
| 5 | 12-15s | 特写固定 | 桌上暗红色信封，手写「林」字 | 主持人（独白）：「又是这个字迹……」 | 悬疑音效，心跳声 | P01 |
```

**格式 B：Seedance 2.0 时间轴格式**

```markdown
## Seedance Prompt

[统一风格前缀]

0-3s: 推镜头从@图片1城市夜景推进，透过玻璃窗进入电台直播间，展示温暖的灯光和专业的播音设备，窗外万家灯火闪烁。

3-6s: 画面中出现@图片2主持人，坐在麦克风前，面带温暖微笑，手指轻推调音台推子，耳机微调。主持人开口说话。

6-9s: 特写主持人的嘴唇和眼神，镜头缓慢推近，展现他温柔而略带疲惫的神情。

9-12s: 切至办公室，@图片3暗红色信封出现在台灯光晕中央，镜头缓慢推近信封，突显其神秘感。

12-15s: 特写信封上手写的「林」字，灯光在信封上投下阴影，环境音逐渐消失，只留下心跳声。定格。

音效设计：
- 开场：城市环境音，远处车流，电台信号杂音
- 中段：播音室干净人声
- 结尾：环境音渐消，悬疑氛围音效，心跳声
```

**尾帧描述**（每集必备）：
```markdown
## 尾帧描述

**场景**：办公室，昏暗台灯下，暗红色信封平放在桌上。
**画面**：
- 主体：暗红色信封，手写「林」字
- 背景：模糊办公桌，台灯光晕
- 光线：圆锥形台灯，信封在光晕中央
- 构图：信封居中，周围黑暗
- 氛围：悬疑，安静

**用途**：作为下集开场（第2集从信封内容展开）
```

### 分镜核心铁律

以 Toonflow 为准，以下规则必须严格遵守：

1. **台词零删改逐字搬运** — 原文对白不得缩写/改写/合并
2. **长台词>20字强制拆镜换景别** — 中景→近景→特写，避免单一镜头过长
3. **4字/秒，单片段≤15秒** — 15秒标准集建议5-8个镜头
4. **出场人物不消失** — 角色退场必须有明确动作（离开/转身/倒下）
5. **外观不进提示词** — 画面描述只写动作/表情/状态，外观已在C01中定义
6. **声音只写环境音+音效，禁BGM** — 允许：脚步声、心跳声、风声、门声、城市环境音
7. **过渡三桥梁** — 动作桥梁（关门/开门）、情绪接力（愤怒→爆发）、空间视线链接（看窗外→窗外景）
8. **尾帧衔接** — 每集末附「尾帧描述」，下集首镜必须承接尾帧
9. **字段隔离** — 分镜文件和△剧本中禁止漫画字段：`**格子**`、`**构图**`、`### Panel`、`## Page`、气泡/旁白/拟声
10. **写入禁 heredoc** — 用 `write_file` 或 Python 脚本写入，写入后验证结构完整性

### 项目目录结构

```text
projects/<小说名>/
├── config.json                 # content_mode: mixed 表示多模式
├── style_guide.md              # 风格前缀（影视分镜用）
├── light_novel/                # 源小说章节（ln001_章名.md）
├── novel_events/               # 阶段1：事件图谱（events_001.md）
├── adaptation_strategy.md      # 阶段2：改编策略
├── drama_scripts/              # 阶段3：△ 剧本（ep001_剧本.md）
├── assets.md                   # 阶段4：资产清单（C/S/P 编码）
├── storyboard/                 # 阶段5：分镜脚本（sb001_分镜.md，核心交付）
└── scripts/                    # 简版快速脚本（sd001_章名.md）
```

### 快速直转模式（跳过阶段 1-4）

**关键陷阱：子 agent 文件路径** — 第3方委托生成脚本时，必须在 context 中给出**绝对路径**（如 `<projects-dir>/某项目/light_novel/ln009_第九章.md`），否则子 agent 可能因路径模糊搜索不到文件。2026-07-20 实测：子 agent 用 `ln009_第九章.md`（无目录前缀）搜索失败，改为绝对路径后立即成功。参见 `references/light-novel-delegate-batch-pattern.md` §关键陷阱。

**关键规则：风格前缀** — 每个分镜脚本文件顶部都必须包含 `**统一风格**：` 行（如 `电影级写实风格，城市夜景，暖色调灯光`）。风格前缀从 `style_guide.md` 或用户指令中读取，批量写入脚本文件。如果漏写，事后用 Python 扫描 `scripts/sd*.md` 并批量插入（推荐在 `**源章节**` 行后插入）。2026-07-20 实测 55 个文件批量插入一次完成。

**关键约束：每集 ≤4000 字符** — 分镜脚本文件必须严格控制在 4000 字符以内。超出时拆分为多个文件（EP1/EP2/EP3...），每集独立文件。生成后立即验证：
```bash
for f in scripts/sd*.md; do
  chars=$(wc -m < "$f")
  echo "$(basename "$f"): ${chars} chars"
  [ "$chars" -gt 4000 ] && echo "⚠️ 超限"
done
```

**触发条件**：用户已有 light_novel/ln*.md 源章节和已建立的角色/场景/道具资产，只想快速产出短剧分镜脚本，不需要完整 5 阶段工作流。典型场景：长篇连载项目的中期章节转换、用户要求"直接从小说生成分镜"。

**工作流**：

1. **读取源章节和项目资产**
   - 读取目标章节 lnXXX.md 全文
   - 读取项目 assets.md 或 characters.md（获取已有 C/S/P 编码）
   - **资产 fallback（常见！）**：当 `assets.md` 不存在且 `characters.md` 仅为占位（如"（待生成）"）时：
     - 优先使用用户在指令中直接提供的 C/S/P 编码及其含义（最可靠的事实源）
     - 或扫描 `scripts/sd*.md` 中已有的资产列来推断存在的编码：
       ```bash
       grep -ohP '(?<=^|\\| )[A-Z]\\d+(?= |$)' scripts/sd*.md | sort -u
       ```
     - 推断出的编码只在本轮脚本中使用，不创建 `assets.md`（避免与未来完整 5 阶段生成的资产清单冲突）。
   - 读取已有分镜脚本（sd* 或 sb*）了解之前使用的格式和风格
   - 如果项目已有 `scripts/sd*.md` 历史文件，沿用其命名模式

2. **确定分集方案**
   - 根据源章节长度和内容密度拆分为 N 集（每集 ≤4000 字符 / 15 秒 / 5-8 镜）
   - 拆集原则：按叙事节拍划分（开场/发现 → 行动/搜索 → 高潮/转折 → 回响/钩子）
   - 源文件每 60-80 行（约 4-6KB）一般可拆分 1 集；长章（250-300 行）拆 4-5 集
   - 每集必须有独立的情感弧线和章末钩子

3. **分镜格式选择**（格式 A 或 B，优先沿用项目已有格式）
   - 表格格式（格式 A）：列定 `镜号 | 时长 | 景别+运镜 | 画面 | 台词/VO | 音效 | @资产`
   - Seedance 格式（格式 B）：列定素材清单 + 时间轴 + 尾帧
   - 格式 A 的 `@资产` 列引用已有的 C/S/P 资产编码（来自 assets.md），注意：
     - 未在资产清单注册的场景（如新章节引入的独特地点）使用画面描述代替资产编码，不强行纳入已有 C/S/P
     - 资产编码仅引用已在 assets.md 定义的条目

4. **直接输出到 scripts/ 目录**
   ```text
   scripts/sdXXX_EP1_标题.md        # 快速脚本（短剧分镜）
   scripts/sdXXX_EP2_标题.md
   └── ...
   ```
   - 命名模式：`sd{章节号}_{EP{N}}_{标题}.md`
   - 如果项目此前使用 storyboard/sbXXX.md 路径，优先沿用；scripts/ 为快速简版用

5. **每集强制包含**
   - 源章节标注（`**源章节**：lnXXX_章名.md`）
   - 尾帧描述（场景/画面/光线/构图/氛围/用途）
   - 第 N 集尾帧应被第 N+1 集首镜承接（多集时自动校验）

6. **写入后验证**
   ```bash
   for f in scripts/sdXXX_EP*.md; do
     chars=$(wc -m < "$f")
     echo "$(basename "$f"): ${chars} chars"
     [ "$chars" -gt 4000 ] && echo "⚠️ 超限"
   done
   ```
   - 每集 ≤4000 字符
   - `@资产` 引用有效（不引用未注册的 C/S/P 编码）
   - 尾帧描述完整

7. **项目约定兼容（重要）** — 快速直转前先读取已有脚本（`scripts/sd*_EP*.md`）了解项目实际使用的格式（这也是 assets.md 不存在时推断 C/S/P 编码的 fallback 路径，见步骤 1）：
   - **镜头密度**：技能模板说 5-8 镜/15秒，但多数项目实际使用 **7 镜/15秒**（每镜 ~2s），尤其对话驱动场景。读已有脚本确认后沿用，不要硬套下限。
   - **`@资产` 列**：真实项目中该列常写**多个空格分隔的资产编码**如 `C01 P06`，不是单条。新章节引入全新地点时（如废弃工厂、地下通道），用画面描述文本代替资产编码，不强行纳入未注册的 C/S/P 编码。
   - **非标准镜头**：部分镜头可能被标记为 `中景→推`、`全景→跟`、`俯拍→缓推` 等复合运镜，这在已有脚本中常见，不需要统一为单一景别。
   - **尾帧格式**：沿用已有脚本的 `**场景**`/`**画面**`/`**用途**` 三级结构，不要发明新字段。
   - **命名模式**：沿用项目的 `sd{章节号}_EP{N}_{标题}.md` 模式，不要改后缀或前缀。

**适用场景对比**：

| 场景 | 推荐路径 | 理由 |
|------|---------|------|
| 已有项目，已有资产，快速产出 | 快速直转（skip 1-4） | 无需重做事件提取和资产清单 |
| 新项目/第一次转换 | 完整 5 阶段 | 需要建立事件图谱和资产清单 |
| 大量剧集/需要多角度素材 | 完整 5 阶段 | assets.md 和事件决策保证素材齐全 |
| 用户明确要"快"、"简单"、"直接出" | 快速直转 | 满足用户效率需求 |

### 后端 API

| 路由 | 方法 | 说明 |
|------|------|------|
| `/scripts?project=<名>` | GET | 脚本列表（file, title, chars, source_ln） |
| `/script?project=<名>&file=<名>` | GET | 单篇脚本完整内容 |

### 前端

Reader项目详情页新增「分镜」tab，列表展示（文件名/标题/字数/来源），每项「查看」和「复制」按钮。独立视图原则（`references/reader-modal-vs-view.md`），不用模态框。

### 选择建议

| 故事类型 | 推荐路线 | 原因 |
|---------|---------|------|
| 动作/战斗/冒险 | 漫画渲染 | 视觉冲击力是核心 |
| 悬疑/恐怖 | 漫画或小说均可 | 看氛围是否依赖画面 |
| 日常/恋爱/喜剧 | 小说路线 | 对话驱动，文字感染力更强 |
| 情感/治愈 | 小说路线 | 心理描写更有优势 |
| 职场/美食/合租 | 小说路线 | 场景与对白适合番茄阅读 |
| 推理/智斗 | 小说路线优先 | 线索和心理可读性更高 |
| **有拍摄需求** | **短剧分镜脚本** | **演员/剧组可读，场→镜头规格** |

详见 `references/novel-to-drama-workflow.md`（含完整模板和铁律）。

### 转换工具

`scripts/convert_to_script.py` — 列出章节、检查转换状态、生成输出路径占位。核心转换由 LLM 驱动。

## 更新日志
- v1.25.0（2026-07-20）：模式七 快速直转模式新增两个重要补充：（1）资产 fallback 路径——当 `assets.md` 不存在且 `characters.md` 为占位时，可从 `scripts/sd*.md` 扫描已有 C/S/P 编码或在用户指令中直接获取；（2）新增步骤 7「项目约定兼容」——记录真实项目与技能模板的常见差异（7 镜/集而非 5-8、多资产编码同行、复合运镜标记），防止快速直转时硬套模板造成格式偏离。实测于《深夜电台主持人》ln009→4 集 sd009_EP* 转换。  
- v1.25.0（2026-07-20）：完成深夜电台主持人12章→55集短剧分镜脚本全量生成。统一风格前缀、前端分镜查看器增加上一个/下一个导航按钮。复制按钮修复兼容HTTP。

- v1.24.1（2026-07-20）：修复复制按钮（`navigator.clipboard` → `document.execCommand('copy')` 兼容 HTTP）。新增「快速直转模式」文档（跳过 5 阶段直接产出脚本），记录 ≤4000 字符/文件约束和复制按钮陷阱。完成 12 章完整短剧脚本批量生成。
- v1.21.2（2026-07-19）：新增 `references/reader-modal-vs-view.md` + 「用户工作流偏好」新条目「Reader 新功能用独立视图，不用模态框」——本次接口文档从 `.api-modal` 弹层改造为 `showApiDoc()` 独立视图的实战记录：实现模板（导航按钮 + setNav + showXxx + window.scrollTo(0,0)）、从模态框迁移的完整清理清单（HTML/CSS/JS 三类残留）、移动端 mXxx 按钮同步、线上+skill 模板双文件同步要求、长文件 patch 凭记忆构造 old_string 失败的教训（与 patch-intext-pitfall 同类但适用于 CSS/代码段）。用户原话"点击接口文档应该是一个新界面展示"明确记录了这条偏好。

- v1.21.1（2026-07-19）：新增 `references/reader-route-ordering-and-by-update.md`——Reader 路由顺序陷阱（FastAPI `{name:path}` 吞掉 `by-update` 子路由，注册顺序必须具体子路径在前）+ 线上 app.py（ThreadingHTTPServer）vs skill reader_server.py（FastAPI）双实现警告；含 `_project_last_updated()` mtime 扫描实现模式、`/projects/by-update` 完整路由参考、前端「最新」视图实现要点、部署验证三件套。SKILL.md「Reader 服务器（内置）」节新增两条 2026-07-19 警告。

- v1.21.0（2026-07-19）：`templates/reader.html` 浅色主题大改造——从深色夜间主题改为浅色 airy 主题（`#f6f7fb` 微冷灰底 + 白色玻璃顶栏 + 柔和中性阴影 `rgba(15,23,42,.05-.10)`），保留番茄红渐变（`--gradient`）作为品牌点缀；**全局隐藏滚动条**（`scrollbar-width:none` + `::-webkit-scrollbar{display:none}`，保留滚动功能）；**移动端阅读工具栏修复**——`.reader-tools` 在 ≤760px 时从 `position:fixed` 改为 `position:static`，使「上一章/A-/A+/下一章」按钮自然落在文章末尾而非悬浮遮罩正文（同步减少 `.reader-box` 底部 padding 从 90px → 40px，释放原本为悬浮工具栏预留的空间）。配套浅色主题 token 完整集合见 `~/.hermes/skills/frontend/single-file-html-app-restyle/templates/light-bookshelf-theme.css`

- v1.20.0（2026-07-12）：整合 Reader 服务器到 skill——新增 `scripts/reader_server.py`（FastAPI 服务器，11 条 API 路由、路径穿越防护、可选 API Key 认证、Pillow 缩略图）和 `templates/reader.html`（番茄小说风格单页 SPA）；修复所有 references 中的硬编码绝对路径泄漏（`$HOME/comic-projects/projects` → `$COMIC_PROJECTS_ROOT`）；隐私扫描覆盖 `.html` 文件；更新 SKILL.md「Reader 服务器（内置）」节及 `references/local-reader-api.md`

- v1.19.1（2026-07-08 实测追加）：模式六 note 8「`write_file` 工具自身的静默字符损坏」确认存在**段落级肌理损坏**子类——不同于已记录的字符级（`_ENC_`）、整词级（`Selectable`）、单字级（U+FFFD）损坏，本次《DemoProjectJ》ln008 续写时 `write_file` 的 `content` 参数流式传输期间，模型在整段中文对话与叙述中出现段落长度的乱码散文：Cyrillic 词块（`тариф`/`неко`）、英语单词混入中文（`OR`/`AND`/`.isVisible`）、表情意义的代码碎片、整句丧失可读性的多段连续损坏。这是目前观测到的最严重损坏等级——**文件本身是否落盘为同样损坏需独立验证**（症状表现在模型助手回复中的回复文本上，而 `write_file` 调用日志返回的字节数与正常章节相当），但坏消息是不管文件是否完整、读者在聊天中看到的交付文本已经不可读。修复方式：发现段落损坏时，不需逐条 `patch`，直接用 `write_file` 整章覆写——但覆写前必须以条理清晰、小于内容 token 上限（≤4K 中文字符）的章节为主要目标，分批写入（先把主体清晰段写入，再 `'a'` 模式追加后续段）。**额外预防**：`write_file` 的 `content` 参数请在冷静专注的模型轮发出，避免当章规划/自我提示同时进入 `content` 段——大段决策性文字与中文叙事散文混合流式传输会增加 transfomer 抽样的崩溃概率。发现自己回复中的正文已肌理损坏时，立即停笔、确认文件状态、覆写整章、不尝试对损坏的段落做点状 `patch`。
- v1.19.0：`references/light-novel-single-script-generation.md` 新增「工具调用预算与模式选择」段——2026-07-09《DemoProjectD》续写第6-14章（共9章）实测暴露会话工具调用迭代上限约束：逐章 `write_file` + 五项自检 + patch 修污染/补字数为 3-7 调用/章，9章即 27-63 次调用撞上上限，仅完成4章即被截断。新增单章调用开销明细表、模式选择规则表（N≥6 强制评估模式三）、预判检查清单，强制批量续写前先评估工具预算。SKILL.md 模式六 note 8 新增「工具调用预算与模式选择」条目；参考资料列表对该 ref 的描述同步更新。本会话 Cyrillic/英文整词污染（`неше` / `narrowing` / `signature` / `borrowed`）和伪 ILLUST 标记（`«ILLUST_2»`）均已被 note 8 五项自检 SOP 即时捕获并 `patch` 修复，确认该 SOP 覆盖有效——未发现新污染类型。
- v1.17.0：模式六 note 8「验证与维护」新增「`write_file` 工具自身的静默字符损坏」段——区分 heredoc 损坏（note 7/12）与 `write_file` 传输层偶发损坏两类问题，记录三种子类污染实例（`_ENC_` 下划线包裹伪标记、`Selectable` 整词英文替换中文语素、`沈令�` U+FFFD 替换字符），并新增强制写入后自检五项 Python SOP（CJK 字数 / 对白格式 / 插图数 / `[a-zA-Z]{3,}` 英文整词 / `_XXX_` 伪标记 / U+FFFD 计数）。2026-07-09《DemoProjectI》续写 ln005–ln013 共 9 章实测：首稿 2 章（ln007、ln008）落入此陷阱，均靠写入当轮自检即时捕获并 `patch` 修复（ln007 CJK 2313→2550、ln008 2486→2575），不跑自检则污染流入下游 Reader。同 session 另发现一处 **`patch` 自身补字时的微笔误**（ln010"过了一很久"→应为"过了很久"，LLM 在 new_string 里改写而非原样复制 old_string，落入 note 8 已记录的 patch 隐式误替换陷阱，忆 note 8「patch 三重陷阱」仍生效，本次未新增陷阱类型）。`verify_light_novel_delivery.py` 与 `scan_unicode_contamination.py` 对本 session 三类污染中 (a) `_ENC_` 与 (c) U+FFFD 亦未覆盖——只有当轮手写自检能抓。
- v1.16.0：模式六 note 8「验证与维护」新增「根级文件一致性自检（强制）」——交付前用 `grep -l "待生成"` 验证根级文件未被占位文本残留；note 13 扩展为「始终加载 skill 后再写稿/写小说（强制）」——明确覆盖轻小说生成/前N章+设定交付路线，补充"缺少加载步骤可能遗漏重要规则"的后果说明。2026-07-08《倒数三秒告白》session 实测：未加载 skill 直接开工，创建了 `chars.md` 而非更新根级 `characters.md`，暴露出缺少加载意识和交付前自检的双重缺口。`scripts/verify_light_novel_delivery.py` 新增两项检查——①角色名漂移检测（`--check-role-drift yes`，默认开）：从 `characters.md` 提取规范化角色名，扫描每章 `「...」——<name>` 归属行里的一字之差变体（如 柠/檬、冬青/檬），补 `validate_light_novel.py` 和 `scan_garbled()` 都检测不到的盲区；②ASCII-in-CJK 扫描（抓"队47人"阿拉伯数字混入中文叙述、"ProjectCode: jixia"英文标识符混入）。模式六 note 5「正文写作格式」新增「角色名漂移陷阱」子条；`references/light-novel-single-batch-generation.md` 新增 §角色名漂移陷阱 + §投递级验证脚本更新段，验收清单新增「跑过 verify_light_novel_delivery.py」一项。2026-07-08《AI女友已下线》session 实测：characters.md 用"沈檬"，三章正文先后出现"沈柠"和"沈冬青"两种漂移变体，手写自检脚本完全漏检，只有 `verify_light_novel_delivery.py --check-role-drift` 能抓。
- v1.14.0：新增 `scripts/scan_unicode_contamination.py`——补 `validate_light_novel.py` 和 `scan_garbled()` 的 Unicode 块越界盲区（Cyrillic `ото`、Hebrew U+05BA 粘 CJK、Latin Extended `ǣ`、HTML 工件 `<table end>`、Latin 借词句中混入）；`references/light-novel-garbled-text-cleanup.md` §5 新增"非 Latin Unicode 块越界"小节；模式六 note 8 跨语言乱码检查段更新，推荐 `scan_unicode_contamination.py` 为投递前最后一道闸
- v1.13.0：新增 `references/patch-intext-pitfall.md`——`patch` 工具对中文长篇正文增补的三重陷阱（隐式误替换、phantom 字符、状态脱节）的实测记录和完整安全 SOP；模式六 note 8 验证段补强对应提醒
- v1.13.0：新增 `references/patch-intext-pitfall.md`——`patch` 工具对中文长篇正文增补的三重陷阱（隐式误替换、phantom 字符、状态脱节）的实测记录和完整安全 SOP；模式六 note 8 验证段补强对应提醒
- v1.12.0：新增轻小说全脚本单次落盘模式（`references/light-novel-single-script-generation.md`）——把元数据+全部章节正文塞进同一个 Python 脚本，2 个工具调用覆盖 ≤6 文件；模式六 note 12 新增"批量落盘"写入路径选项
- v1.11.0：小说路线升级为 20 万字长篇生产流程；新增 `update_long_novel_context.py` 和 `validate_long_novel.py`，强制分批生成、压缩上下文、角色/伏笔/最近连续性提取，避免加载全文导致上下文爆炸
- v1.10.0：完善模式六为独立小说/网文生成流程，新增 validate_light_novel.py 验证脚本，明确小说项目结构、章节 beat、正文格式、批量生成与 Reader 书架接入规则
- v1.9.0：新增模式六（轻小说 + 关键场景插图路线），新增 export_light_novel.py 脚本，在稿子完成后增加路线选择入口（漫画渲染 vs 轻小说）
- v1.8.5：新增 `references/image-generation-config.md` API 性能实测数据（120-155s/图）、批量渲染模式说明、`--output-dir` 多集覆盖避免指南
- v1.8.4：新增 `render_images.py --limit` 默认值为 1 的陷阱说明、`--output-dir` 多集覆盖风险、`terminal().workdir` 中文路径限制及解决方案、渲染重试策略补充
- v1.8.3：新增气泡格式解析规则（update_project.py 角色名解析）、追加写入污染风险与修复方法、系列大结局/最终集规则、文件写入九条规则（Shell heredoc 禁用、write_file 优先、分批写入验证等）
- v1.8.1：修正 export_for_render.py 输出为 story-renderer 手动分镜标准 `## 镜头 N`；README 徽章改为通用静态徽章
- v1.8.0：集成 story-renderer 渲染流程；新增 export_for_render.py 桥接脚本；支持稿子生成后直接渲染漫画图片
- v1.7.0：漫画脚本格式升级为 Page/Panel；新增格子/气泡/旁白/拟声/转场、结尾钩子、下集提示；脚本验证适配 Panel；续写强制读取上集末3个Panel；风格只读 style_guide
- v1.5.0：前端分页与懒加载优化；新增部署访问说明；reader 路由说明
- v1.4.0：新增在线脚本生成接口规范、config.json script_source 配置
- v1.3.0：新增自动更新项目文件脚本、角色一致性检查脚本
- v1.2.0：新增 AI 绘图提示词、初始化脚本、验证脚本、编辑工作流
- v1.1.0：新增三种分镜密度模式（对话多/平衡/电影短剧风）
- v1.0.0：初始版本，支持分镜生成、项目管理、热点抓取
