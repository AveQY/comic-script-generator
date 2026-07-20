# 2026-07-06 Reader 调试与漫画逻辑生成经验

本记录归档一次完整的 Reader 前端调试 + 漫画生成链路修复经验，供后续同类任务复用。

## 用户工作流纠正

用户明确指出：图片不符合正常漫画逻辑时，不能只在渲染后处理阶段修补；**生成稿子阶段就必须直接产出具体、可画、连续的漫画镜头**。后处理脚本只能兜底旧稿，不能成为正常流程依赖。

执行同类任务时应优先顺序：

1. 检查 episode 稿子的 `画面` 和 `构图` 是否具体可画。
2. 检查 `render_input` 是否继承了具体镜头，而不是抽象模板句。
3. 再检查单图渲染、对白叠加和漫画页合成。
4. 不要只重跑生图；先修 prompt/source episode。

## 抽象模板句必须视为不合格

以下内容出现在 `画面` 字段时，应视为不合格稿，而非“可接受的概括”：

- 普通日常场景
- 异常事件突然出现
- 主角靠近异常源
- 关键配角登场
- 世界观第一次展开
- 规则第一次被验证
- 主角做出第一次主动选择
- 危机升级
- 情感冲突爆发
- 关键线索出现
- 结尾钩子
- 结合本作设定
- 环境信息明确

正确写法必须包含：角色姓名/外貌、关键物件、动作前后顺序、地点、光线、表情、画面焦点和气泡留白。

## 生图与叠字分工

- 生图模型只画“无字干净漫画画面”。
- 正向 prompt 必须包含类似：`no text, no letters, leave empty space for speech bubbles`。
- 中文对白、拟声、旁白由 `overlay_comic_text.py` 叠加。
- 不要把气泡对白塞进 `render_input` 的旁白字段让生图模型生成，否则容易变成乱码文字或插画感。
- `export_for_render.py` 应清理正向 prompt，避免混入 `photorealistic`, `3d render`, `blurry`, `watermark`, `readable text` 等反向词。

## Reader 前端调试经验

常见问题和修法：

1. **Service Worker 缓存旧 404**
   - 症状：后端已修好，但浏览器仍请求旧资源并报 404。
   - 调试阶段可主动 unregister：
     `navigator.serviceWorker.getRegistrations().then(regs => regs.forEach(r => r.unregister()))`。

2. **`await` 写在非 async 函数中**
   - 症状：页面直接报 `await is only valid in async functions`，后续所有逻辑不执行。
   - 修法：所有调用 `await api(...)` 的函数必须声明为 `async function`，并用 `node --check` 检查内联脚本。

3. **图片真实加载但看不见**
   - 症状：Network 无明显报错，点击图片下方详情能加载，但画廊区域空白。
   - 可能原因：CSS opacity 初始为 0，懒加载 onload/class 逻辑未触发，或 `IntersectionObserver` 仍观察旧 DOM。
   - 稳定方案：项目切换/innerHTML 替换后断开旧 observer 并重建；调试时可先用普通 `<img data-src>` + 简单 observer，避免 Web Worker/IndexedDB 等复杂结构。

4. **用户偏好前端风格**
   - 漫画/小说 Reader 优先浅色、清爽、类似番茄小说网：顶部搜索，左侧项目卡片，右侧内容区，统计卡片、分集、图片画廊、对照稿、文档、正文阅读分区。
   - 图片加载慢时优先 `/thumb` + 分批加载；但调试“看不到图”时先保证最小链路可见，再恢复优化。

## 验证建议

对“完整生成一个项目给用户看”的请求，建议实际跑通：

```text
生成/写入 episode
→ validate_episode.py
→ export_for_render.py
→ render_images.py
→ overlay_comic_text.py
→ compose_manga_pages.py
→ Reader 可访问
```

如果批量脚本 LLM 接口失败但当前会话仍可生成内容，按兜底流程手写项目文件并继续验证，不要停在脚本失败报告。