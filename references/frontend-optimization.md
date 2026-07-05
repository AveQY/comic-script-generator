# comic-script-generator reader 前端优化记录

2026-07-03 在服务器-叶（`YOUR_SERVER_IP`）对线上 Reader 执行了前端性能优化，解决项目数量过多导致页面卡顿的问题。

## 修改文件

- `<user-home>/comic-script-generator-api/reader.html`
- `<user-home>/comic-script-generator-api/app.py`

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

## 快速回滚

```bash
cd <user-home>/comic-script-generator-api
cp app.py.bak.20260703_043201 app.py
# reader.html 的原始备份为 reader.html.bak.20260703_043201
sudo systemctl restart comic-api.service
```

## 维护注意事项

- `reader.html` 是单文件 SPA，后续改 UI 时注意保留分页相关 CSS/JS 结构。
- 如果前后端分页默认值要调整，同步修改 `DEFAULT_PAGE_SIZE = 20` 和前端 `page_size=20`。
- 修改服务器代码后记得重启 `comic-api.service`。
- Reader 页面由 Flask 路由 `/reader` 和 `/` 提供；浏览器直接访问 `/reader.html` 会 404，前端登录验证调用的是 `/projects?api_key=...`。
- Nginx `comic-script-generator.YOUR_DOMAIN` site 反代到 8081；default site 也反代到 8081，但只有带正确 `Host` 头时才命中。若从浏览器访问站点报 404，优先检查域名解析与 Cloudflare SSL 模式。
