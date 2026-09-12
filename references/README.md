# Comic Script Generator References

`references/` 共 71 个参考文档，**按需读取，不要一次性全部加载**。子 skill（`skills/csg-*`）会在对应步骤标注需要读取的文件。

> 命名约定：`light-novel-*` 轻小说线 · `reader-*` / `rendering-*` / `manga-*` Reader 与渲染线 · `*-lessons` / `*-pitfall` / `write_file-*` 实战踩坑记录。

## 通用规范与模板

| 文件 | 内容 |
|------|------|
| `ai-prompt-template.md` | AI 绘图提示词模板（SD/Midjourney/DALL-E 格式），漫画 Panel 生成提示词规范 |
| `config-schema.md` | 项目配置文件 schema，定义 `config.json` 字段结构与校验规则 |
| `image-generation-config.md` | 生图接口配置说明 |
| `editing-workflow.md` | 续写与修改工作流：读取上下文、局部修改、伏笔管理、写作风格延续 |
| `export-for-render.md` | 从漫画稿提取 Panel 内容并转换为 story-renderer 输入的桥接规范 |
| `script-api-spec.md` | 在线接口规范（端点定义、请求/响应格式、错误码） |
| `hotspot-scraping.md` | 热点抓取平台可访问性指南（各平台是否可无登录访问及限制） |
| `batch-generation.md` | 批量生成架构设计与常见问题 |
| `batch-fallback-generation.md` | 批量生成的降级/回退策略 |
| `generation-logic-and-style-consistency.md` | 生成逻辑与风格一致性 |
| `novel-outline-style-dimensions.md` | 小说大纲与风格维度 |
| `long-novel-generation.md` | 长篇小说生成 |
| `novel-generation-and-bookshelf.md` | 小说生成与书架 |
| `novel-to-drama-workflow.md` | 小说转短剧工作流 |
| `manga-generation-pipeline.md` | 漫画生成流水线 |
| `full-manga-production.md` | 完整漫画生产流程 |
| `thumb-optimization.md` | 缩略图优化 |
| `skill-privacy-hardening.md` | skill 隐私加固 |
| `skill-production-readiness-audit.md` | skill 生产就绪审计 |

## 漫画质量与验收

| 文件 | 内容 |
|------|------|
| `panel-format-generation-lessons.md` | Page/Panel 生成实战经验：格式通过≠故事连贯、先写 episode beats、保守提取伏笔 |
| `manga-rendering-lessons.md` | 漫画渲染经验 |
| `market-manga-production-lessons.md` | 市场向漫画生产经验 |
| `market-manga-validation.md` | 市场向漫画验收 |
| `delegate-outline-drift.md` | 子代理大纲漂移陷阱 |
| `delegation-format-lessons.md` | 子代理分派格式经验 |

## 轻小说线（light-novel-*，15 篇）

`light-novel-quickstart-recipe.md`（快速上手）、`light-novel-single-script-generation.md` / `light-novel-single-batch-generation.md` / `light-novel-batch-generation.md` / `light-novel-batch-continuation.md`（单章/批量/续写生成）、`light-novel-delegate-batch-pattern.md`（子代理批量模式）、`light-novel-flat-structure.md`（扁平结构）、`light-novel-style-fragmentation.md`（风格碎片化）、`light-novel-tail-degradation.md`（尾部退化）、`light-novel-llm-code-switch.md`（LLM 语码切换）、`light-novel-garbled-text-cleanup.md`（乱码清理）、`light-novel-heredoc-pitfall.md`（heredoc 陷阱）、`light-novel-interrupted-session-continuation.md`（中断会话续写）、`light-novel-bookshelf-reader.md`（书架与 Reader）、`light-novel-reader-debug.md`（Reader 调试）

## Reader 与渲染线

| 文件 | 内容 |
|------|------|
| `local-reader-and-renderer-ops.md` | 本地 Reader/渲染器运维 |
| `local-reader-api.md` | 本地 Reader API |
| `online-reader-deployment.md` | 线上 Reader/API 部署记录：域名、路由、Nginx 反代、认证与常见故障 |
| `novel-reader-deployment.md` | 小说 Reader 部署 |
| `reader-api-docs-self-describing.md` | API 文档自描述接口 |
| `reader-and-manga-logic.md` | Reader 与漫画逻辑 |
| `reader-generation-debug.md` | Reader 生成调试 |
| `reader-homepage-light-novel-ui.md` | Reader 首页轻小说 UI |
| `reader-modal-vs-view.md` | 模态框 vs 独立视图 |
| `reader-render-pitfalls.md` | Reader 渲染陷阱 |
| `reader-rendering-lessons.md` | Reader 渲染经验 |
| `reader-route-ordering-and-by-update.md` | Reader 路由顺序与按更新排序 |
| `rendering-and-reader-ops.md` | 渲染与 Reader 运维 |
| `rendering-reader-lessons.md` | 渲染/Reader 经验汇总 |
| `logic-style-rendering-and-reader-debug.md` | 逻辑/风格/渲染与 Reader 调试 |
| `long-novel-production-and-reader.md` | 长篇生产与 Reader |
| `frontend-optimization.md` | Reader 前端性能优化：分页、懒加载、搜索上下文限制、后端分页接口变更与回滚 |

## 工具陷阱与实战记录

| 文件 | 内容 |
|------|------|
| `file-writing-and-fallback.md` | 文件写入实战经验与回退策略 |
| `patch-intext-pitfall.md` | patch 工具的三重陷阱 |
| `write_file-framework-xml-leak.md` | write_file 框架 XML 泄漏问题 |
| `write_file-paragraph-level-corruption.md` | write_file 段落级损坏问题 |
| `write_file-stream-timeout.md` | write_file 流式超时问题 |

---

*部分早期文档尚未补写单条描述，先按文件名归类；描述与实际内容有出入时以文件正文为准。*
