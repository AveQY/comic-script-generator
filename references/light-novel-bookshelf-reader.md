# 轻小说批量生成与番茄书架前端经验（2026-07）

## 触发场景
- 用户认为逐格漫画生成不理想，要求改走“轻小说 + 关键插图”路线。
- 用户要求前端不是单一项目界面，而是先进入首页，再展示小说分类与书架。

## 生成策略
- 对日常、恋爱、治愈、职场、美食等对话/情绪驱动题材，优先建议模式六（轻小说路线）。
- 批量生成小说时，每本项目仍按独立项目目录落盘：
  - `config.json`：加入 `content_mode: light_novel`、`category`、`script_unit: light_novel`。
  - `summary.md`：项目卖点 + 章节摘要。
  - `characters.md`：核心角色。
  - `foreshadowing.md`：未回收/已回收伏笔。
  - `style_guide.md`：插图风格。
  - `light_novel/ln001_*.md ...`：正文。
  - `render_input/key_scenes*.json`：关键插图清单。
- 首页书架计数不能只数 `episodes/*.md`；轻小说项目应以 `light_novel/ln*.md` 作为章节数。

## Reader/API 后端要点
- 新增/保留接口：`GET /light-novels?project=<name>`，返回：
  - `project`
  - `count`
  - `novels: [{file,title,chars,url}]`
- `project_meta()` 应识别轻小说项目：
  - `content_mode = cfg.content_mode or ('light_novel' if light_novel/ln*.md exists else 'comic')`
  - `category = cfg.category or cfg.content_mode or ''`
  - `episodes = len(light_novel/ln*.md) if exists else len(episodes/*.md)`
  - 可额外返回 `light_novels` 数量。

## 番茄小说式前端规则
- 首屏必须是首页/书架，不要直接进入某个项目详情。
- 首页结构建议：
  - 顶部品牌：`🍅 番茄书架`
  - 左侧：分类频道（全部、日常、恋爱、治愈、搞笑、漫画等）
  - 主区：欢迎 Banner + 分类 chip + “我的书架”小说卡片
  - 点击书卡后进入书籍详情/章节列表，默认小说阅读模式。
- 保留模式切换：`📖 小说` 与 `🖼 漫画`，但默认优先小说模式。
- 书卡展示项目故事名、简介、分类、章数、插图/渲染图数量。
- 小说阅读页使用米黄背景、宋体/serif、首行缩进、字号调节、上下章导航、阅读进度条。

## 前端调试坑
- 修改 `reader.html` 后必须提取 `<script>...</script>` 用 `node --check` 检查语法：
  ```bash
  python3 - <<'PY'
  from pathlib import Path
  import re
  html=Path('/path/to/comic-script-generator-api/reader.html').read_text(encoding='utf-8')
  m=re.search(r'<script>([\s\S]*)</script>', html)
  Path('/tmp/reader_script.js').write_text(m.group(1), encoding='utf-8')
  PY
  node --check /tmp/reader_script.js
  ```
- 一次多函数 patch 后容易多出/缺少 `}`，症状是前端一直“加载中”，因为 `loadProjects()` 没执行。
- 修复后验证：
  ```bash
  curl -fsS http://127.0.0.1:8081/projects
  curl -fsS 'http://127.0.0.1:8081/light-novels?project=<urlencoded>'
  curl -fsS http://127.0.0.1:8081/reader | grep -E 'home-hero|bookshelf|番茄书架'
  ```

## 不要记录为永久负面结论
- 生图接口慢/超时是服务状态问题；可记录“用 `--limit 999`、不传统一 `--output-dir`、5 workers 并发”的正确模式，但不要写死“接口不可用”。
