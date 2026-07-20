# 轻小说 Reader 前端调试经验（2026-07）

适用：`comic-script-generator` 的 Reader/API 前端新增或维护「轻小说/番茄小说风」阅读模式时。

## 背景
在为 `DemoProjectA` 增加轻小说模式时，后端 `/projects`、`/light-novels` 均正常返回，但前端一直停在“加载中”。根因不是 API，而是 `reader.html` 中新增模式切换代码后多出一个 `}`，导致整个 `<script>` 语法错误，`loadProjects()` 没有执行。

## 必做验证
修改 `reader.html` 后必须提取 `<script>` 并用 Node 做语法检查：

```bash
python3 - <<'PY'
from pathlib import Path
import re
html = Path('/path/to/comic-script-generator-api/reader.html').read_text(encoding='utf-8')
m = re.search(r'<script>([\s\S]*)</script>', html)
Path('/tmp/reader_script.js').write_text(m.group(1), encoding='utf-8')
print('script bytes', len(m.group(1)))
PY
node --check /tmp/reader_script.js
```

通过后再验证接口：

```bash
curl -sS http://127.0.0.1:8081/projects | python3 -m json.tool | head
curl -sS 'http://127.0.0.1:8081/light-novels?project=506%E5%8F%B7%E5%90%88%E7%A7%9F%E5%B1%8B' | python3 -m json.tool | head
```

## 轻小说模式实现要点

### 后端接口
新增 `GET /light-novels?project=<name>`：
- 读取 `<project>/light_novel/ln*.md`
- 返回 `file/title/chars/url`
- `url` 指向 `/file?project=<name>&path=<rel>`

注意：浏览器/前端必须使用 `encodeURIComponent` 生成 URL；shell/curl 直接写中文查询参数可能触发 HTTP server 的 bad request。测试中文路径时优先用 Python `urllib.parse.quote`。

### 前端模式切换
Header 增加两个按钮：
- `🖼 漫画`：原有项目详情、分集稿、图库、对照稿
- `📖 小说`：轻小说目录和章节阅读器

切换逻辑：
- `switchMode('novel')` 时调用 `/light-novels`
- 项目加载后可以后台预取小说列表，但不要阻塞漫画模式加载
- 如果小说列表为空，显示“暂无轻小说内容，请先生成轻小说”

### 番茄小说风 UI
推荐样式：
- 米黄阅读纸背景：`#faf7f2`
- serif 字体：`Noto Serif SC`, `STSong`, `SimSun`, `Songti SC`
- 宽松行距：`line-height: 2.0~2.2`
- 正文最大宽度：`720~800px`
- 首行缩进：`text-indent: 2em`
- 顶部阅读进度条
- A+/A- 字号调节
- 上一章/下一章导航

### 插图占位符
`export_light_novel.py` 会插入：

```markdown
<!-- ILLUST_1 -->
```

前端解析 Markdown 时不能直接跳过该行。应保留占位符到 HTML 字符串中，随后替换成插图块；否则插图永远不会显示。

错误：
```js
if(line.startsWith('<!-- ILLUST_')) continue;
```

正确：
```js
if(line.startsWith('<!-- ILLUST_')){ html += line; continue; }
```

## 常见故障排查

1. 页面一直“加载中”
   - 先检查 JS 语法：`node --check /tmp/reader_script.js`
   - 再看 `/projects` 是否正常
   - 若 API 正常但页面不动，通常是前端脚本语法错误导致 `loadProjects()` 未执行

2. 小说章节能列出但正文打不开
   - 检查 `/file?project=...&path=light_novel/...` 的 URL 编码
   - 前端用 `fetch(novel.url)`，后端返回的 URL 应可直接访问

3. 插图不显示
   - 检查 Markdown 中 `<!-- ILLUST_N -->` 是否被保留到 HTML 中
   - 检查 `currentDetail.images` 是否有可用渲染图
   - 若暂时没有图，用 `· · ·` 分隔符兜底，不要让页面报错

4. 旧页面缓存
   - Reader 调试阶段继续主动 unregister Service Worker，避免旧 JS 缓存导致“已修复但浏览器仍报错”
   - 用户侧提示强刷：Windows `Ctrl+F5`，Mac `Cmd+Shift+R`
