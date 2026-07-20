# 生成阶段漫画逻辑与画风统一经验

## 触发场景

当用户反馈“生成的图片不符合正常漫画逻辑”“画风不够统一”时，不应只重跑生图或靠后处理补救。应回到生成稿与渲染输入阶段修正：

1. episode 的 `画面` 字段是否具体可画。
2. `render_input` 是否把对白错误塞进生图 prompt。
3. `style_guide.md` 是否有角色视觉指纹和统一风格锁。
4. 导出的每个 prompt 是否注入相同角色/场景/线条/网点规则。

## 生成稿阶段硬规则

`画面` 字段必须直接可画，写清：

- 角色姓名、年龄感、外貌/服装/发型
- 关键物件和物件位置
- 动作前后顺序
- 地点和光线
- 表情与情绪变化
- 画面焦点和对白气泡留白

禁止抽象模板句：

- “普通日常场景”
- “异常事件突然出现”
- “主角靠近异常源”
- “关键配角登场”
- “世界观第一次展开”
- “危机升级”
- “情感冲突爆发”
- “关键线索出现”
- “结合本作设定”

出现这些词时应视为稿子不合格，而不是进入渲染。

## 验证脚本要求

`validate_episode.py` 应检查：

- `画面` 是否过短，短于约 35 字通常不可稳定渲染。
- 是否包含上述抽象模板词。
- 如果 episode 明确写 `**预计 Panel 数**：12个` 这类短篇规格，应按短篇实际 panel 数验证，不强制套用模式 B 的 40+ Panel。

## 渲染输入要求

`export_for_render.py` 应保证：

- 生图 prompt 只画干净漫画格，不负责生成中文文字。
- 不把气泡对白塞到旁白字段喂给生图模型。
- 正向 prompt 不混入 `photorealistic, 3d render, oil painting, blurry, watermark` 等反向词。
- 每个 prompt 都包含：
  - `no text`
  - `no letters`
  - `leave empty space for speech bubbles`
  - `same character design`
  - `same face`
  - `same hairstyle`
  - `same outfit`
  - `same manga line style`
  - `same screentone density`

## 画风统一做法

在项目 `style_guide.md` 增加：

```markdown
## 角色视觉指纹
- 主角：年龄、国籍/体型、发型、脸型、服装、道具、固定表情特征。
- 重要配角：同样记录稳定外貌和服装。
- 场景统一：固定地点、光线、关键道具、时代/天气、画面质感。

## 风格说明
统一黑白/彩色、线条粗细、网点密度、明暗、气泡留白、是否允许文字等。
```

导出脚本应读取 `## 角色视觉指纹` 和 `## 风格说明`，并把它们注入每个镜头 prompt。仅靠泛泛的 “modern manga style” 无法保证角色脸、服装、线条密度统一。

## 推荐流程

```text
生成 episode
→ validate_episode.py 拦截抽象画面
→ export_for_render.py 注入风格锁和角色指纹
→ render_images.py 生无字图
→ overlay_comic_text.py 叠加中文对白/拟声
→ compose_manga_pages.py 合成漫画页
→ Reader 对照图和稿子检查逻辑/画风
```

## 失败时优先级

1. 画面不合逻辑：先修 episode 的 `画面/构图`，不要直接重跑图片。
2. 中文文字乱码：生图 prompt 加 no text/no letters，使用 overlay 脚本叠字。
3. 角色/画风不统一：先补 `style_guide.md` 角色视觉指纹和 consistency lock，再重导 render_input。
4. 单张缺图：只补缺失 scene，随后重跑 overlay 和 compose，不重跑全项目。
