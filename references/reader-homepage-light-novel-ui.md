# Reader 首页与轻小说书架调试经验（2026-07-07）

## 背景
用户指出：Reader 前端不应只有一个项目详情页；应先进入首页，再有小说分类和书架展示小说，风格高仿番茄小说。

## 持久 UI 规则
- `/reader` 首屏应是首页/书架，而不是自动进入单个项目详情。
- 首页结构建议：顶部品牌（番茄红）、左侧分类频道、主区欢迎 Banner、分类 Chips、书架卡片。
- 分类至少包含：全部、日常、恋爱、治愈、搞笑、漫画。
- 作品以“书卡”展示：封面、故事名、简介、分类标签、章节数、图片数。
- 点击书卡后进入该书详情/阅读；默认进入轻小说模式，保留漫画模式切换。
- 用户偏好浅色、清爽、番茄小说风：米黄正文阅读区、宋体/楷体、较大行距、A+/A- 字号调节、上下章导航、阅读进度条。

## API/前端实现要点
- 后端新增 `GET /light-novels?project=<name>`：读取 `light_novel/ln*.md`，返回 `{project,count,novels:[{file,title,chars,url}]}`。
- 前端状态：`novelMode=true` 作为默认；`showHome()` 渲染首页；`openBook(name)` 打开书并进入小说模式。
- Header 品牌点击应回到首页：`<h1 onclick="showHome()">🍅 番茄书架</h1>`。
- 左侧不再是单纯“项目列表”，而是“分类频道”；分类点击只过滤书架，不直接进入项目详情。
- `/file` URL 必须使用 `encodeURIComponent`，中文项目名/路径不能裸拼到 URL，否则 HTTP 解析可能 400。

## 调试强制步骤
每次改 `reader.html` 内联 JS 后，必须提取 `<script>` 并跑语法检查，避免页面一直“加载中”：

```bash
python3 - <<'PY'
from pathlib import Path
import re
html = Path('/path/to/comic-script-generator-api/reader.html').read_text(encoding='utf-8')
m = re.search(r'<script>([\s\S]*)</script>', html)
Path('/tmp/reader_script.js').write_text(m.group(1), encoding='utf-8')
PY
node --check /tmp/reader_script.js
```

曾出现的问题：`renderComicDetail()` 附近多出一个 `}`，导致整个 JS 不执行，页面停留在“加载中”。`node --check` 能直接定位。

## 验证命令
```bash
curl -fsS http://127.0.0.1:8081/health
curl -fsS http://127.0.0.1:8081/projects
curl -fsS 'http://127.0.0.1:8081/light-novels?project=506%E5%8F%B7%E5%90%88%E7%A7%9F%E5%B1%8B'
curl -fsS http://127.0.0.1:8081/reader | grep -E 'home-hero|bookshelf|showHome|番茄书架'
```

## 交付口径
修复后回复应说明：首屏是首页，左侧是分类频道，主区是书架卡片；点击书卡进入小说阅读；强刷浏览器可清掉旧缓存。
