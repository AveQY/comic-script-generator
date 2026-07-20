# 2026-07-06 漫画生成与 Reader 调试经验

本记录用于补充 `comic-script-generator` 的通用流程，避免后续重复踩坑。

## 1. 生成稿子阶段必须直接满足漫画逻辑

用户明确纠正：不能先生成抽象模板稿，再靠后处理修复。新稿生成时就必须满足：

- `画面` 字段必须是可直接绘制的具体画面：角色姓名/外貌、关键物件、动作前后顺序、地点、光线、表情、画面焦点。
- 禁止抽象模板句：`普通日常场景`、`异常事件突然出现`、`主角靠近异常源`、`关键配角登场`、`世界观第一次展开`、`危机升级`、`情感冲突爆发`、`关键线索出现`、`结合本作设定`。
- 每格需要承接上一格的动作、视线、物件位置或情绪变化。
- 验证脚本应把抽象模板句视为不合格，而不是只检查 Page/Panel 格式。

已落地脚本：
- `scripts/validate_episode.py`：增加抽象模板句检查、短篇 `预计 Panel 数 <= 20` 的验收宽容。
- `scripts/repair_manga_logic.py`：仅作为旧稿兜底修复器，不作为正常生成流程依赖。

## 2. 画风统一优先级

用户反馈“画风不够统一”。只靠相同风格词不够，必须加入项目级一致性锁：

- `style_guide.md` 应包含 `## 角色视觉指纹` 与 `## 风格说明`。
- 每个角色固定：年龄、发型、脸型、服装、关键道具、表情气质。
- 每个场景固定：主场景、光线、关键道具、线条密度、网点密度。
- `export_for_render.py` 导出时必须把角色视觉指纹和风格说明注入每个镜头 prompt。
- prompt 中加入类似：`CONSISTENCY LOCK: same character design, same face, same hairstyle, same outfit, same manga line style, same screentone density across all panels`。

## 3. 生图不要负责中文对白

用户目标是“真实可阅读漫画”。当前稳定做法：

1. 生图 prompt 强制 `no text / no letters / leave empty space for speech bubbles`。
2. 中文对白、拟声由 `overlay_comic_text.py` 叠加。
3. `export_for_render.py` 不应把气泡对白塞进生图的旁白/画面描述字段。

## 4. 多线程渲染

用户明确要求耗时任务多线程/并发。`render_images.py` 已支持：

```bash
python3 scripts/render_images.py <render_input.md> \
  --output-dir <rendered_dir> \
  --limit 12 \
  --workers 5 \
  --retries 2 \
  --sleep 0.2
```

实测：`--workers 5 --retries 2 --sleep 0.2` 可完成 12 张短篇漫画渲染。若出现 429/401/5xx，先补单张或降到 `--workers 3`。

## 5. Reader 调试经验

- “加载更多”不要固定传 `start=PAGE_SIZE`；应维护 `nextRenderIndex` 游标，每次追加下一批并更新按钮剩余数量。
- 追加图片用 `insertAdjacentHTML('beforeend', ...)`，不要向 `.gallery` 里套额外 wrapper `<div>`。
- 缩略图缓存键必须包含源文件 `mtime:size`，否则更新图片后仍可能看到旧缩略图。
- 调试后清空 `/path/to/comic-projects/disk_cache`，并建议用户浏览器 `Ctrl+Shift+R` 或清站点数据。

## 6. 交付验收

完成后至少报告：

- 项目名（Reader 显示名与真实目录名可能不同）
- 分镜稿路径
- `render_input` 路径
- 原始渲染图数量
- 叠字图数量
- 漫画页数量
- Reader API `/projects/<name>` 返回的 stats

不要只说“已生成”，必须用真实文件数量和 API 结果验收。
