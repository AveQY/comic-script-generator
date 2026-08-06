---
name: csg-init
description: >-
  comic-script-generator 的首次 onboarding 与项目初始化。创建项目骨架、选择分镜密度模式、配置项目。
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, terminal
---

## 初始化流程

**首次使用必须初始化：**

1. 询问用户项目保存位置（默认：`~/comic-projects/`）
2. 询问稿子源：
   - [1] 本地文件（从用户电脑选择脚本文件）
   - [2] 在线接口（从远程 API 获取脚本内容）
3. 运行初始化脚本创建项目骨架：
   ```bash
   python scripts/init_project.py "<项目名>" --output <保存位置> --mode B --episodes 6
   ```
   **路径注意：** 当前脚本会在 `<保存位置>/projects/<项目名>/` 下创建项目，而不是直接创建到 `<保存位置>/<项目名>/`。初始化后验证文件时应以脚本输出的 `Project created: ...` 为准，再读取对应路径的 `config.json` / `style_guide.md`。
   脚本会创建完整目录结构和配置文件：
   ```
   projects/<项目名>/
   ├── config.json          # 项目配置（分镜模式、集数、风格等）
   ├── summary.md           # 每集摘要索引
   ├── characters.md        # 角色档案
   ├── foreshadowing.md     # 伏笔追踪
   └── episodes/            # 分集稿子
       ├── ep001_<标题>.md
       ├── ep002_<标题>.md
       └── ...
   ```
3. 如果选择在线接口，收集接口配置：
   - 接口地址（如 `https://api.example.com/v1/generate`）
   - API Key
   - 请求方法（POST/GET）
   - 请求体格式（参考 `references/script-api-spec.md`）
   - 测试接口连通性
4. 将 config.json 内容展示给用户确认，允许修改：
   - `density_mode`：A（对话多镜头少）/ B（平衡）/ C（电影短剧风）
   - `total_episodes`：计划总集数
   - `art_style`：AI 绘图风格描述
5. 配置文件 schema 详见 `references/config-schema.md`
