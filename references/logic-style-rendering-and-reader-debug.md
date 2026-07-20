# 2026-07 漫画逻辑、统一画风与 Reader 调试经验

## 触发场景
当用户反馈“生成的图片不符合正常漫画逻辑”“画风不统一”“Reader 看不到新图/加载更多报错”时，按本参考执行，不要只重跑生图。

## 生成阶段必须完成漫画逻辑
- 不要在 `画面` 字段写抽象模板句，例如：`异常事件突然出现`、`关键配角登场`、`世界观第一次展开`、`危机升级`、`情感冲突爆发`、`关键线索出现`、`结合本作设定`。
- `画面` 应可直接绘制：角色姓名/外貌 + 关键物件 + 动作前后顺序 + 地点 + 光线 + 表情 + 画面焦点。
- 每格必须承接上一格的动作、视线、物件位置或情绪，读者按图顺序能理解故事。
- `validate_episode.py` 应把抽象模板句和过短 `画面` 当作问题拦截；短篇若写了 `预计 Panel 数：12个`，验证不应强制按 B 模式 40+ Panel 误判。

## 统一画风/角色连续性
只靠 `modern manga style` 这类泛词不够。项目 `style_guide.md` 应包含：
- 固定画风锁：黑白手绘商业漫画页、统一外轮廓线、统一网点密度、统一明暗策略。
- 角色视觉指纹：年龄、脸型、发型、体型、服装、道具，并明确“所有镜头保持一致”。
- 场景统一：主场景、固定道具、光线变化方式。
- 生图禁止生成文字：`no text, no letters, leave empty space for speech bubbles`；中文对白/拟声由 `overlay_comic_text.py` 后期叠加。

`export_for_render.py` 应读取 `## 角色视觉指纹` 与 `## 风格说明`，每张图都注入：
```text
CONSISTENCY LOCK: same character design, same face, same hairstyle, same outfit, same manga line style, same screentone density across all panels
```

## 渲染并发
图片接口已验证可用参数：
```bash
python3 scripts/render_images.py render_input/ep001_unified_render.md \
  --output-dir rendered/ep001_workers5_test \
  --limit 12 --workers 5 --retries 2 --sleep 0.2
```
- 若 429/401/5xx，先补失败单张；频繁失败再降到 `--workers 3`。
- 完成后运行：`overlay_comic_text.py` → `compose_manga_pages.py`。
- 不要直接覆盖 Reader 默认目录，先输出到测试目录，验收后再复制到默认 `rendered/ep001___render`、`localized/ep001___render`、`comic_pages`。

## Reader 调试经验
- 前端“加载更多”不要写死 `loadMore('render', 12)`；应维护 `nextRenderIndex` 游标，每次追加下一批，并更新剩余数量。
- 追加图片时用 `insertAdjacentHTML('beforeend', ...)`，不要把额外 wrapper `<div>` 塞进 `.gallery`。
- `/thumb` 缩略图缓存键必须包含源文件 `mtime + size`，否则重渲染后仍显示旧缩略图。
- 调试阶段可清空 `/path/to/comic-projects/disk_cache`，并把缩略图响应缓存调低为 `max-age=300, must-revalidate`。
- Reader 左侧可能显示 `config.title` 而不是目录名；若用户找不到 `_逻辑测试版`，解释标题与目录名映射。

## 项目清理
删除项目必须先明确规则。若用户选择“只保留 X”，再删除其他项目。删除后用 `/projects` 确认 API 只返回目标项目。
