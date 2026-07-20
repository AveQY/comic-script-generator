# Reader 自描述 API 文档接口（/api-docs）

**日期**：2026-07-19
**触发**：用户原话「你要有一个接口时获取接口文档内容的」

## 核心模式

把 API 文档做成一个**真实接口**而不是硬编码的 HTML/MD 文件，让文档成为**单一事实源**：

```
GET /api-docs?format=json   → 结构化 dict（前端渲染用）
GET /api-docs?format=md     → Markdown 字符串（导出用）
```

**架构要点**：
1. 后端定义 `API_DOCS` 常量（dict），包含 title/version/base_url/auth/env/groups[]/errors[]/security 字段
2. 路由同时返回两种格式（`format=json|md`，默认 json）
3. **`/api-docs` 自己也写进 `API_DOCS['groups']` 里**——自描述完整
4. 前端 `showApiDoc()` 异步 `fetch('/api-docs?format=json')` → 用 `renderApiDocs(d)` 函数渲染到 `#main`
5. 加新接口只改后端常量一处，刷新前端就看到最新文档

## 为什么这样比硬编码 HTML 好

| 维度 | 硬编码 HTML（旧） | /api-docs 接口（新） |
|---|---|---|
| 单一事实源 | 前端 HTML + 后端代码两处 | 后端 `API_DOCS` 一处 |
| 维护成本 | 加接口要改两处 | 只改后端常量 |
| 机器可读性 | 无法 | 可 curl / jq / 程序化消费 |
| 前端新鲜度 | 改完要重启+刷新 | 刷新即可 |
| 文档自描述 | 不包含自己 | 包含 `/api-docs` 本身 |
| 状态动态 | 静态写死 | `auth.enabled` 等可动态反映运行时配置 |

## API_DOCS 结构示例

```python
API_DOCS = {
    'title': 'Reader API 文档',
    'version': '1.0.0',
    'base_url': 'http://localhost:8081',
    'auth': {
        'enabled': bool(API_KEY),  # 运行时动态
        'env_var': 'COMIC_READER_API_KEY',
        'methods': ['?api_key=<KEY>', 'X-API-Key: <KEY>'],
    },
    'env': [
        {'name': 'COMIC_PROJECTS_ROOT', 'desc': '...'},
        ...
    ],
    'groups': [
        {
            'name': '📚 项目（Projects）',
            'endpoints': [
                {
                    'method': 'GET',
                    'path': '/projects',
                    'desc': '...',
                    'params': [{'name': 'search', 'desc': '...'}],
                    'example': "curl '...'",
                },
                ...
            ],
        },
        # ... 最后一组是 '📚 元信息'，包含 /api-docs 自己
    ],
    'errors': [{'code': 401, 'desc': '...'}, ...],
    'security': '路径穿越防护说明...',
}
```

## 路由实现（旧版 app.py / ThreadingHTTPServer 风格）

放在 `/projects/{name}` 兜底**之前**（参考 `reader-route-ordering-and-by-update-2026-07-19.md`）：

```python
if u.path == '/api-docs':
    fmt = qs.get('format', ['json'])[0]
    if fmt == 'md':
        return self.send_json({'format': 'markdown', 'content': api_docs_markdown()})
    return self.send_json({'format': 'json', 'content': api_docs_json()})
```

## Markdown 渲染函数

```python
def api_docs_markdown():
    d = API_DOCS
    lines = [f"# {d['title']}", '']
    lines.append(f"**基础 URL**：`{d['base_url']}`  ·  **版本**：`{d['version']}`")
    lines.append('')
    # auth / groups / errors / security 各 section
    for group in d['groups']:
        lines.append(f"## {group['name']}")
        for ep in group['endpoints']:
            lines.append(f"### `{ep['method']} {ep['path']}`")
            lines.append(ep['desc'])
            if ep.get('params'):
                lines.append('**参数：**')
                for p in ep['params']:
                    lines.append(f"- `{p['name']}` {p['desc']}")
            if ep.get('example'):
                lines.append('```bash')
                lines.append(ep['example'])
                lines.append('```')
    return '\n'.join(lines)
```

## 前端动态渲染

替换硬编码 HTML，改为：

```javascript
async function showApiDoc(){
  setNav('Api');
  let main = document.getElementById('main');
  main.innerHTML = '<div class="empty">📖 加载接口文档…</div>';
  try{
    let resp = await api('/api-docs?format=json');
    let d = resp.content;
    main.innerHTML = `<section class="section">${renderApiDocs(d)}</section>`;
  }catch(e){
    main.innerHTML = '<div class="empty">加载失败：'+esc(e.message||e)+'<br><br><button class="btn primary" onclick="showApiDoc()">重试</button></div>';
  }
  window.scrollTo(0,0);
}

function renderApiDocs(d){
  // 用 d.groups / d.auth / d.env / d.errors 拼 HTML
  // 标题旁标注 "数据来自 /api-docs"，让用户知道这是动态加载的
  // auth.enabled 显示 🔒/🔓 标识
}
```

## 前端展示要点

1. 副标题标注 `数据来自 /api-docs` 让用户知道这是动态加载
2. `auth.enabled` 为 true 时显示 🔒 认证已启用，false 时显示 🔓 未启用
3. 加载失败给"重试"按钮，不静默吞掉
4. 仍走 `setNav('Api')` + 独立视图模式（见 `reader-modal-vs-view-2026-07-19.md`）

## 验证三件套

```bash
# 1. JSON 格式
curl -s http://127.0.0.1:8081/api-docs?format=json | jq '.content.groups | length'

# 2. Markdown 格式
curl -s http://127.0.0.1:8081/api-docs?format=md | jq -r '.content' | head -20

# 3. 前端可访问
curl -s http://127.0.0.1:8081/reader | grep -c 'renderApiDocs\|/api-docs'
```

## 何时用这个模式

- API 接口数 ≥5，文档需要长期维护
- 前后端分离，前端需要展示文档
- 文档可能被其它工具消费（CI 检查、SDK 生成、README 同步）
- 接口列表会随时间增长

**不适合**：接口极少（<3）且永不变动的项目——硬编码更省事。

---

## 文档字段 richness：只写 params+example 不够（2026-07-19 补）

**触发**：同一会话内用户连续问了两个本可由文档直接回答的问题——「获取完整文章内容的接口是哪个」（需要在 `/doc` `/episode` `/file` 三兄弟中选对）和「`/files/xxx.txt` 为什么 404」（把 query 形式当成路径形式写）。

**教训**：接口文档只写 `method/path/desc/params/example` 不够。用户在做选择时还需要：

| 字段 | 作用 | 例子 |
|---|---|---|
| `returns` | 返回结构（JSON 包裹？原始字节？） | `{"project":"...","content":"<完整 Markdown>"}` vs `原始字节流` |
| `note` | 适用场景 + 兄弟接口区分 + 易错点 | `读轻小说章节用它；/episode 只访问 episodes/ 子目录` |
| `guides[]` | 跨接口使用指南 + 常见错误对照 | `怎么读完整一本书` / `❌ /files/x → ✅ /file?project=&path=` |

**最低限度**：当一组接口里有 ≥2 个语义相近的兄弟（如 `/doc` vs `/episode` vs `/file`），每个都必须写 `note` 说明"什么时候用它而不是兄弟"；当用户可能拼错 URL 形式（`/files/{name}` vs `/file?project=&path=`）时，必须在 `guides[]` 里写一段"常见错误 URL"对照表。

**API_DOCS 增量字段示例**：

```python
{
    'method': 'GET', 'path': '/doc',
    'desc': '获取【项目内任意 Markdown 文档】完整内容（...light_novel/ln001.md 等）。读轻小说章节就用它。',
    'params': [
        {'name': 'project', 'desc': '项目名（必填，URL 编码）'},
        {'name': 'file', 'desc': '文档文件名（必填），如 light_novel/ln001.md 或 characters.md'},
    ],
    'returns': '{"project":"...","file":"...","content":"<完整 Markdown 文本>"}',
    'example': "curl 'http://localhost:8081/doc?project=DemoProjectB&file=light_novel/ln001.md'",
    'note': '前端阅读器读章节正文用的就是它。/episode 只访问 episodes/ 子目录；/file 不包 JSON 壳返回原始字节。',
}

# 顶层新增 guides[]
'guides': [
    {
        'title': '📖 怎么读"完整一本轻小说"',
        'steps': [
            '① GET /projects/{name} → 拿到 light_novels 数组（含每章 file 路径）',
            '② 对每个 chapter.file 调 GET /doc?project={name}&file={chapter.file}',
            '③ 拼接所有 chapter 的 content 字段即为完整书稿',
        ],
        'example': "# 1. 拿章节列表\ncurl 'http://localhost:8081/projects/DemoProjectB' | jq '.stats.novel_chapters'\n\n# 2. 取第 1 章正文\ncurl 'http://localhost:8081/doc?project=DemoProjectB&file=light_novel/ln001.md' | jq -r '.content'",
    },
    {
        'title': '⚠️ 常见错误 URL',
        'steps': [
            '❌ /files/{project}/{path}     → 路由不存在（404）',
            '❌ /file/{project}/{path}      → 路由不存在（404）',
            '✅ /file?project={name}&path={path}   → 正确格式',
            '✅ /doc?project={name}&file={file}    → 读 markdown 正文推荐',
        ],
        'example': "# 错误\ncurl 'http://localhost:8081/files/某项目/some.txt'   # → 404\n\n# 正确\ncurl 'http://localhost:8081/file?project=某项目&path=some.txt'",
    },
]
```

**前端 `renderApiDocs` 对应增量**：

```javascript
// endpoint 卡片在 example 下加 returns 块 + note tip
${ep.returns ? `<div class="api-params"><strong>返回：</strong><code>${esc(ep.returns)}</code></div>` : ''}
${ep.note ? `<div class="api-note">${esc(ep.note)}</div>` : ''}

// groups 之后渲染 guides 一节
let guidesHtml = (d.guides||[]).length ? `
  <h3>📚 使用指南</h3>
  ${d.guides.map(g=>`
    <div class="api-endpoint">
      <div class="api-desc" style="font-weight:700">${esc(g.title)}</div>
      <div class="api-params">${g.steps.map(s=>`<div>${esc(s)}</div>`).join('')}</div>
      ${g.example ? `<div class="api-example">${esc(g.example)}</div>` : ''}
    </div>
  `).join('')}` : '';
```

**Markdown 渲染函数同步**：`api_docs_markdown()` 也要处理 `returns` / `note` / `guides[]` 三个新字段——`returns` 渲染为 json fenced block，`note` 渲染为 `> 💡 ...` 引用，`guides[]` 渲染为独立"📚 使用指南"section。

## 相关 reference

- `reader-modal-vs-view-2026-07-19.md` — 前端展示用独立视图不用模态框
- `reader-route-ordering-and-by-update-2026-07-19.md` — 后端路由顺序陷阱
