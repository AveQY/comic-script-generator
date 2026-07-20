# Reader 路由顺序陷阱与 `/projects/by-update` 实现

2026-07-19 实战：为 Reader 增加「按最后更新时间排序」接口时，撞上一个隐蔽的路由匹配陷阱，并发现线上服务跑的文件与 skill 模板不一致。本条同时记录陷阱、正确实现和部署注意事项。

---

## 1. 路由顺序陷阱（强制）

**症状**：新增 `GET /projects/by-update` 后请求一直 404 / 返回 "Project 'by-update' not found"。

**根因**：FastAPI 按注册顺序匹配路由。`/projects/{name:path}` 写在文件靠前位置（v1.20.0 起在 `scripts/reader_server.py` 第 394 行），`/projects/by-update` 如果注册在它**之后**，`by-update` 会被 `{name:path}` 捕获当成项目名。

### FastAPI（`scripts/reader_server.py`）正确顺序

```python
# 先注册具体路径
@app.get("/projects/by-update")
async def list_projects_by_update(...):
    ...

# 再注册路径参数
@app.get("/projects/{name:path}")
async def project_detail(name: str, ...):
    ...
```

`@app.get("/projects")`（无参数）位置不限——FastAPI 会优先精确匹配。

### ThreadingHTTPServer（`app.py` 旧版）正确顺序

旧版 `app.py` 在 `do_GET` 里用 `if u.path.startswith('/projects/')` 链式匹配，是从上到下的：

```python
if u.path == '/projects':                              # 精确匹配
    ...
if u.path == '/projects/by-update':                    # ← 必须先于 startswith
    ...
if u.path.startswith('/projects/'):                    # 兜底，会吃掉 by-update
    ...
```

**经验法则**：任何 `by-X` / 具体子路径（`/projects/by-update`、`/projects/featured` 等）必须先于 `{name}` / `startswith` 兜底路由注册。在改之前用 `grep -nE '@app\\.get|if u\\.path'` 列出当前所有路由，确认插入位置不会被子路径兜底捕获。2026-07-19 补充：`/api-docs` 这类新的精确匹配路由在 `app.py` 里同样要插在 `u.path.startswith('/projects/')` 兜底**之前**——本次把它紧跟在 `/projects/by-update` 块后面，避免日后再被路径参数路由吞掉。

---

## 2. 线上跑的 app.py ≠ skill 的 reader_server.py（重要）

2026-07-19 实测发现：`http://<IP>:8081` 跑的是 `<reader-deploy-dir>/app.py`（基于 `http.server.ThreadingHTTPServer` 的旧版实现，16KB），**不是** skill 里的 `scripts/reader_server.py`（FastAPI + uvicorn，24KB）。

两份文件路由结构完全不同：

| 维度 | skill `scripts/reader_server.py` | 线上 `app.py` |
|---|---|---|
| 框架 | FastAPI + uvicorn | ThreadingHTTPServer |
| 路由注册 | `@app.get()` 装饰器 | `do_GET` 里的 if/elif |
| 启动 | `uvicorn scripts.reader_server:app` | `python3 app.py` |
| 路径匹配 | FastAPI 路由解析 | `u.path.startswith(...)` |
| 行数 | ~700 | ~370 |

**部署时必须先确认线上在跑哪一份**：

```bash
# 查 PID 对应的工作目录和启动命令
ss -tlnp | grep 8081
ls -la /proc/<PID>/cwd
cat /proc/<PID>/cmdline | tr '\0' ' '
```

**改接口/路由时**：
1. 如果是 `python3 app.py` 启动的，改 `<reader-deploy-dir>/app.py`
2. 如果是 `uvicorn scripts.reader_server:app` 启动的，改 skill 的 `scripts/reader_server.py`
3. 两份都要改时，**分别写**——不能复制粘贴，因为框架不同
4. 改完重启对应进程，验证 `curl http://127.0.0.1:8081/<新路由>` 返回 200

**长期建议**：未来把线上切到 skill 的 FastAPI 版本，统一维护一份。当前两份并存的状态容易改错文件。

---

## 3. `_project_last_updated()` 实现模式

按内容文件 mtime 排序的核心函数，两份后端共用同一思路：

```python
def _project_last_updated(p: Path) -> float:
    """Latest mtime across content files (md + images), fallback to dir mtime."""
    latest = 0.0
    # Markdown: root + episodes/ + light_novel/
    for pattern in ('*.md', 'episodes/*.md', 'light_novel/*.md'):
        for f in p.glob(pattern):
            try:
                m = f.stat().st_mtime
                if m > latest:
                    latest = m
            except OSError:
                continue
    # Images under known render dirs
    for d in ('rendered', 'render_output', 'images', 'comic_pages'):
        sub = p / d
        if not sub.is_dir():
            continue
        for ext in ('*.png', '*.jpg', '*.jpeg', '*.webp', '*.gif'):
            for f in sub.rglob(ext):
                try:
                    m = f.stat().st_mtime
                    if m > latest:
                        latest = m
                except OSError:
                    continue
    # Fallback: directory mtime
    if latest == 0.0:
        try:
            latest = p.stat().st_mtime
        except OSError:
            pass
    return latest
```

**关键设计决策**：

1. **扫描内容文件，不是目录 mtime**：目录 mtime 只在新建/删除直接子项时变化，章节内容修改不会冒泡。必须扫文件。
2. **跳过元数据占位**：`summary.md`/`characters.md` 等元数据 mtime 也算"内容更新"——用户改章节正文 + 更新角色档案都是有效更新。
3. **图片也要扫**：渲染新图也算更新。`rglob` 而不是 `glob` 因为图片在子目录里。
4. **`OSError` 兜底**：文件被并发删除时不崩。
5. **返回 Unix timestamp**：响应同时给 `last_updated`（float）+ `last_updated_iso`（ISO string），前端用 timestamp 排序、用 ISO 显示。

---

## 4. 完整路由实现（参考）

```python
@app.get("/projects/by-update")
async def list_projects_by_update(
    request: Request,
    limit: int = Query(50, ge=1, le=200),
    content_mode: Optional[str] = Query(None),
):
    await verify_api_key(request)
    if not PROJECTS_ROOT.is_dir():
        return {"projects": [], "count": 0}

    import datetime as _dt
    items = []
    for entry in PROJECTS_ROOT.iterdir():
        if not entry.is_dir() or entry.name.startswith('.'):
            continue
        config = load_json_safe(entry / "config.json")
        stats = _compute_project_stats(entry)
        # content_mode filter
        if content_mode == "light_novel" and stats["novel_chapter_count"] == 0:
            continue
        elif content_mode == "comic":
            is_comic = (
                stats["image_count"] > 0
                or (stats["novel_chapter_count"] == 0 and stats["episode_count"] > 0)
                or "comic" in str(config.get("content_mode", "")).lower()
                or "漫画" in str(config.get("category", ""))
            )
            if not is_comic:
                continue
        last_updated = _project_last_updated(entry)
        items.append({
            "name": entry.name,
            "config": config,
            "stats": {k: stats[k] for k in ("episode_count", "image_count", "novel_chapter_count")},
            "last_updated": last_updated,
            "last_updated_iso": _dt.datetime.fromtimestamp(last_updated).isoformat() if last_updated > 0 else None,
        })
    items.sort(key=lambda x: x["last_updated"], reverse=True)
    return {"projects": items[:limit], "count": len(items), "limit": limit}
```

---

## 5. 前端「最新」视图实现要点

`templates/reader.html` 加入口：

1. **顶部 nav + 移动端底 nav 各加一个按钮**（两处都要改，忘了任何一个都会出现桌面/移动一端没入口）
2. **`setNav` 函数的 `['Home','Cats','Shelf','Rank','Comic']` 数组要加新名字**——否则新按钮永远不会有 `.active` 高亮
3. **相对时间工具函数**：
   ```javascript
   function relTime(ts){
     if(!ts) return '';
     let now = Date.now()/1000, diff = now - ts;
     if(diff < 60) return '刚刚';
     if(diff < 3600) return Math.floor(diff/60) + ' 分钟前';
     if(diff < 86400) return Math.floor(diff/3600) + ' 小时前';
     if(diff < 86400*7) return Math.floor(diff/86400) + ' 天前';
     if(diff < 86400*30) return Math.floor(diff/86400/7) + ' 周前';
     if(diff < 86400*365) return Math.floor(diff/86400/30) + ' 个月前';
     return Math.floor(diff/86400/365) + ' 年前';
   }
   ```
4. **行右侧双行时间显示**：第一行大字相对时间（番茄红高亮），第二行小字 ISO 具体时间（次要灰色），既给人快速判断也保留精确值
5. **接口文档同步**：v1.21.3 起文档**不再**维护在前端 HTML 里——改为在后端 `API_DOCS` 常量（`app.py` / `reader_server.py` 两份都要加）的对应 group 里追加 endpoint 条目，前端 `showApiDoc()` 会自动渲染。详见 `references/reader-api-docs-self-describing-2026-07-19.md`。（2026-07-19 修正：旧版本条写"在 openApiDoc 模态框里加 `<div class=\"api-endpoint\">`"——模态框已移除，硬编码 HTML 文档已被 `/api-docs` 取代。）

---

## 6. 部署后的验证三件套

```bash
# 1. 后端路由通
curl -s 'http://127.0.0.1:8081/projects/by-update?limit=3' | python3 -m json.tool | head -20

# 2. content_mode 过滤生效
curl -s 'http://127.0.0.1:8081/projects/by-update?content_mode=light_novel' | python3 -c "import json,sys;d=json.load(sys.stdin);print(f'ln count: {d[\"count\"]}')"

# 3. 前端 HTML 包含新按钮和新函数
curl -s http://127.0.0.1:8081/reader | grep -c 'showRecent\|by-update'   # 应 ≥3
```

三件套全过才算完。

---

## 7. 同步 skill 模板与线上文件

`templates/reader.html` 是 skill 模板，`<reader-deploy-dir>/reader.html` 是线上跑的副本。**每次改前端必须同步**：

```bash
cp <reader-deploy-dir>/reader.html \
   /root/.hermes/skills/comic-script-generator/templates/reader.html
md5sum <两个文件>  # 验证一致
```

后端同理：如果 skill 的 `scripts/reader_server.py` 也加了对应路由（即使线上跑的是旧 app.py），保持同步以避免下次切到 FastAPI 版本时丢失功能。
