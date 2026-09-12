# 漫画渲染与 Reader 经验汇总（合并版）

> 本文合并自 6 篇历史踩坑记录（reader-rendering-lessons / rendering-reader-lessons / manga-rendering-lessons / rendering-and-reader-ops / reader-and-manga-logic / logic-style-rendering-and-reader-debug，原文见 2026-09-12 之前的 git 历史），按主题去重整理。
>
> **触发场景**：用户反馈"生成的图片不符合正常漫画逻辑""画风不统一""Reader 看不到新图/加载更多报错"时，按本参考执行，不要只重跑生图。

## 1. 生成阶段必须完成漫画逻辑

不要先生成抽象模板稿再靠后处理修复——后处理只能兜底旧稿，不能成为正常流程依赖。`episodes/*.md` 的每个 `Panel` 在生成时就必须满足：

- `画面` 是可直接绘制的具体画面：角色姓名/外貌、关键物件、动作前后顺序、地点、光线、表情、画面焦点、气泡留白。
- 每个 Panel 必须承接上一格的动作、视线、物件位置或情绪变化，读者按图序能理解故事。
- 生成后用 `validate_episode.py` 拦截抽象模板句和过短 `画面`；短篇若写了 `预计 Panel 数：12个`，验证不应强制按 B 模式 40+ Panel 误判。

**抽象模板句黑名单**（出现在 `画面` 字段即视为不合格稿）：

```text
普通日常场景 / 异常事件突然出现 / 主角靠近异常源 / 关键配角登场 / 世界观第一次展开 /
规则第一次被验证 / 主角做出第一次主动选择 / 危机升级 / 情感冲突爆发 / 关键线索出现 /
结尾钩子 / 结合本作设定 / 环境信息明确
```

## 2. 画风统一：角色视觉指纹 + 风格锁

仅靠 `modern manga style` 等泛词不够。项目 `style_guide.md` 应包含：

```markdown
## 角色视觉指纹
- 主角/配角：年龄、国籍/人种、发型、脸型、体型、固定服装、固定道具。
- 场景统一：固定场景、光线、道具、时间段、氛围。

## 风格说明
统一为黑白/彩色的具体漫画风格；统一外轮廓线、网点密度、明暗策略；
所有镜头角色保持相同发型、服装、脸型和道具。生图不生成中文文字，只留对白气泡空间。
```

`export_for_render.py` 应读取 `## 角色视觉指纹` 和 `## 风格说明`，注入每张图 prompt 并追加：

```text
CONSISTENCY LOCK: same character design, same face, same hairstyle, same outfit, same manga line style, same screentone density across all panels
```

## 3. 生图与叠字分工（两段式管线）

中文对白/拟声**不要**交给生图模型——它经常漏字、乱码，且 `text`/`watermark` 类反向词本来就在抑制文字。正确链路：

```text
无字干净漫画图 → overlay_comic_text.py 叠加中文对白/拟声 → compose_manga_pages.py 合页
```

- 所有生图 prompt 包含：`no text, no letters, no watermark, leave empty space for speech bubbles`。
- `export_for_render.py` 应清理正向 prompt，避免混入 `photorealistic`, `3d render`, `blurry`, `watermark`, `readable text` 等反向词。
- 叠字默认只做角色对白气泡 + 拟声；**旁白默认不上图**（会让页面显得杂乱、插画感），需要时提供 `--include-narration` 类开关。
- CJK 字体：Ubuntu 先 `apt-get install -y fonts-noto-cjk fontconfig`，用 Noto Sans CJK 保证中文渲染。
- 叠字若失败需要重做，先从 `scene_XXX.url.txt` 保存的 URL 恢复干净底图，**不要在已叠字的图上反复叠**。

**生图接口配置**（凭证只放私有配置，永不进公开文档）：

```json
{
  "image_generation": {
    "endpoint": "https://.../v1/images/generations",
    "authorization": "Bearer <token>",
    "model": "gpt-image-2",
    "size": "1024x1024",
    "timeout_seconds": 300
  }
}
```

- 超时给足 120–300 秒；返回 `data[0].b64_json` 或 `data[0].url` 都要支持，URL 响应时保存 `scene_XXX.url.txt` 备份以便恢复原始图。

## 4. 渲染并发与多项目并行

单项目已验证参数：

```bash
python3 scripts/render_images.py render_input/ep001_xxx_render.md \
  --output-dir rendered/ --limit 12 --workers 5 --retries 2 --sleep 0.2
```

- `workers=5` 可稳定完成 12 张短篇渲染；出现 429/401/5xx 先补失败单张，持续失败再降 `--workers 3`。
- 失败后不要重跑整个项目，按缺失的 `scene_XXX.png` 补图。
- 结果先输出到测试目录，验收后再复制到默认 `rendered/`、`localized/`、`comic_pages/`，不要直接覆盖 Reader 默认目录。

多项目并行（subshell + wait）：

```bash
for P in <project1> <project2> <project3>; do
  (
    EP=$(find "$P/episodes" -maxdepth 1 -type f -name 'ep001_*.md' | head -n1)
    python3 scripts/export_for_render.py "$EP" --project-dir "$P" --style-guide "$P/style_guide.md"
    RENDER=$(find "$P/render_input" -maxdepth 1 -type f -name '*_render.md' | head -n1)
    python3 scripts/render_images.py "$RENDER" --limit 1 --sleep 0
  ) &
done
wait
```

## 5. 验证链路与冒烟测试

- **先 `--limit 1` 冒烟**：验证文件真实存在、非零大小、尺寸/格式正确，而不是只看 API 返回成功；通过后再放开批量。
- 完整交付前实际跑通全链路：

```text
生成/写入 episode → validate_episode.py → export_for_render.py → render_images.py
→ overlay_comic_text.py → compose_manga_pages.py → Reader 可访问
```

- 批量脚本 LLM 接口失败但当前会话仍可生成时，按兜底流程手写项目文件继续验证，不要停在脚本失败报告。

## 6. Reader 前端坑（高频）

| 坑 | 修法 |
|---|---|
| "加载更多"写死 `loadMore('render', 12)` | 维护全局游标 `nextRenderIndex`，进项目时重置为 PAGE_SIZE，每次 `slice(start, end)` 追加并更新游标，剩余 0 时移除按钮 |
| 追加图片破坏画廊布局 | 用 `insertAdjacentHTML('beforeend', ...)`，不要把额外 wrapper `<div>` 塞进 `.gallery` |
| 重渲染后缩略图仍旧 | `/thumb` 缓存键必须包含源文件 `mtime + size`；调试时可清空 disk_cache、响应头 `max-age=300, must-revalidate` |
| Service Worker 缓存旧 404 | 调试时 `navigator.serviceWorker.getRegistrations().then(rs => rs.forEach(r => r.unregister()))` |
| `await` 报错后续全挂 | 所有调用 `await api(...)` 的函数声明为 `async`，用 `node --check` 检查内联脚本 |
| 画廊空白但图片能加载 | CSS opacity 初始 0 / observer 未触发：项目切换或 innerHTML 替换后断开旧 `IntersectionObserver` 重建；调试先用简单 `<img data-src>` |
| flex 左列表不滚动 | `min-height: 0; flex: 1; overflow-y: auto; -webkit-overflow-scrolling: touch` |
| 用户找不到项目 | Reader 左侧优先显示 `config.title` 而非目录名；排查 `/projects` 返回的 `name` 与 `title` 映射 |

## 7. 部署现实核查

`references/online-reader-deployment.md` 描述的线上 Reader **不一定**存在于当前主机。声称"在运行"之前先核实：

- 文档端口（通常 8081）有进程监听
- 预期服务/进程存在（`comic-api.service`、`app.py`、Flask/FastAPI 等）
- 部署目录存在

若都不在，如实说 Reader 未在运行，并提供本地 Reader/API 的启动方案，不要暗示远程部署存在。

## 8. 项目命名与清理

- 项目目录用**故事标题**命名（如 `云端便利店`），不用技术批次名（`async_comic_001_*`）。
- 失败/空项目（`episodes=0`、`images=0`、`status=planning`）应归档出 Reader 可见根目录，不污染项目列表。
- 删除项目必须先明确规则（如用户说"只保留 X"），删除后用 `/projects` 确认 API 只返回目标项目。

## 9. 用户偏好速记

- Reader 浅色、清爽、类似番茄小说网：顶部搜索、左侧项目卡片（故事名优先）、右侧内容分区（统计/分集/画廊/对照稿/文档/正文）。
- 长批量任务要安全并行 + 后台跟踪 + 完成后给出具体验证摘要。
- 高质量"手绘感"输出：先写带明确格间连续性的 page beats，再生成面板图，再叠字合页——模板化的稿子无论如何排版都读起来不像漫画。
