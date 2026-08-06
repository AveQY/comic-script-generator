---
name: comic-script-generator
description: 根据大纲或热点生成漫画分镜稿/小说/短剧分镜脚本，支持项目管理、角色档案、伏笔追踪。总协议+路由器，具体工作流在 skills/ 子 skill 中。
version: 1.26.5
tags: [creative, comic, screenplay, storyboard]
---

# 漫画脚本生成器 — 总协议 & 路由器

本文件是 **总协议 + 路由器**。每个模式的具体工作流在 `skills/csg-*/SKILL.md` 各子 skill 中。

**首次使用必须先读 `skills/csg-init/SKILL.md` 初始化项目。**

## 路由表（触发词 → 子 skill）

| 用户说 | 调用子 skill | 前置条件 |
|--------|------------|---------|
| "初始化" / "创建项目" / "init" | `csg-init` | 无（入口） |
| "写分镜" / "根据大纲写" / "生成第一集" | `csg-mode1-user-outline` | 项目已初始化 |
| "抓热点" / "热点话题" / "今天有什么热点" | `csg-mode2-hotspot` | 已 init，网络通畅 |
| "续写" / "继续写第N集" / "修改xxx" | `csg-mode3-continue` | 项目已有至少一集 |
| "批量生成" / "批量 N 个" / "auto" | `csg-mode4-batch` | 已 init |
| "渲染" / "出图" / "生成漫画图片" | `csg-mode5-render` | 项目有稿子 + story-renderer |
| "写小说" / "轻小说" / "番茄小说" / "书架" | `csg-mode6-light-novel` | 已 init |
| "短剧" / "分镜脚本" / "△剧本" / "拍摄脚本" | `csg-mode7-drama` | 有小说源章节 |
| "爆款评估" / "哪些是爆款" / "评估潜力" | `csg-mode8-evaluation` | 有已生成项目 |
| "分镜密度" / "Page/Panel 模板" / "格式参考" | `csg-densities` | 任意时刻 |
| "角色模板" / "伏笔模板" / "摘要模板" | `csg-templates` | 任意时刻 |
| "部署" / "Reader" / "启动服务器" | `csg-deployment` | 任意时刻 |
| "市场验收" / "漫画评分" / "market validation" | `csg-market-validation` | 有完成的漫画项目 |

**Mode detection**（首次接非 init 触发词时执行）：
1. 检查项目目录是否存在 `config.json` — 无 → 提示先初始化
2. 检查 `content_mode` 判断漫画/小说/混合模式
3. 路由到对应子 skill

## 隐私与本地敏感配置（强制）

- 真实 API token、Authorization/Bearer、Cookie、私有域名、服务器公网 IP、VPN/代理订阅、数据库密码等敏感信息，**只能保存在本地私有配置文件**，不能写入 `SKILL.md`、README、references、示例文件、项目稿件或任何准备提交/发布的文件。
- 生图接口配置优先读取：`--config` → `$COMIC_IMAGE_CONFIG` → `~/.config/comic-script-generator/image_config.json`。
- 推荐私有配置路径：`~/.config/comic-script-generator/image_config.json`，权限设置为 `600`。
- skill 目录内只允许保留 `config.example.json` 占位模板；真实 `config.json` 即使被 `.gitignore` 忽略，也不作为推荐存放位置。
- 发布、同步、打包 skill 前必须运行 `python3 scripts/privacy_check.py`，确认没有真实 token、私有 IP/域名或本机路径泄漏。
- **备份文件禁止上传**：`.gitignore` 必须包含 `*.bak*`、`*.backup*` 模式，防误提交。
- 禁止写真实服务器路径、公网 IP、真实项目名、代理端口、API Key。
- 通用占位：`<user-home>/`、`<reader-deploy-dir>/`、`<projects-dir>/`、`DemoProjectA`。
- 每次清理后运行 grep 确认无泄漏。
- 发布/README 文档中提及路径变更时要使用中性描述，避免暴露隐私清理痕迹。

## 更新检查（每次使用前）

**每次启动该 skill 前，必须先检查是否有更新：**

1. 运行 `python scripts/check_update.py`
2. 脚本会自动：
   - 检测 GitHub 网络连通性
   - 比对本地与远程 `origin/main` 的 commit SHA
   - 输出 JSON 结果（`network_available`、`update_available`、`action`）
3. 如果网络不通或无法获取 commit，脚本返回 `action: "skip"`，继续正常使用当前 skill
4. 如果 `action: "update_needed"`，先执行 `git pull origin main` 更新 skill，再继续使用

**注意：** 只有这个 skill 目录下包含完整的 git 历史，`check_update.py` 依赖 git 命令正常工作。

## 更新地址

源仓库：https://github.com/AveQY/comic-script-generator

## 核心强制规则（跨模式共享）

### 1. Page/Panel 漫画格式（模式一二三四五通用）

所有漫画脚本必须使用 `## Page X` / `### Panel X` 结构，每个 Panel 必须包含：
`格子`、`画面`、`构图`、`气泡`、`旁白`、`拟声`、`转场`、`AI 提示词`

没有气泡/旁白/拟声时也必须写"无"。

### 2. 禁止 Shell heredoc 写入任何稿子文件

- ❌ `cat >> << 'EOF'` — 实测导致内容丢失
- ❌ `cat > << 'EOF'` — 全角字符+反引号混合不可靠
- ❌ `python3 << PYEOF` + `r"""…"""` — 损坏中文正文
- ✅ 使用 `write_file` 工具或 Python `open().write()` 写入
- 写入后必须验证完整性（`wc -l -c` + `grep "^### Panel" | wc -l`）

### 3. 每集生成后必须验证

```bash
python scripts/validate_episode.py episodes/epXXX_xxx.md --project-dir projects/<项目名>
python scripts/consistency_check.py episodes/epXXX_xxx.md --project-dir projects/<项目名>
```

验证不通过时必须修复后再继续。

### 4. AI 提示词格式

- 必须使用 fenced code block 格式（````text … ````），不能使用 inline 单行格式
- 正向提示词以 `masterpiece, best quality, <project_style_keywords>` 开头
- 必须包含 `no text, no letters, leave empty space for speech bubbles`
- 反向提示词固定不变，含 `watermark, text, signature`

### 5. 文件命名

- 集数用三位数：ep001, ep002, ep010, ep100
- 标题用故事核心：`ep001_天台相遇.md`
- 小说章节：`ln001_章名.md`

### 6. 热点抓取限制

- ✅ 百度热搜（top.baidu.com/board?tab=realtime）：无需登录，优先使用
- ❌ 微博热搜：需要登录，会重定向
- ❌ 知乎热榜：需要登录，返回空页面
- 浏览器超时/不可用时改用 JSON API：`curl "https://top.baidu.com/api/board?platform=pc&tab=realtime"`

### 7. terminal() workdir 中文路径限制

`terminal()` 的 `workdir` 参数**不兼容含中文的路径**。改为在 `command` 中用 `cd <路径>` 进入目录。

### 8. 始终加载 skill 后再写稿/写小说

只要涉及漫画脚本生成或轻小说生成，必须先通过 `skill_view(name='comic-script-generator')` 加载本 skill 再开始。

### 9. 更新 skill 版本号规则

更新 skill 功能时必须同步更新 frontmatter 的 `version:` 字段和 changelog 条目。

## 用户工作流偏好

- **先确认再执行**：涉及多步修改、设计方案、或可能影响现有文件的变更时，先说明方案并等待确认。
- **明确指令必须原样执行**：用户点名要的具体交付物，必须按字面执行，不得擅自替换。
- **风格统一优先**：同一项目的所有集必须使用相同的 AI 绘图风格。
- **Reader 新功能用独立视图，不用模态框**。
- **API 文档走自描述接口**。
- **双副本同步**：修改后立即确认状态「已更新本地，未 commit/push」。
- **分阶段交付**：优先分"生成稿子"和"渲染漫画"两个阶段。
- **只审格式，不审剧情**。
- **并行 dispatch 而非串行等待**：有 N 个独立任务时一次性 dispatch 所有批次。
- **不允许 commit/push 除非用户明确说"commit"或"push"**。

## 共享基础设施

### 参考资料（references/）

- `references/ai-prompt-template.md` — AI 绘图提示词模板
- `references/config-schema.md` — 项目配置文件 schema
- `references/editing-workflow.md` — 续写与修改工作流
- `references/hotspot-scraping.md` — 热点抓取平台可访问性指南
- `references/script-api-spec.md` — 在线接口规范
- `references/file-writing-and-fallback.md` — 文件写入实战经验
- `references/panel-format-generation-lessons.md` — Page/Panel 生成实战经验
- `references/light-novel-*.md` — 轻小说相关参考文档
- `references/patch-intext-pitfall.md` — patch 工具的三重陷阱
- `references/reader-*.md` — Reader 前端相关参考
- `references/manga-*.md` — 漫画渲染相关参考
- `references/delegate-outline-drift.md` — 子代理大纲漂移陷阱
- 完整列表见 skill 目录下的 `references/`

### 脚本工具（scripts/）

- `scripts/init_project.py` — 项目初始化
- `scripts/update_project.py` — 自动更新项目文件
- `scripts/validate_episode.py` — 分集验证
- `scripts/consistency_check.py` — 角色一致性检查
- `scripts/export_for_render.py` — 导出渲染输入
- `scripts/render_images.py` — 渲染图片
- `scripts/overlay_comic_text.py` — 叠加中文对白气泡
- `scripts/compose_manga_pages.py` — 合成漫画页
- `scripts/export_light_novel.py` — 轻小说导出
- `scripts/validate_light_novel.py` — 轻小说验证
- `scripts/verify_light_novel_delivery.py` — 投递级验证
- `scripts/scan_unicode_contamination.py` — Unicode 块污染扫描
- `scripts/update_long_novel_context.py` — 长篇上下文压缩
- `scripts/validate_long_novel.py` — 长篇小说验收
- `scripts/convert_to_script.py` — 短剧分镜转换
- `scripts/batch_generate.py` — 批量生成
- `scripts/reader_server.py` — Reader 服务器
- `scripts/check_update.py` — 更新检查
- `scripts/privacy_check.py` — 隐私扫描
- `scripts/repair_manga_logic.py` — 修复漫画逻辑
- `scripts/stitch_localized_chapter.py` — 拼接长图
- 完整列表见 skill 目录下的 `scripts/`

## 更新日志

- v1.26.0（2026-08-05）：新增模式八（小说爆款评估）
- v1.25.0–v1.21.0（2026-07-19~21）：Reader 改造、短剧分镜、快速直转、单文件 SPA 重构
- v1.20.0（2026-07-12）：整合 Reader 服务器到 skill
- v1.19.0–v1.1.0（2026-07-06~09）：轻小说路线、批量生成、渲染流程、格式升级
- v1.0.0（2026-06-?）：初始版本
- **v1.26.5（2026-08-06）**：重构为路由式架构。主 SKILL.md 精简为总协议+路由器，8 个模式 + 5 个辅助功能拆分为独立子 skill 文件（`skills/csg-*/SKILL.md`），仿 cheat-on-content 设计。每个子 skill 独立维护，降低上下文加载开销。