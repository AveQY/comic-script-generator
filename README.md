# Comic Script Generator

<p align="center">
  <img src="https://img.shields.io/badge/version-v1.27.1-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/format-Page%2FPanel%20%2B%20Light%20Novel-orange.svg" alt="Format">
</p>

<p align="center">
  <strong>漫画分镜、轻小说正文、短剧分镜脚本与漫画渲染生产工具</strong><br>
  <strong>Generate Page/Panel comic scripts, light novels, drama storyboards, and render-ready manga assets</strong>
</p>

<p align="center">
  <a href="#简介">简介</a> •
  <a href="#架构总协议--路由器">架构</a> •
  <a href="#核心特性">核心特性</a> •
  <a href="#快速开始">快速开始</a> •
  <a href="#安全配置与凭证管理">安全配置</a> •
  <a href="#脚本工具">脚本工具</a> •
  <a href="README.en.md">English</a>
</p>

---

## 简介

**Comic Script Generator** 是一个 AI Agent skill（Hermes / Claude Code / WorkBuddy 等通用），用于生产漫画分镜、轻小说正文、短剧分镜脚本、关键场景插图清单与渲染输入文件。

四条核心路线：

1. **漫画路线**：`Page → Panel` 分镜脚本，每个 Panel 包含格子、画面、构图、气泡、旁白、拟声、转场和 AI 提示词。
2. **渲染路线**：把漫画稿导出为 `render_input/`，再通过私有 OpenAI-compatible 图片接口渲染、叠字、合成漫画页和长图。
3. **小说路线**：生成番茄小说风格轻小说/网文正文，配套 16 种文笔风格（prose_style）、关键插图清单、长篇上下文压缩和验收脚本。
4. **短剧路线**：小说章节直转 `△` 短剧拍摄脚本/分镜表，另附 6 维爆款潜力评估。

---

## 架构：总协议 + 路由器（v1.26.5+）

自 v1.26.5 起采用**路由式子 skill 架构**（仿 [cheat-on-content](https://github.com/XBuilderLAB/cheat-on-content) 设计）：

- 根目录 `SKILL.md` = **总协议 + 路由器**（跨模式强制规则、隐私规范、更新检查），保持轻量；
- 具体工作流拆分到 `skills/csg-*/SKILL.md` **13 个子 skill**，按需加载，降低上下文开销；
- `references/` 下 71 篇参考文档按需读取，分类索引见 [`references/README.md`](references/README.md)。

### 模式路由表

| 触发词示例 | 子 skill | 说明 |
|--------|------------|---------|
| "初始化" / "创建项目" | `csg-init` | 项目骨架创建 + 分镜密度选择 + prose_style 配置（入口） |
| "写分镜" / "根据大纲写" | `csg-mode1-user-outline` | 按用户大纲生成分镜脚本 |
| "抓热点" / "今天有什么热点" | `csg-mode2-hotspot` | 百度热搜抓取 → 选题 → 生成 |
| "续写" / "继续写第N集" | `csg-mode3-continue` | 续写与修改，伏笔管理 |
| "批量生成" / "auto" | `csg-mode4-batch` | 批量多项目循环生产 |
| "渲染" / "出图" | `csg-mode5-render` | 导出 → 并发渲染 → 叠字 → 合成 |
| "写小说" / "轻小说" / "书架" | `csg-mode6-light-novel` | 独立轻小说生产线 |
| "短剧" / "△剧本" / "拍摄脚本" | `csg-mode7-drama` | 小说直转短剧分镜 |
| "爆款评估" / "评估潜力" | `csg-mode8-evaluation` | 6 维爆款潜力评分（CH/ER/CA/PQ/AD/CO） |
| "分镜密度" / "Page/Panel 模板" | `csg-densities` | A/B/C 密度模式与格式模板 |
| "角色模板" / "伏笔模板" | `csg-templates` | 项目文件 Markdown 模板 |
| "部署" / "Reader" | `csg-deployment` | Reader 服务器部署与 API |
| "市场验收" / "漫画评分" | `csg-market-validation` | 100 分制市场验收 |

---

## 核心特性

### Page/Panel 漫画稿格式

- 使用 `## Page X` / `### Panel X`。
- 每个 Panel 必填：`格子`、`画面`、`构图`、`气泡`、`旁白`、`拟声`、`转场`、`AI 提示词`（没有则写"无"）。
- 同一项目所有集必须使用同一个 `style_guide.md`。

### 小说 / 网文路线

- 原生轻小说项目结构：`light_novel/lnXXX_<章名>.md`。
- **16 种文笔风格预设（prose_style，v1.27.0）**：创建小说时多选，写入 `config.json` + `prose_style_guide.md`，续写自动沿用，颗粒度为单本小说。
- 正式长篇默认目标不少于 20 万字。
- `update_long_novel_context.py` 压缩上下文，避免每次续写读取全文。
- `validate_light_novel.py` / `validate_long_novel.py` / `verify_light_novel_delivery.py` 三级验收。

### 渲染与 Reader

- `export_for_render.py`：导出 story-renderer 风格 `## 镜头 N` 输入。
- `render_images.py`：调用私有生图接口并发渲染。
- `overlay_comic_text.py`：叠加中文对白/拟声。
- `compose_manga_pages.py`：合成漫画页，`stitch_localized_chapter.py` 拼接完整汉化长图。
- `reader_server.py`：本地 Reader 服务器，漫画/小说双模式、书架、缩略图、懒加载、图片对照稿。

---

## 安全配置与凭证管理

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

**推荐用 git clone 安装**（skill 内置 `check_update.py` 更新检查依赖 git 历史）：

```bash
git clone https://github.com/AveQY/comic-script-generator.git <你的-skills-目录>/comic-script-generator
```

### 1. 初始化漫画项目

```bash
python3 scripts/init_project.py "项目名" --output ~/comic-projects --mode B --episodes 6
```

会创建：

```text
<输出目录>/projects/<项目名>/
├── config.json
├── summary.md
├── characters.md
├── foreshadowing.md
├── style_guide.md
└── episodes/
```
（注：脚本会在 `--output` 指定路径下自动创建 `projects/` 子目录进行项目隔离，实际路径为 `~/comic-projects/projects/<项目名>/`）

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

全部 23 个脚本一览：

| 脚本 | 作用 |
|------|------|
| `scripts/init_project.py` | 初始化漫画项目（含 prose_style 文笔风格配置） |
| `scripts/update_project.py` | 提取角色、伏笔、摘要并更新项目文件 |
| `scripts/validate_episode.py` | 验证漫画 Page/Panel 格式 |
| `scripts/consistency_check.py` | 检查角色一致性 |
| `scripts/repair_manga_logic.py` | 修复漫画逻辑问题 |
| `scripts/batch_generate.py` | 批量生成多个漫画项目 |
| `scripts/export_for_render.py` | 导出渲染输入 |
| `scripts/render_images.py` | 调用私有生图接口并发渲染 |
| `scripts/restore_raw_images.py` | 恢复原始渲染图 |
| `scripts/overlay_comic_text.py` | 后期叠加中文对白/拟声 |
| `scripts/compose_manga_pages.py` | 合成漫画页 |
| `scripts/stitch_localized_chapter.py` | 拼接汉化长图 |
| `scripts/export_light_novel.py` | 从漫画稿导出轻小说兼容文本 |
| `scripts/validate_light_novel.py` | 验证轻小说正文 |
| `scripts/verify_light_novel_delivery.py` | 轻小说投递级验证 |
| `scripts/update_long_novel_context.py` | 生成长篇小说压缩上下文 |
| `scripts/validate_long_novel.py` | 验收长篇小说字数/章节/上下文 |
| `scripts/convert_to_script.py` | 小说章节转短剧分镜脚本 |
| `scripts/scan_unicode_contamination.py` | Unicode 块污染扫描 |
| `scripts/scan_cjk_prose_pollution.py` | 中文正文污染扫描 |
| `scripts/reader_server.py` | Reader 阅读器服务器（漫画/小说双模式） |
| `scripts/check_update.py` | 检查远程更新（内置 24 小时缓存，网络不通时跳过） |
| `scripts/privacy_check.py` | 发布前隐私/安全检查 |

Reader 服务器额外依赖见 [`requirements-reader.txt`](requirements-reader.txt)。

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

## ⭐ Star 趋势

[![Star History Chart](https://api.star-history.com/svg?repos=aveqy/comic-script-generator&type=Date)](https://star-history.com/#AveQY/comic-script-generator&Date)

---

## 许可证

MIT
