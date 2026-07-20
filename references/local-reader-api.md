# Local Reader/API setup notes

Use these notes when the comic-script-generator skill needs a local project browser and the standalone API project is absent.

## Trigger
- User asks to run the front-end/Reader site for generated comic projects.
- `/path/to/comic-script-generator-api` or the expected deployed app is missing.

## Recommended local fallback

### 首选：FastAPI + uvicorn（功能更全）

Use `scripts/reader_server.py` from the skill directory:

```bash
cd /path/to/skill
pip install fastapi uvicorn aiofiles Pillow
COMIC_PROJECTS_ROOT=/path/to/comic-projects/projects COMIC_READER_PORT=8081 COMIC_READER_API_KEY=yourkey python3 scripts/reader_server.py
```

Supported endpoints match the skill's deployment documentation (see SKILL.md「Reader 服务器（内置）」节).

### 备用：ThreadingHTTPServer（兼容兜底）

If FastAPI dependencies are unavailable, the legacy `app.py` approach still works: a minimal Python `ThreadingHTTPServer` app that serves:
- `GET /reader` — single-page Reader UI.
- `GET /health` — health check with project root.
- `GET /projects` — list directories under the comic projects root, filtered by search/status/has_images.
- `GET /projects/<name>` — project detail including config, episodes, render inputs, docs, images, and aggregate stats.
- `GET /episode?project=<name>&file=<episode.md>` — full episode content.
- `GET /doc?project=<name>&file=<doc.md>` — project docs such as `summary.md`, `characters.md`, `foreshadowing.md`, `style_guide.md`.
- `GET /thumb?project=<name>&path=<relative path>&width=<w>&height=<h>&fit=cover|inside` — 动态缩略图接口，当前稳定输出 JPEG，质量 78，支持 cover/inside。响应头通常包含 `Cache-Control: public, max-age=86400`。
  - 注意：虽然曾实现过 AVIF/WebP 内容协商和 `disk_cache/` 预生成脚本，但当前可靠运行版本仍以 JPEG 为主；现代格式可作为后续优化项，不阻塞基本可用性。
- `GET /file?project=<name>&path=<relative path>` — 原图/文档访问，不支持内容协商，始终按文件真实类型返回。

Default environment:
```bash
COMIC_PROJECTS_ROOT=/path/to/comic-projects/projects
COMIC_READER_PORT=8081
```

Start pattern:
```bash
cd /path/to/comic-script-generator-api
COMIC_PROJECTS_ROOT=/path/to/comic-projects/projects COMIC_READER_PORT=8081 python3 app.py
```

Verify:
```bash
curl -fsS http://127.0.0.1:8081/health
curl -fsS http://127.0.0.1:8081/projects
```

## UX lessons from session
- Prefer a light, clean UI if the user requests visual polish or complains that the interface is not beautiful enough.
- Project names should be story-facing names, not technical batch IDs. If generated directories are named like `async_comic_001_*`, rename stable finished projects to their story titles and store the old technical ID in `config.json` as `slug` if useful.
- The Reader should show complete project data, not only a minimal list: stats, episodes, full text, summary, characters, foreshadowing, style guide, config, render inputs, and image gallery.
- Avoid truncating episode content in the API; let the UI scroll instead.

## Security
- Validate project/path inputs with resolved paths to prevent traversal outside the project root.
- If exposed publicly, keep UFW allowing only required ports and add optional Reader API key support via `COMIC_READER_API_KEY`.
