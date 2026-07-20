# Manga Rendering & Reader Lessons

Session-derived lessons for turning generated comic scripts into readable manga pages.

## Rendering pipeline

- Do **not** rely on the image model to render readable Chinese dialogue. It often omits text or produces garbled text.
- Generate clean art panels first, then deterministically overlay dialogue/sfx with a script using a CJK font.
- Keep negative prompts like `text`, `letters`, `logo`, `watermark` for the art-generation step; this is compatible with post-processing text later.
- For user-facing manga, avoid dumping all `旁白` onto the image. Default to role dialogue bubbles and essential `拟声`; only include narration when explicitly requested or narratively necessary.
- If earlier images were overwritten with bad lettering, restore raw images from saved `scene_XXX.url.txt` files before re-lettering.

## Continuity

- A pile of isolated panel prompts does not become readable manga just because it is laid out in a grid.
- For “真实可阅读/手绘漫画” requests, first rewrite the episode as coherent page beats: setup → action → reaction → discovery → decision → page hook.
- Each panel should explicitly inherit an action, gaze direction, object, or emotional state from the previous panel.
- Prefer fewer, stronger panels (e.g. 12 panels across 2 pages) over many repetitive panels when making a quality sample.
- Use `Page → Panel` structure and compose final `comic_pages/page_XXX.png` images for the reader, not only separate `scene_XXX.png` illustrations.

## Reader/frontend expectations

- Show projects by story title, not technical batch/async directory names.
- Archive or hide empty planning/test projects (`episodes=0`, `images=0`) so the reader list is not polluted.
- For review workflows, clicking a rendered image or composed comic page should show a comparison area with:
  - selected image preview
  - image path
  - matched episode file
  - full episode script text
  - separate “open original image” link
- Reader UI preference from this workflow: light theme, scrollable left project list, story-name-first project cards.

## Useful implementation notes

- Install a CJK font before text overlay on Ubuntu: `apt-get install -y fonts-noto-cjk fontconfig`.
- Use a local-only proxy (Mihomo/Clash) for GitHub access when needed; keep subscription URLs and keys out of public README/skill files.
- Store image API keys and proxy subscriptions only in private config files with restrictive permissions; never embed secrets in generated reader pages or public docs.
