# Reader / Render Pitfalls Captured 2026-07-05

## Frontend Reader UI

When building or repairing the comic reader frontend:

- Prefer a light, clean dashboard style when the user asks for a public-facing browsing UI.
- Display projects by story title, not technical directory names such as `async_comic_001_...` or `batch_...`.
- Empty/test projects with `episodes=0` and `images=0` should be archived out of the active projects root instead of shown in the reader.
- If the left project list does not scroll, fix the flex container, not just `overflow:auto`:
  ```css
  .sidebar { display:flex; flex-direction:column; min-height:0; }
  .list {
    flex:1;
    min-height:0;
    overflow-y:auto;
    overflow-x:hidden;
    -webkit-overflow-scrolling:touch;
    overscroll-behavior:contain;
  }
  ```

## Image Rendering With Dialogue

Image models often produce nice art but omit or garble readable Chinese dialogue. Do not rely on the image prompt alone for speech bubbles.

Correct flow:

1. Generate clean panel art from the visual prompt.
2. Deterministically overlay dialogue/旁白/拟声 from the episode markdown onto the rendered PNG with a script.
3. Use a CJK font such as Noto Sans CJK.
4. Show the lettered images in the reader.

Pitfalls found:

- `export_for_render.py` may include visual prompts but omit `气泡/旁白/拟声` from the prompt block used by `render_images.py`.
- Negative prompts containing `text` suppress speech bubbles and signs. For raw art generation this may be acceptable, but final comic output needs post-processing text overlay.
- The stable solution is not “ask the image model to write Chinese text”; it is “render art, then overlay readable text”.

Suggested helper script behavior:

- Parse each `### Panel N` block from the episode markdown.
- Extract fields: `气泡`, `旁白`, `拟声`.
- Match `Panel N` to `scene_NNN.png`.
- Draw rounded white bubbles and dark narration boxes using PIL.
- Save either overwriting `scene_NNN.png` or as `scene_NNN_lettered.png`.

## Batch Rendering Discipline

- Parallel rendering is useful, but high concurrency can lead to missing outputs from timeouts/rate limits.
- Use a resumable task list that skips existing `scene_NNN.png` files.
- If many images are missing after a run, retry only missing files at lower concurrency.
- Always verify final counts per project and per episode, not just process exit code.
