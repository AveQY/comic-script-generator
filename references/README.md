# Comic Script Generator References

## AI Prompt Template
AI 绘图提示词模板（SD/Midjourney/DALL-E 格式），用于漫画 Panel 的生成提示词规范。

## Config Schema
项目配置文件 schema，定义 `config.json` 的字段结构与校验规则。

## Editing Workflow
续写与修改工作流：读取上下文、局部修改、伏笔管理、写作风格延续。

## Hotspot Scraping
热点抓取平台可访问性指南，记录各平台是否可无登录访问及抓取限制。

## Script API Spec
在线接口规范（端点定义、请求/响应格式、错误码），所有在线接口必须遵循此规范。

## Online Reader Deployment
线上 Reader/API 部署记录：站点域名、路由、Nginx 反代、认证方式与常见故障。

## Frontend Optimization
Reader 前端性能优化记录：分页、懒加载、搜索上下文限制、后端分页接口变更与回滚方法。

## Panel Format Generation Lessons
Page/Panel 漫画脚本生成实战经验：格式通过不等于故事连贯、先写 episode beats、保守提取伏笔、连载递进链样例。

## Batch Generation
批量生成架构设计与常见问题。

## Export for Render
从现有漫画稿提取 Panel 内容并转换为 story-renderer 输入脚本的桥接规范。
