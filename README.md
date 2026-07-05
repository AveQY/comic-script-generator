# Comic Script Generator

<p align="center">
  <img src="https://img.shields.io/badge/version-v1.8.1-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/format-Page%2FPanel-orange.svg" alt="Page/Panel Format">
</p>

<p align="center">
  <strong>漫画分镜脚本生成与渲染衔接工具</strong><br>
  <strong>Generate Page/Panel comic scripts, then export them for image/video rendering</strong>
</p>

<p align="center">
  <a href="#快速开始">快速开始</a> •
  <a href="#核心特性">核心特性</a> •
  <a href="#脚本工具">脚本工具</a> •
  <a href="#项目结构">项目结构</a> •
  <a href="README.en.md">English</a>
</p>

---

## 简介

**Comic Script Generator** 是一个漫画分镜脚本生成 skill，用于根据用户大纲、热点话题或连载上下文生成标准漫画稿。

当前核心格式是 **Page → Panel**，不是影视化 `Scene`。每个 Panel 包含格子、画面、构图、气泡、旁白、拟声、转场和 AI 提示词。

从 v1.8.1 开始，它支持与 `story-renderer` 工作流衔接：可以先生成漫画稿，再把选中的剧集导出为渲染输入脚本，后续用于生成漫画图片或视频。

---

## 核心特性

### Page/Panel 漫画稿格式

- 使用 `## Page X` / `### Panel X`
- 每个 Panel 必填：
  - `格子`
  - `画面`
  - `构图`
  - `气泡`
  - `旁白`
  - `拟声`
  - `转场`
  - `AI 提示词`
- 每集包含：
  - 故事梗概
  - 分镜模式
  - 本集核心情绪
  - 本集钩子
  - 本集结尾钩子
  - 下集提示

### 多种创作模式

- **大纲模式**：根据用户提供的故事大纲生成分集漫画稿
- **热点模式**：抓取可访问热点，筛选适合改编的题材
- **续写/修改模式**：读取项目上下文，承接上一集最后 3 个 Panel
- **批量模式**：批量生成多个独立漫画项目，支持断点续传和失败重试
- **渲染衔接模式**：从已生成漫画稿导出 story-renderer 兼容输入

### 项目管理

- `summary.md`：每集摘要索引
- `characters.md`：角色档案
- `foreshadowing.md`：伏笔追踪
- `style_guide.md`：固定画风与负面提示词
- `episodes/`：分集漫画稿
- `render_input/`：导出的渲染输入脚本

### 风格一致性

同一项目所有剧集必须使用同一个 `style_guide.md`。生成时只能读取固定风格词，不能让模型临时拼接主画风、线条风格、上色方式和负面提示词。

---

## 快速开始

### 1. 初始化项目

```bash
python scripts/init_project.py "项目名" --output ~/comic-projects --mode B --episodes 6
```

会创建：

```text
projects/<项目名>/
├── config.json
├── summary.md
├── characters.md
├── foreshadowing.md
├── style_guide.md
└── episodes/
```

### 2. 生成漫画稿

使用 skill 时，提供大纲或题材方向，例如：

```text
帮我写一个校园恋爱故事的第一集，模式 B。
```

生成后保存到：

```text
projects/<项目名>/episodes/ep001_<标题>.md
```

### 3. 更新项目状态

```bash
python scripts/update_project.py episodes/ep001_<标题>.md --project-dir projects/<项目名> --episode-num 1
```

### 4. 验证质量

```bash
python scripts/validate_episode.py episodes/ep001_<标题>.md --project-dir projects/<项目名>
python scripts/consistency_check.py episodes/ep001_<标题>.md --project-dir projects/<项目名>
```

### 5. 导出给 story-renderer 渲染

```bash
python scripts/export_for_render.py episodes/ep001_<标题>.md --project-dir projects/<项目名> --style-guide projects/<项目名>/style_guide.md
```

输出：

```text
projects/<项目名>/render_input/ep001_<标题>_render.md
```

后续可将该文件交给 story-renderer 渲染为图片或视频。

---

## 分镜密度模式

| 模式 | 说明 | 推荐用途 |
|------|------|----------|
| A | 对话多，镜头少，每集约 30-40 Panel | 恋爱、日常、对话密集型 |
| B | 一个对话对应一个镜头，每集约 50-60 Panel | 通用漫画脚本 |
| C | 一段对话多个镜头，每集约 150-250 Panel | 电影感、短剧感、动作戏 |

---

## 脚本工具

| 脚本 | 作用 |
|------|------|
| `scripts/init_project.py` | 初始化项目，创建配置、角色档案、伏笔文件、style_guide |
| `scripts/update_project.py` | 从分集稿提取角色、伏笔、摘要并更新项目文件 |
| `scripts/validate_episode.py` | 验证 Page/Panel 格式、必填字段、提示词完整性 |
| `scripts/consistency_check.py` | 检查角色一致性、未记录角色、外貌冲突 |
| `scripts/check_update.py` | 检查远程仓库是否有新提交 |
| `scripts/batch_generate.py` | 批量生成多个漫画项目 |
| `scripts/export_for_render.py` | 将 episode 的 Panel 导出为 story-renderer 输入脚本 |

---

## 项目结构

```text
projects/<项目名>/
├── config.json
├── summary.md
├── characters.md
├── foreshadowing.md
├── style_guide.md
├── episodes/
│   ├── ep001_<标题>.md
│   └── ep002_<标题>.md
├── render_input/
│   └── ep001_<标题>_render.md
└── rendered/
    └── ep001/
```

---

## 标准 Panel 示例

```markdown
## Page 1

### Panel 1

**格子**：横向大格
**画面**：黄昏的城市天台，夕阳将天空染成橙红色。主角站在栏杆边，风吹起校服衣摆。
**构图**：远景，人物置于画面右下角，天空占据大面积留白

**气泡**：
- 阿明（右侧，对话气泡）："今天也要结束了吗？"

**旁白**：
- 旁白框（左上）："那天的风，比往常更安静。"

**拟声**：
- `呼——`：细长字体，沿栏杆方向延伸

**转场**：情绪转场，接下一格人物特写

**AI 提示词**：
正向：
```text
<来自 style_guide.md 的固定风格>, 黄昏天台，远景，橙红色天空，孤独情绪
```
反向：
```text
<来自 style_guide.md 的固定反向提示词>
```
```

---

## 渲染衔接流程

v1.8.1 新增 `export_for_render.py`，用于把已生成漫画稿转换为 story-renderer 可识别的 `## 镜头 N` 输入脚本。

流程：

1. 先生成并确认漫画稿
2. 选择要渲染的剧集
3. 运行 `export_for_render.py`
4. 检查 `render_input/` 中生成的渲染脚本
5. 调用 story-renderer 生成图片或视频

这个设计让创作分成两个阶段：

- 第一阶段：只生成和审稿
- 第二阶段：确认稿子后再花费图片/视频生成额度

---

## 隐私与配置原则

skill 本身不应包含任何用户私有信息。真实信息应保存在用户自己的配置或项目目录中，例如：

- GitHub 用户名
- API Key
- 服务器 IP
- 线上域名
- 本地用户目录
- 生成模型配置

README 和脚本中只保留占位符，如 `YOUR_DOMAIN`、`YOUR_SERVER_IP`、`YOUR_MODEL_PROVIDER`。

---

## 更新日志

### v1.8.1

- 修正渲染导出格式为 story-renderer 手动分镜标准 `## 镜头 N`
- README 徽章改为静态通用徽章，避免依赖用户 GitHub 名称

### v1.8.0

- 集成 story-renderer 渲染衔接流程
- 新增 `scripts/export_for_render.py`
- 支持从已生成 episode 导出 `render_input/*.md`
- README 更新为 Page/Panel 格式，移除旧 Scene 示例
- skill 文档去个人信息化

### v1.7.0

- 漫画脚本格式升级为 Page/Panel
- 新增格子、气泡、旁白、拟声、转场字段
- 新增本集结尾钩子与下集提示
- 续写强制读取上一集末 3 个 Panel
- 风格统一读取 `style_guide.md`

---

## License

MIT
