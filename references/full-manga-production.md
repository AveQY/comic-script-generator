# Full manga production lessons (2026-07-06)

Lessons from producing and debugging a Reader-visible manga project end-to-end.

## User workflow expectations

- When the user asks to regenerate a manga project, do **not** deliver a 12-panel smoke test as if it were a complete issue.
- Default “formal one-shot / full issue” target should be about **8 pages / 48 Panels** unless the user explicitly asks for a short sample.
- If the user asks to start over, delete the old project and stale thumbnail cache first, then regenerate and verify from scratch.
- Report only the final verifiable project name and Reader status after long work; intermediate background IDs are useful while running, but final answer should be concrete.

## Required end-to-end pipeline

Use this order for formal delivery:

```text
delete stale project/cache when regenerating
→ create project structure
→ generate Page/Panel script
→ validate_episode.py
→ export_for_render.py
→ render_images.py with workers=5
→ identify missing/failed scene_XXX.png
→ safe short-prompt补图 for failed scenes
→ overlay_comic_text.py
→ compose_manga_pages.py
→ Reader API verification
```

Minimum verification before saying “done”:

```text
episode exists and has expected Page/Panel count
no missing required Panel fields
render_input scenes == Panel count
rendered scene_001..scene_N all exist
localized scene_001..scene_N all exist
comic_pages count matches page count
Reader /projects/{name} reports expected stats
```

## Rendering concurrency

For the current image endpoint, `workers=5` has been verified usable for manga rendering:

```bash
python3 scripts/render_images.py render_input/ep001___render.md \
  --output-dir rendered/ep001___render \
  --limit 48 --workers 5 --retries 2 --sleep 0.2
```

If some scenes fail with transient HTTP errors or content-policy false positives, do **not** rerun the whole issue. Create a small missing-scenes render input containing only safe, short prompts for missing scene numbers and render that file into the same output directory.

## Safe prompt fallback for content-policy false positives

Long prompts with supernatural phrasing can trigger content-policy false positives. The durable pattern is:

1. Keep the episode/script intact if the story is valid.
2. Replace only the render prompt for failed scene(s) with a short neutral visual description.
3. Avoid charged words like “震动/倒流/裂缝/鬼/消失” in the render-only fallback.
4. Use simple wording: “young female illustrator drawing at a desk, old art studio, warm lamp, rainy window, monochrome manga panel, no text”.
5. Render only missing scenes into the existing `rendered/epXXX___render/` folder.

## Reader frontend/debugging lessons

- Reader may display `config.title` instead of the directory/project name. When the user says they cannot find a `_测试版` suffix, check whether the UI is showing the shorter title.
- “加载更多” must use a real cursor (`nextRenderIndex`), not a fixed inline `loadMore('render', 12)` start value. Append cards with `insertAdjacentHTML('beforeend', ...)`, update remaining count, and remove the pager when done.
- Thumbnail cache must include source file `mtime:size` in the cache key; otherwise regenerated images may still show old thumbnails. After replacing images, clear `/path/to/comic-projects/disk_cache` and force browser refresh if needed.

## Formal issue size

- 12 Panels / 2 pages is acceptable only as a smoke test or short sample.
- For a “complete” manga chapter delivery, generate at least **8 pages / 48 Panels** unless otherwise specified.
- Mention clearly if a project is only a format/rendering test; do not present it as a full chapter.
