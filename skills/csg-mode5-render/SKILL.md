---
name: csg-mode5-render
description: >-
  将 comic-script-generator 的分镜稿通过 story-renderer 渲染为漫画图片。支持导出、并发渲染、气泡叠加、漫画页合成。
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, terminal
---

## 模式五：脚本生成后渲染为漫画图片（集成 story-renderer）

**触发条件**：用户已有 comic-script-generator 项目，想将某集分镜稿渲染为漫画图片或视频。

**前置条件**：
- 项目已通过 comic-script-generator 初始化并生成了至少一集稿子
- story-renderer skill 已安装且初始化（配置了图片生成 API）
- 项目的 style_guide.md 存在且完整

**工作流程**：

1. **选择项目与剧集**
   - 展示已有项目列表，用户选择目标项目
   - 展示该项目下已完成的剧集，用户选择要渲染的剧集
   - 用户可选择渲染全部集数或指定集数

2. **生成 story-renderer 输入脚本**
   - 运行脚本从 episode 稿子提取可渲染内容：
     python scripts/export_for_render.py episodes/epXXX_xxx.md --project-dir projects/<项目名> --style-guide projects/<项目名>/style_guide.md
   - 脚本自动完成：
     - 读取每集 Page X / Panel X 结构
     - 提取每个 Panel 的画面、构图、AI 提示词字段
     - 注入 style_guide.md 的固定正向/反向提示词
     - 生成 story-renderer 兼容的输入脚本（镜头 N 格式）
     - 如果有气泡台词，自动转为旁白字段
     - 输出到 projects/<项目名>/render_input/epXXX_<标题>_render.md

3. **预览与确认**
   - 展示提取的镜头数和 Estimated 成本（基于 story-renderer 的 API 定价）
   - 用户可编辑、跳过、或调整单个镜头的提示词
   - 确认后调用 story-renderer 的渲染流程

4. **调用 story-renderer 渲染**
   - 使用 story-renderer 的 render 命令（或等效流程）
   - 传入生成好的输入脚本
   - 渲染参数：
     - 默认宽高比：9:16（竖屏漫画）
     - 一致性策略：固定 seed + 角色指纹（从 style_guide.md 和 characters.md 提取）
     - 负面提示词：来自 style_guide.md
   - 生成图片保存到 projects/<项目名>/rendered/epXXX/ 目录
   - 支持断点续传：已渲染的 Panel 不重复生成

5. **结果回写**
   - 渲染完成后，将图片路径回写到 episode 稿子的对应 Panel 下
   - 格式：在 Panel 末尾追加 渲染图：rendered/ep003/scene_05.png
   - 运行 update_project.py 更新项目状态

**参数说明**：
- --episodes / -e：要渲染的集数（如 1,2,3 或 all）
- --panels / -p：指定 Panel 范围（如 1-10）
- --width / -W：图片宽度，默认 1024
- --height / -H：图片高度，默认 1792
- --no-confirm：跳过确认直接生成

**注意事项**：
- 渲染前必须确认 style_guide.md 存在，否则终止并提示先生成
- 同一个 Panel 可能因对话量大而拆分为多个渲染镜头，由 export_for_render.py 自动处理
- 渲染所需 API token/endpoint 必须来自本地私有配置：`--config`、`COMIC_IMAGE_CONFIG` 或 `~/.config/comic-script-generator/image_config.json`；禁止放入 skill 目录真实配置。
- 如果 story-renderer 未初始化，引导用户先运行“初始化 story-renderer”

### 出图路线选择

在启动渲染流程前，先判断故事类型：
- **对话密集/日常/情感类** → 推荐模式六（轻小说 + 关键场景插图），每集 5-8 张图，成本约 1/8。
- **动作/视觉驱动类** → 走本模式五完整漫画渲染。

