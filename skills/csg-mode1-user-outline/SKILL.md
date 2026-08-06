---
name: csg-mode1-user-outline
description: >-
  根据用户提供的故事情节大纲生成详细 Page/Panel 分镜脚本，含角色档案、伏笔追踪、自动更新与验证。
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, terminal
---

### 模式一：用户提供大纲

1. **接收大纲**
   - 用户提供故事大纲、主题、角色设定等
   - 确认项目名称（新项目 or 续写现有项目）

2. **项目结构检查**
   - 如果是现有项目，读取：
     - `项目名/summary.md`：每集摘要
     - `项目名/characters.md`：角色档案
     - `项目名/foreshadowing.md`：未回收伏笔
   - 如果是新项目，创建目录：
     ```
     projects/<项目名>/
     ├── summary.md          # 每集摘要索引
     ├── characters.md       # 角色档案
     ├── foreshadowing.md    # 伏笔追踪
     └── episodes/           # 分集稿子
         ├── ep001_<标题>.md
         ├── ep002_<标题>.md
         └── ...
     ```

3. **分镜密度选择（重要）**
   - 如果用户未在初始化时选择，现在必须询问：
   ```
   请选择分镜密度模式：
   1. 对话多，镜头少（传统漫画风，每集30-40场景）
   2. 一个对话对应一个镜头（平衡模式，每集50-60场景）
   3. 一段对话多个镜头（电影短剧风，每集150-250场景）
   ```
   - 将选择更新到项目 `config.json`

4. **生成分镜脚本**
   - 根据大纲 + 项目上下文 + 分镜密度模式生成详细分镜
   - **每个场景必须附带 AI 绘图提示词**，格式详见 `references/ai-prompt-template.md`
   - 每个场景包含：
     - **页码与格号**：`## Page X` / `### Panel X`，禁止继续使用 `## Scene X`
     - **格子**：普通格/横向大格/竖向窄格/半页大格/跨页大格/三连小格/无边框格等
     - **画面**：人物表情、动作、环境细节、光线氛围、关键物件
     - **构图**：远景/中景/特写/俯拍/仰拍/过肩/双人构图等
     - **气泡**：角色、位置、气泡类型、台词
     - **旁白**：旁白框位置与内容；没有则写“无”
     - **拟声**：拟声字、位置、字体表现；没有则写“无”
     - **转场**：动作/视线/时间跳切/情绪/悬念/对比/场景/翻页钩子
     - **AI 提示词**：正向/反向提示词，风格部分只能来自 `style_guide.md`

5. **保存和维护**
   - 保存稿子到 `episodes/epXXX_<标题>.md`
   - 运行自动更新脚本提取结构化信息：
     ```bash
     python scripts/update_project.py episodes/ep001_xxx.md --project-dir projects/<项目名> --episode-num 1
     ```
     脚本自动完成：
     - 提取新角色 → 追加到 `characters.md`
     - 扫描伏笔关键词 → 追加到 `foreshadowing.md`
     - 生成摘要条目 → 追加到 `summary.md`
     - 更新 Panel 数/对话数 → 更新 `config.json`
   - 运行质量验证脚本检查生成质量：
     ```bash
     python scripts/validate_episode.py episodes/ep001_xxx.md --project-dir projects/<项目名>
     ```
   - 运行角色一致性检查：
     ```bash
     python scripts/consistency_check.py episodes/ep001_xxx.md --project-dir projects/<项目名>
     ```
   - 所有检查通过后，项目文件已自动更新完成
