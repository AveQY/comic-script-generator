# 2026-07 漫画生成、渲染与 Reader 调试经验

本记录来自一次完整的“稿子 → render_input → 生图 → 叠字 → 合页 → Reader 验收”调试，适用于后续漫画项目生产。

## 1. 生成稿子阶段就要保证漫画逻辑

不要先生成抽象模板稿再靠后处理修复。`episodes/*.md` 的每个 `Panel` 在生成时就必须满足：

- `画面` 是可直接绘制的具体画面：角色姓名/外貌、关键物件、动作前后顺序、地点、光线、表情、画面焦点都要明确。
- 禁止抽象模板句：
  - “普通日常场景”
  - “异常事件突然出现”
  - “主角靠近异常源”
  - “关键配角登场”
  - “世界观第一次展开”
  - “危机升级”
  - “情感冲突爆发”
  - “关键线索出现”
  - “结合本作设定”
- 每个 Panel 必须承接上一格的动作、视线、物件位置或情绪变化。
- 生成后必须用 `validate_episode.py` 检查抽象模板句和过短画面描述。

## 2. 画风统一需要角色视觉指纹 + 风格锁

仅靠“modern manga style”等泛词不够。项目 `style_guide.md` 应增加：

```markdown
## 角色视觉指纹
- 主角：年龄、国籍/人种、发型、脸型、体型、固定服装、固定道具、必须保持一致的特征。
- 配角：同上。
- 场景统一：固定场景、光线、道具、时间段、氛围。

## 风格说明
统一为黑白/彩色的具体漫画风格；同一角色必须保持相同发型、服装、脸型和道具。生图不生成中文文字，只留对白气泡空间。
```

`export_for_render.py` 应读取 `## 角色视觉指纹` 和 `## 风格说明`，把它们注入每一张图的 prompt，并追加：

```text
CONSISTENCY LOCK: same character design, same face, same hairstyle, same outfit, same manga line style, same screentone density across all panels
```

## 3. 生图不要生成中文文字

中文对白/拟声不要交给生图模型。正确链路：

```text
无字干净漫画图 → overlay_comic_text.py 叠加中文对白/拟声 → compose_manga_pages.py 合页
```

所有生图 prompt 应包含：

```text
no text, no letters, no watermark, leave empty space for speech bubbles
```

## 4. 并发渲染参数

`render_images.py` 已验证可用：

```bash
python3 scripts/render_images.py <render_input.md> \
  --output-dir <rendered_dir> \
  --limit 12 \
  --workers 5 \
  --retries 2 \
  --sleep 0.2
```

经验：
- `workers=5` 可稳定完成 12 张短篇漫画渲染。
- 如果出现 429、401、5xx，先补失败单张；如果持续失败，再降到 `workers=3`。
- 失败后不要重跑整个项目，按缺失 `scene_XXX.png` 补图。

## 5. Reader “加载更多”前端坑

`reader.html` 中不要让按钮固定传 `loadMore('render', 12)`。这会导致每次都从第 12 张开始加载，出现重复/错误。

正确做法：

- 维护全局游标 `nextRenderIndex`。
- 进入项目时重置 `nextRenderIndex = PAGE_SIZE`。
- 每次点击 `loadMoreRender()`：
  - `start = nextRenderIndex`
  - `end = min(start + PAGE_SIZE, images.length)`
  - 追加 `images.slice(start, end)`
  - 更新 `nextRenderIndex = end`
  - 剩余为 0 时移除按钮。

## 6. Reader 显示名注意

Reader 左侧优先显示 `config.title`，不是目录名。若目录名是 `雨夜球馆的最后一分_逻辑测试版`，但 `config.title` 是 `雨夜球馆的最后一分`，用户会看到后者。排查时看 `/projects` 返回的 `name` 与 `title` 对应关系。
