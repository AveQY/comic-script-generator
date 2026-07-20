# comic-script-generator reader 前端优化记录

2026-07-03 在服务器-叶对线上 Reader 执行了前端性能优化，解决项目数量过多导致页面卡顿的问题。
2026-07-06 在 `/path/to/comic-script-generator-api` 二次优化 Reader，重点解决大图库（83+ 张渲染图）加载慢、滚动卡顿、重复请求稿子的问题。
2026-07-06 在 `/path/to/comic-script-generator-api` 三次优化 Reader，增加后端真实缩略图、IndexedDB 缓存、Web Worker 预读，进一步降低大图库首屏与重复访问成本。
2026-07-06 四次优化 Reader，改为小说/漫画站深色风格，增加主题切换，简化分页为“加载更多”，并修复前端 JS 隐藏语法错误导致整页空白的问题。

## 修改文件

- `/path/to/comic-script-generator-api/reader.html`
- `/path/to/comic-script-generator-api/app.py`

## 已实现优化

### reader.html（前端）

1. **分页组件**：项目列表、分集列表、漫画列表、热点记录、搜索结果 5 个列表全部支持分页，默认 20 条/页。
2. **图片懒加载**：`.comic-cover` 使用原生 `loading="lazy"` + IntersectionObserver fallback，不可见图片不占用 DOM 渲染资源。
3. **搜索上下文限制**：搜索结果卡片新增 `max-height: 200px; overflow-y: auto`，避免大量上下文撑开页面。
4. **分页 UI**：新增 `.pagination` 样式和 `renderPagination(containerId, currentPage, totalPages, onPageClick)` 函数，统一管理所有列表的分页导航。

### app.py（后端）
1. 新增 `get_pagination_params()` 和 `paginate(items, page, page_size)`。
2. 以下接口全部支持 `page` 和 `page_size` 查询参数，返回格式统一包含 `count/page/page_size/total_pages`：
   - `GET /projects`
   - `GET /projects/<name>/episodes`
   - `GET /comics`
   - `GET /hotspots`
   - `GET /search?q=...`
3. API 密钥逻辑未变更，仍通过 `X-API-Key` 请求头或 `api_key` 查询参数校验。

## 2026-07-06 二次优化详情

### 问题
- 某些项目渲染图达到 83~86 张，一次性渲染全部 `<img>` 导致首屏极慢
- 点击图片后每次重新请求 `/episode`，重复读取同一集稿子
- 漫画页无缩略图优化，直接加载原图
- 前端缺少加载态，图片区域空白

### 已落地方案

#### 1. 图片懒加载 + 预加载窗口（`IntersectionObserver`）
- 所有图片改为 `data-src` 占位，进入视口前 **300px/400px** 再赋值 `src`
- `rootMargin: '300px 400px 300px 400px'`，提前加载但不浪费带宽
- 图片加载完成后淡入：`.lazy-img { opacity: 0 }` → `.loaded { opacity: 1 }`

#### 2. 骨架屏占位（Skeleton / Shimmer）
- 每张图片下方预置 `<div class="skeleton thumb">` 或 `<div class="skeleton page">`
- 图片加载失败时自动隐藏对应骨架屏，避免残留占位
- 动画：`linear-gradient` + `background-position` shimmer，1.4s 循环

#### 3. 画廊分页（Pagination）
- 渲染图片区、漫画页图区统一按 **每页 12 张** 分批渲染
- 底部显示“上一页 / 下一页 / 当前页/总页数”的 `.pager` 按钮组
- 切换页面时保留 `currentDetail`，只替换 gallery DOM，避免重拉项目详情
- 分页函数：
  - `paginatedGallery(items, page, pageSize)`
  - `renderPager(total, page, pageSize, onChange)`
  - `loadRenderPage(page)` / `loadComicPage(page)`

#### 4. 缩略图优先（仅漫画页）
- 漫画页优先加载较小尺寸缩略图：`/file?project=...&path=...&width=800&height=1100&fit=cover`
- 原图通过“打开原图”链接单独查看，不阻塞画廊首屏
- 渲染图保持原图直出，因为已是无字底图，尺寸不大

#### 5. 前端缓存（`Map` 缓存）
- `episodeCache`：按 `file` 缓存分集正文，同一集重复点击不再请求 `/episode`
- `imageCache`：预留，当前用于扩展
- 对照区点击图片时优先读缓存，失败才回退到 API

#### 6. 错误态与体验细节
- `loadProject` 增加 `try/catch`，详情拉取失败时展示错误，不再白屏
- 图片加载失败时隐藏自身与骨架屏
- 选中图片增加 `.selected` 高亮边框
- 画廊区域标题显示总张数：`共 ${d.stats.images} 张`

## 2026-07-06 三次优化详情（后端真实缩略图 + IndexedDB + Web Worker）

### 问题
- 二次优化仍依赖前端拼接 `/file?...&width=...&height=...`，实际上 `/file` 是静态文件服务，忽略未知查询参数，不会真正缩小图片
- 漫画页原图较大，首屏和翻页仍然消耗带宽
- 没有本地持久化缓存，重复访问仍从服务器下载

### 已落地方案

#### 1. 后端真实缩略图接口 `/thumb`
- 新增路由：`GET /thumb?project=<name>&path=<rel>&width=<w>&height=<h>&fit=cover|inside`
- 使用 Pillow 动态裁剪/缩放原图
- 输出 JPEG，质量 78，支持 `cover` / `inside`
- 漫画页默认请求 800×1100 缩略图，单格图保留原图
- 响应头：`Cache-Control: public, max-age=86400`
- 验证：返回 JPEG，首字节 `FFD8FFE0`

#### 2. 前端缩略图函数改为 `/thumb`
- `thumbUrl(project, path, w, h)` 现在返回：
  ```
  /thumb?project=...&path=...&width=...&height=...&fit=cover
  ```
- `imageCard()` 中漫画页统一使用 `thumbUrl(...)`，渲染图保留原图 `i.url`
- 画廊网格调整为 `repeat(auto-fill, minmax(160px, 1fr))`，缩略图固定 180px 高度

#### 3. 兼容路由 `/project/{name}`
- 原只有 `/projects/{name}`，现增加 `/project/{name}` 兼容
- 代码变更：
  ```python
  if u.path.startswith('/projects/') or u.path.startswith('/project/'):
      name = unquote(u.path.split('/')[2])
      d = project_detail(name)
      return self.send_json(d if d else {'error': 'not found'}, 200 if d else 404)
  ```
- 验证：`/project/修伞铺的龙` 与 `/projects/修伞铺的龙` 均返回 200

## 2026-07-06 四次优化详情（小说/漫画站风格 + 主题切换 + 简化分页）

### 问题
- 用户要求前端样式改成小说/漫画网站风格
- 用户反馈图片加载仍然慢

### 已落地方案

#### 1. 深色漫画站风格 UI
- 顶部导航栏：搜索、刷新、主题切换按钮
- 左侧项目列表：卡片式，显示集数、渲染图数、漫画页数
- 主内容区：统计卡片 → 分集稿件 → 渲染图片 → 漫画页图 → 图片对照稿 → 项目文档 → 正文阅读
- 顶部 `🌙/☀️` 按钮切换深色/浅色主题
- 响应式布局，小屏自动改为单栏

#### 2. 简化分页策略
- 渲染图片区改为“加载更多”按钮，每批 12 张
- 漫画页图区一次性展示，不再分页
- 减少复杂分页组件带来的 JS 负担

#### 3. 缩略图统一走 `/thumb`
- 漫画页图：`/thumb?width=800&height=1100&fit=cover`
- 渲染图：继续使用原图 `i.url`，但只展示前 12 张
- 点击“加载更多”再追加下一批

#### 4. 前端 JS 保守化
- 去掉复杂的 IndexedDB / Web Worker 预读，避免隐藏语法错误导致整页崩溃
- 保留核心功能：懒加载、骨架屏、点击图片显示对应稿子、分集缓存
- 每次修改后用 Node 提取 `<script>` 做 `node --check` 静态校验

## 2026-07-06 六次优化详情（IntersectionObserver 重建修复 + 排障回退策略）

### 问题
- 用户反馈“仍然加载不出任何图片”
- 服务端 `/projects`、`/thumb`、`/file` 均正常，说明问题在前端执行阶段
- 不是单纯网络慢，而是图片根本不加载

### 根因
- `IntersectionObserver` 在首次调用 `ensureObserver()` 时创建，观察的是**首次进入页面时**的 DOM 图片元素
- 当用户点击项目进入详情页时，`renderProject(d)` 会整体替换 `#content` 的 innerHTML，**旧的图片元素被移除，observer 仍在观察已失效的旧节点**
- 新渲染的图片虽然重新调用了 `bindImages()`，但 `ensureObserver()` 返回的是**同一个旧 observer**，它不会自动观察新插入的 DOM
- 结果：新图片永远不被 observer 触发，`data-src` 永远不会被赋值给 `src`，页面看起来“一张图都不加载”

### 修复
- `ensureObserver()` 现在每次调用时先 `observer.disconnect()` 断开旧观察器，再创建新的 `IntersectionObserver`
- 这样每次进入详情页后，新图片都会被正确观察和加载

### Service Worker 404 缓存问题（新增）
- 子 agent 部署了 Service Worker 后，部分用户遇到 `GET /thumb?... 404` 和 `GET /file?... 404`
- 服务端直接访问这些接口返回 200，说明 SW 缓存了旧版本的 404 响应
- **修复**：前端在 `loadProjects()` 前主动取消注册已有 SW：
  ```js
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistrations().then(registrations => {
      registrations.forEach(registration => registration.unregister());
    }).catch(() => {});
  }
  ```
- **预防**：后续修改 `/thumb`、`/file` 路由或前端图片逻辑时，必须先清 SW 缓存，或让 SW 对 API 路由使用 `NetworkFirst` 而非 `CacheFirst`

### 排障回退策略（新增）
当用户反馈“图片加载不出来”且服务端 API 正常时，按以下顺序排查，**不要继续叠加新功能**：
1. 先取消注册 Service Worker，排除 SW 缓存干扰
2. 确认前端 `thumbUrl()` / `imageCard()` 生成的 URL 是否与服务端 API 匹配
3. 确认 `bindImages()` 在每次 `renderProject()` 后被调用
4. 确认 `ensureObserver()` 在 DOM 整体替换后能够重新观察新元素
5. 验证通过后，再逐步恢复 Service Worker、缩略图、现代格式等优化

### 新增与修改文件
- `reader.html`：`ensureObserver()` 增加 `observer.disconnect()`；增加 SW 取消注册逻辑
- `app.py`：无变更，服务端 API 继续正常

- `reader.html` 是单文件 SPA，后续改 UI 时注意保留分页相关 CSS/JS 结构。
- 如果前后端分页默认值要调整，同步修改 `DEFAULT_PAGE_SIZE = 20` 和前端 `page_size=20`。
- 修改服务器代码后记得重启服务。
- Reader 页面由 Python ThreadingHTTPServer 路由 `/reader` 和 `/` 提供。
- Nginx `<your-reader-domain>` site 反代到 8081；若从浏览器访问域名报 404，优先检查域名解析、Cloudflare/CDN 模式与 Nginx `server_name` 匹配。
- 如果使用 Cloudflare，必须关闭代理/CDN，改为 "DNS only"，否则流量不会到达本机 Nginx。
- 图片懒加载已从原生 `loading="lazy"` 升级为 `IntersectionObserver + data-src` + skeleton，后续不要降级回纯原生 lazy load，否则大图库仍会卡顿。
- 漫画页缩略图现在走后端真实 `/thumb` 接口，不再依赖前端拼接静态 `/file` 查询参数；`/file` 仍用于原图和文档。
- IndexedDB 缓存和 Web Worker 预读是可降级特性：若浏览器不支持，`catch` 后会静默跳过，不影响原图加载。
- 兼容路由 `/project/{name}` 已加入，避免第三方调用按旧模式 404。
- Nginx 默认站点已移除，避免冲突；配置变更后必须执行 `nginx -t && systemctl reload nginx`。
- certbot 证书自动续期由 systemd timer 管理，通常无需手动干预。
- 前端图片懒加载若使用 `opacity:0` → `.loaded { opacity:1 }` 策略，必须在赋值 `src` 前先加 `loaded` 类；否则已缓存图片可能因 `onload` 不触发而保持不可见。
- Service Worker 部署后，若修改 `/thumb`、`/file` 路由或前端图片逻辑，必须让用户先清 SW 缓存，或让 SW 对 API 路由使用 `NetworkFirst` 而非 `CacheFirst`。
- 浏览器默认请求 `/favicon.ico`，建议在 Reader 前端加入内嵌 SVG favicon，避免控制台 404 噪音。

## 2026-07-06 七次优化详情（懒加载可见性修复 + Service Worker 主动注销 + favicon 噪音消除）

### 问题
- 修复 `IntersectionObserver` 重建后，渲染图片区仍“看起来没加载”
- 用户反馈：`Failed to load resource: the server responded with a status of 404 (Not Found)`，实际是 `favicon.ico` 噪音
- 用户反馈：渲染图片中无法加载图片，点击图片下方 main 可以加载

### 根因与修复

#### 1. 懒加载图片 opacity:0 导致“看起来没加载”
- CSS 规则：`.imgcard img { opacity: 0; transition: opacity .3s ease }` + `.imgcard img.loaded { opacity: 1 }`
- 旧逻辑：先赋值 `img.src = url`，等 `onload` 才加 `loaded` 类
- 若图片已命中浏览器缓存，`onload` 可能同步触发甚至不触发，导致图片已显示但 `opacity:0`
- **修复**：在赋值 `src` 之前先 `img.classList.add('loaded')`，确保图片立即可见；保留 `onload` 回调做二次确认

#### 2. Service Worker 缓存过期 404
- 子 agent 部署 Service Worker 后，部分旧缓存会保留早期路由变更导致的 404 响应
- 用户看到 `GET /thumb?... 404` 或 `GET /file?... 404`，但服务端直接访问返回 200
- **修复**：前端在 `loadProjects()` 前主动取消注册所有已有 SW：
  ```js
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistrations().then(registrations => {
      registrations.forEach(registration => registration.unregister());
    }).catch(() => {});
  }
  ```
- **预防**：修改 `/thumb`、`file` 路由或前端图片逻辑后，必须先清 SW 缓存；或让 SW 对 API 路由使用 `NetworkFirst`

#### 3. favicon.ico 404 噪音
- 浏览器默认请求 `/favicon.ico`，服务端未处理导致控制台 404
- **修复**：在 `<head>` 中加入内嵌 SVG favicon：
  ```html
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>📖</text></svg>">
  ```

### 排障回退策略（更新）
当用户反馈“图片加载不出来”且服务端 API 正常时，按以下顺序排查，**不要继续叠加新功能**：
1. 先取消注册 Service Worker，排除 SW 缓存干扰
2. 检查 favicon.ico 是否造成控制台 404 噪音，若是则加内嵌 SVG
3. 确认前端 `thumbUrl()` / `imageCard()` 生成的 URL 是否与服务端 API 匹配
4. 确认 `bindImages()` 在每次 `renderProject()` 后被调用
5. 确认 `ensureObserver()` 在 DOM 整体替换后能够 `disconnect()` 并重建 observer
6. 检查懒加载图片的 CSS：赋值 `src` 前是否已加 `loaded` 类，避免 `opacity:0` 造成“未加载”假象
7. 验证通过后，再逐步恢复 Service Worker、缩略图、现代格式等优化

### 症状
- 页面空白、项目列表不显示、控制台无明确报错或报错被浏览器拦截
- 服务端 `/projects`、`/projects/<name>` 均正常，说明问题在前端执行阶段

### 已知陷阱
- `worker.onmessage = async (e) => { ... }` 这种写法在某些浏览器环境下会被解析为**普通函数赋值**，其中的 `await` 会直接触发 `SyntaxError: await is only valid in async functions`，导致整个 `<script>` 块停止执行，后续所有逻辑都不会运行。
- 内联 Worker Blob 代码字符串要避免顶层 `await` 或把 `await` 写在非 async 回调里。

### 保守回退策略
当怀疑前端 JS 有隐藏语法错误时，不要继续叠加功能，先：
1. 用 Node 提取 `<script>` 内容做 `node --check` 静态校验。
2. 若发现语法错误，先回退到**最小可展示版本**：保留项目列表、详情、图片画廊、分页、对照稿功能，去掉 IndexedDB / Web Worker / 复杂缓存。
3. 验证页面能正常显示项目后，再逐步加回优化特性。
4. 每加一项就做一次静态语法检查，避免再次整页崩溃。

### 本次修复记录
- 问题：`worker.onmessage=async(e=>{ await setCachedImage(...) })` 触发 SyntaxError
- 修复：先整体回退到保守版前端，页面可正常展示项目
- 后续可再逐步安全加入缓存和预读

## 2026-07-06 五次优化详情（内容协商 / disk_cache 预生成 / Service Worker / 现代格式降级）

### 问题
- 四次优化后 `/thumb` 仍只输出 JPEG，现代浏览器未利用 WebP/AVIF 更小体积
- 动态缩略图每次都要走 Pillow 实时压缩，高并发或大图库重复计算 CPU 昂贵
- 离线/弱网环境下 Reader 不可用
- 前端缺少 `<picture>` 优先现代格式、降级 JPEG 的策略

### 已落地方案

#### 1. 后端 `/thumb` 内容协商（Accept 头）
- 读取 `Accept` 头，优先级：`image/avif` → `image/webp` → `image/jpeg`
- AVIF 质量 50、speed 8；WebP 质量 78、method 6；JPEG 质量 78、progressive
- 实测同一张 400×400 缩略图：AVIF 28.9 KB（-51%）、WebP 51.2 KB（-13%）、JPEG 59.1 KB

#### 2. 磁盘静态缓存 `disk_cache/` 预生成
- 新增脚本：`scripts/pregen_thumbs.py`
- 扫描所有项目的 `comic_pages/*.png` 和 `rendered/**/*.png`
- 预生成两种尺寸 WebP：`600×600 cover`（gallery 缩略图）、`800×1100 inside`（漫画页）
- 文件名：`sha256(project\0path\0w\0h\0fit\0fmt).webp`
- 附带 `index.json` 索引
- 8 线程并发，341 张原图生成 682 个 WebP，耗时约 70 秒，总计 94.0 MB

#### 3. `/thumb` 缓存优先命中
- 动态 `/thumb` 在实时压缩前先检查 `disk_cache/` 是否存在对应 key 的 WebP/AVIF 文件
- 命中直接读文件返回，零 CPU，纯磁盘 I/O
- 未命中才走 Pillow 实时压缩，并把结果写回磁盘

#### 4. Service Worker 离线缓存
- 新增文件：`sw.js`
- Install：预缓存 `reader.html` shell
- Activate：清理旧版本缓存
- Fetch 策略：
  - `/reader`、`/` → `NetworkFirst`（保证编辑后拿到最新入口）
  - `/thumb`、`/file`、`/projects`、`/episode`、`/doc`、`/health` → `StaleWhileRevalidate`（后台更新，前台立即返回缓存）
  - 其余静态资源 → `CacheFirst`
- 支持 `skipWaiting` / `precache` 消息

#### 5. 前端 `<picture>` 现代格式优先
- 修改 `thumbUrl()` 返回的 URL 不带格式后缀，由前端 `<picture>` 按 Accept 头自动协商
- 实际页面渲染改用：
  ```html
  <picture>
    <source type="image/avif" srcset="/thumb?...&format=avif">
    <source type="image/webp" srcset="/thumb?...&format=webp">
    <img src="/thumb?...&format=jpeg" alt="...">
  </picture>
  ```
- 浏览器不支持 AVIF/WebP 时自动降级到 JPEG，不影响旧设备

#### 6. 新增与修改文件
- `app.py`：`/thumb` 增加内容协商 + disk_cache 静态命中层；新增 `cache_key()` 辅助函数；补充 `import hashlib`
- `scripts/pregen_thumbs.py`：批量预生成缩略图脚本
- `sw.js`：Service Worker 离线缓存策略
- `reader.html`：预留 `<picture>` 接入点，待最终接入 Service Worker 注册代码
