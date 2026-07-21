# Comic Script Generator

<p align="center">
  <img src="https://img.shields.io/badge/version-v1.11.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/format-Page%2FPanel%20%2B%20Light%20Novel-orange.svg" alt="Format">
</p>

<p align="center">
  <strong>漫画分镜、轻小说正文与漫画渲染生产工具</strong><br>
  <strong>Generate Page/Panel comic scripts, light novels, and render-ready manga assets</strong>
</p>

<p align="center">
  <a href="#快速开始">快速开始</a> •
  <a href="#核心特性">核心特性</a> •
  <a href="#隐私与本地配置">隐私配置</a> •
  <a href="#脚本工具">脚本工具</a> •
  <a href="README.en.md">English</a>
</p>

---

## 简介

**Comic Script Generator** 是一个 Hermes skill，用于生产漫画分镜、轻小说正文、关键场景插图清单与渲染输入文件。

核心路线：

1. **漫画路线**：`Page → Panel` 分镜脚本，每个 Panel 包含格子、画面、构图、气泡、旁白、拟声、转场和 AI 提示词。
2. **渲染路线**：把漫画稿导出为 `render_input/`，再通过私有 OpenAI-compatible 图片接口渲染、叠字、合成漫画页和长图。
3. **小说路线**：生成番茄小说风格轻小说/网文正文，配套关键插图清单、长篇上下文压缩和验收脚本。

---

## 核心特性

### Page/Panel 漫画稿格式

- 使用 `## Page X` / `### Panel X`。
- 每个 Panel 必填：`格子`、`画面`、`构图`、`气泡`、`旁白`、`拟声`、`转场`、`AI 提示词`。
- 同一项目所有集必须使用同一个 `style_guide.md`。

### 小说 / 网文路线

- 原生轻小说项目结构：`light_novel/lnXXX_<章名>.md`。
- 正式长篇默认目标不少于 20 万字。
- 支持 `update_long_novel_context.py` 压缩上下文，避免每次续写读取全文。
- 支持 `validate_light_novel.py` 和 `validate_long_novel.py` 验收。

### 渲染与 Reader

- `export_for_render.py`：导出 story-renderer 风格 `## 镜头 N` 输入。
- `render_images.py`：调用私有生图接口并发渲染。
- `overlay_comic_text.py`：叠加中文对白/拟声。
- `compose_manga_pages.py`：合成漫画页。
- `stitch_localized_chapter.py`：拼接完整汉化长图。
- Reader 支持漫画/小说双模式、缩略图、懒加载、图片对照稿。

---

## 隐私与本地配置

**硬规则：skill 仓库和 skill 目录不得包含真实敏感信息。**

不得写入 `SKILL.md`、README、references、示例文件、项目稿件或任何准备提交/发布的文件：

- API token / Authorization / Bearer / Cookie
- 私有图片 API 域名
- 服务器公网 IP
- VPN/代理订阅
- 数据库密码
- 个人本机路径或生产部署路径

生图配置只允许保存在本地私有文件，推荐：

```bash
mkdir -p ~/.config/comic-script-generator
cp config.example.json ~/.config/comic-script-generator/image_config.json
chmod 600 ~/.config/comic-script-generator/image_config.json
export COMIC_IMAGE_CONFIG=~/.config/comic-script-generator/image_config.json
```

`render_images.py` 配置读取顺序：

```text
1. --config
2. $COMIC_IMAGE_CONFIG
3. ~/.config/comic-script-generator/image_config.json
```

发布或同步前必须运行：

```bash
python3 scripts/privacy_check.py
```

---

## 快速开始

### 1. 初始化漫画项目

```bash
python3 scripts/init_project.py "项目名" --output ~/comic-projects --mode B --episodes 6
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

### 2. 生成并验证漫画稿

```bash
python3 scripts/update_project.py episodes/ep001_<标题>.md --project-dir projects/<项目名> --episode-num 1
python3 scripts/validate_episode.py episodes/ep001_<标题>.md --project-dir projects/<项目名>
python3 scripts/consistency_check.py episodes/ep001_<标题>.md --project-dir projects/<项目名>
```

### 3. 导出渲染输入

```bash
python3 scripts/export_for_render.py episodes/ep001_<标题>.md --project-dir projects/<项目名> --style-guide projects/<项目名>/style_guide.md
```

输出：

```text
projects/<项目名>/render_input/ep001_<标题>_render.md
```

### 4. 渲染图片

```bash
python3 scripts/render_images.py projects/<项目名>/render_input/ep001_<标题>_render.md --limit 999 --workers 5 --sleep 0.2 --retries 2
```

注意：`--limit` 默认是 1；渲染全部必须显式传 `--limit 999` 或 `--limit 0`。

---

## 分镜密度模式

| 模式 | 说明 | 推荐用途 |
|------|------|----------|
| A | 对话多，镜头少，每集约 30-40 Panel | 恋爱、日常、对话密集型 |
| B | 一个对话对应一个镜头，每集约 50-60 Panel | 通用漫画脚本 |
| C | 一段对话多个镜头，每集约 150-250 Panel | 电影感、短剧感、动作戏 |
| LN | 轻小说 / 网文正文 | 日常、恋爱、治愈、职场、推理 |

---

## 脚本工具

| 脚本 | 作用 |
|------|------|
| `scripts/check_update.py` | 检查远程更新，网络不通时跳过 |
| `scripts/privacy_check.py` | 发布前隐私扫描 |
| `scripts/init_project.py` | 初始化漫画项目 |
| `scripts/update_project.py` | 提取角色、伏笔、摘要并更新项目文件 |
| `scripts/validate_episode.py` | 验证漫画 Page/Panel 格式 |
| `scripts/consistency_check.py` | 检查角色一致性 |
| `scripts/batch_generate.py` | 批量生成漫画项目 |
| `scripts/export_for_render.py` | 导出渲染输入 |
| `scripts/render_images.py` | 调用私有生图接口渲染图片 |
| `scripts/overlay_comic_text.py` | 后期叠加中文对白/拟声 |
| `scripts/compose_manga_pages.py` | 合成漫画页 |
| `scripts/stitch_localized_chapter.py` | 拼接汉化长图 |
| `scripts/export_light_novel.py` | 从漫画稿导出轻小说兼容文本 |
| `scripts/validate_light_novel.py` | 验证轻小说正文 |
| `scripts/update_long_novel_context.py` | 生成长篇小说压缩上下文 |
| `scripts/validate_long_novel.py` | 验收长篇小说字数/章节/上下文 |

---

## 项目结构

```text
projects/<项目名>/
├── config.json
├── summary.md
├── characters.md
├── foreshadowing.md
├── style_guide.md
├── episodes/                 # 漫画分集稿
├── light_novel/              # 小说章节
├── long_novel_context/       # 长篇上下文压缩
├── render_input/             # 渲染输入 / 插图清单
├── rendered/                 # 单格渲染图
├── comic_pages/              # 合成漫画页
└── localized/                # 汉化长图等最终交付物
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
<来自 style_guide.md 的固定风格>, 黄昏天台，远景，橙红色天空，孤独情绪, no text, no letters, leave empty space for speech bubbles
```
反向：
```text
<来自 style_guide.md 的固定反向提示词>
```
```

---

## 生产发布检查

发布、复制到其他环境、或 push 前执行：

```bash
python3 -m py_compile scripts/*.py
python3 scripts/privacy_check.py
python3 scripts/check_update.py
```

检查目标：

- Python 脚本语法通过。
- 无真实 token/IP/私有域名/本机路径泄漏。
- `config.example.json` 只有占位符。
- 真实配置只在本地私有路径。
- README 与 `SKILL.md` 版本一致。

---

---

## 支持

如果这个项目对你有帮助，欢迎点个 ⭐ Star！

[![GitHub stars](https://img.shields.io/github/stars/AveQY/comic-script-generator?style=social)](https://github.com/AveQY/comic-script-generator)

