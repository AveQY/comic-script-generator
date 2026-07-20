# Skill 生产化与脱敏审计记录

适用于将 `comic-script-generator` 从内部自用工具整理为可交接、可发布或可生产运行的 skill 时使用。

## 触发场景

- 用户要求检查 skill 是否完整、是否包含隐私数据、逻辑是否清晰、能否投入实际生产。
- 准备把本地 skill 同步到 GitHub、分享给他人、迁移到新机器或作为正式生产流程使用。
- skill 内新增了部署、Reader、图片 API、渲染或长篇小说生产相关脚本后。

## 必查项

1. **敏感信息扫描**
   - 搜索：`Bearer`、`authorization`、`api_key`、`token`、`secret`、`password`、真实图片 API 域名、真实服务器 IP、VPN/订阅信息。
   - 真实密钥不得放在 skill 目录，尤其不能放在 `config.json` 后随 skill 一起发布。
   - 推荐改为：`--config` 或环境变量 `COMIC_IMAGE_CONFIG=/path/to/private/config.json`。
   - 发布包中只保留 `config.example.json`，用 `<YOUR_IMAGE_API_ENDPOINT>`、`<YOUR_TOKEN>` 等占位符。

2. **私有环境信息脱敏**
   - 对外发布前替换真实部署信息：服务器 IP、个人域名、本机路径、`/path/to/server-home/...`、`/path/to/comic-projects/...` 等。
   - 内部生产文档可保留路径，但应明确标注“本机部署示例”，避免写成通用规则。

3. **版本一致性**
   - `SKILL.md` frontmatter 的 `version:`、`README.md` badge、更新日志要一致。
   - 如果本地有大量未提交/未跟踪文件，不要宣称这是干净发布版；先整理 changelog 和文件清单。

4. **逻辑清晰度检查**
   - `SKILL.md` 应保留 class-level 主流程：漫画路线、小说路线、渲染路线、Reader 接入、验证命令、红线。
   - 会话实战细节、错误转录、历史坑点下沉到 `references/`，不要让主文件变成平铺日志。
   - 检查重复章节，尤其是“模式五/模式六/更新日志/示例模板”是否重复。

5. **可运行性验证**
   - 运行 `python3 -m py_compile scripts/*.py`。
   - 抽查关键脚本 `--help`：`init_project.py`、`validate_episode.py`、`render_images.py`、`validate_light_novel.py`、`validate_long_novel.py`。
   - 检查必备脚本是否存在：初始化、更新、验证、一致性、导出渲染、渲染、叠字、合页、拼长图、轻小说导出、长篇上下文压缩。

## 生产结论模板

```text
内部生产：可用 / 需先清理后可用 / 暂不可用
对外发布：可发布 / 需脱敏后发布 / 暂不可发布
阻塞项：<密钥、版本、重复章节、脚本失败等>
建议动作：<脱敏、版本同步、主文件瘦身、添加发布检查脚本>
```

## 重要经验

一个 skill 可以“能干活”但还不是“可发布产品”。判断时要分开回答：

- **内部生产可用性**：脚本能否运行、流程是否完整、Reader/渲染/验证是否闭环。
- **对外发布准备度**：是否脱敏、版本是否一致、文档是否通用、git 工作区是否干净。

如果发现真实 Bearer Token 或私有 API 配置，必须直接标记为发布阻塞项。