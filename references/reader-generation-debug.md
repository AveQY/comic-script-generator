# 2026-07 Reader + Manga Generation Lessons

## Trigger
Use these notes when generating a complete manga project for the user, wiring it into the local Reader, or debugging generated comic pages/images.

## Key lessons from the session

### 1. Generate concrete drawable panels at script time
Do not let the episode writer output abstract placeholders such as:
- “异常事件突然出现”
- “关键配角登场”
- “世界观第一次展开”
- “危机升级”
- “结合本作设定”

Every `**画面**` must be directly drawable: named character, stable outfit/appearance, concrete object, action sequence, location, lighting, expression, and visual focal point. `validate_episode.py` should fail template-like descriptions.

### 2. Style consistency requires a character/style lock, not just generic style words
A style guide with only `modern manga style, bold lines...` is not enough. Add:
- `## 角色视觉指纹` with fixed hair, clothing, face/age, recurring props
- `## 风格说明` with line weight, screentone density, monochrome/color choice, scene lighting rules
- Export prompts should inject `CONSISTENCY LOCK: same character design, same face, same hairstyle, same outfit, same manga line style, same screentone density across all panels`

### 3. Do not ask the image model to render Chinese text
Prompt images as clean no-text manga panels with bubble space:
- `no text, no letters, no watermark`
- `leave empty space for speech bubbles`
Then overlay readable Chinese with `overlay_comic_text.py`.

### 4. Use concurrent rendering for short manga projects
`render_images.py` now supports:
```bash
python3 scripts/render_images.py render_input/ep001___render.md \
  --output-dir rendered/ep001___render \
  --limit 12 --workers 5 --retries 2 --sleep 0.2
```
This was verified on a 12-panel project. If 429/401/5xx occurs, retry the failed scene singly or reduce to 3 workers.

### 5. Content-policy false positives can be solved by shortening one scene prompt
If one scene returns `content_policy_violation`, do not abandon the project. Replace only that scene’s positive prompt with a short safe English prompt focusing on harmless visual action. Example successful fallback:
```text
monochrome Japanese manga panel, black and white ink line art, clean interior art studio at night, young female illustrator with short black hair and loose sweater sitting at a drawing desk, holding a brush and calmly drawing the final line on a blank comic panel, sheets of paper gently lifted by a soft breeze, warm desk lamp, rainy window reflection, no text, no letters, no watermark, empty speech bubble space
```
Then rerun just that scene:
```bash
python3 scripts/render_images.py render_input/ep001___render.md --start 11 --limit 1 --workers 1 --retries 2
```

### 6. Reader “load more” must use a real cursor
Do not hard-code `loadMore('render', 12)` for every click. Maintain `nextRenderIndex`, reset it when loading a new project, and update/remove the button after each batch.

### 7. Thumbnail cache must invalidate on source changes
`/thumb` cache keys should include source image signature (`mtime:size`), not just project/path/width/height/fit/format. Browser cache should be short enough for iterative work, e.g. `max-age=300, must-revalidate`. Clear `disk_cache` after replacing rendered images.

### 8. Final verification checklist
Before telling the user “done,” verify real outputs:
- `validate_episode.py` passes with no issues
- episode has Page headers, 12 panels (or expected count), all required fields, hook and next hint
- `render_input` has matching scene count
- rendered raw images count equals panel count
- localized images count equals panel count
- `comic_pages` exists and has expected page count
- Reader API returns the project and correct stats

## Known good complete-flow shape
```text
create project
→ write concrete episode
→ validate_episode.py
→ export_for_render.py
→ render_images.py --workers 5 --retries 2
→ retry failed scenes individually with safer prompt if needed
→ overlay_comic_text.py
→ compose_manga_pages.py
→ clear thumbnail cache if replacing images
→ verify Reader stats
```
