---
name: csg-deployment
description: >-
  Reader 服务器部署与访问说明、后端 API 路由、前端双模式阅读、缩略图加速、线上 vs skill 双实现注意事项。
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, terminal
---

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
- **复制按钮陷阱（2026-07-20 实测）**：`navigator.clipboard.writeText()` 在 HTTP（非 HTTPS）环境下静默失败，用户点击无响应且不报错。**强制修复方案**：改用 `document.execCommand('copy')` 回退方案——创建临时 `<textarea>`，`select()` 后 `execCommand('copy')`，再 `removeChild()`。详见 reader.html 中的 `copyText()` 函数。
- **字数显示**：前端显示字符数时应使用 `字` 而非 `字节`。后端 `chars` 字段返回 `len(content.strip())`（字符数），而非 `f.stat().st_size`（字节数）。注意同步修改前端模板中所有 `${...} 字节` → `${...} 字`。
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
