# Reader / Rendering Lessons (2026-07-05)

These notes capture durable workflow lessons from running `comic-script-generator` end-to-end on a server with a Reader UI and an OpenAI-compatible image endpoint.

## Private image endpoint configuration

- Keep API keys and image endpoint configuration in a private local `config.json` or environment variable, never in public README/reference docs.
- A practical config shape is:
  - `image_generation.endpoint`
  - `image_generation.authorization`
  - `image_generation.model`
  - `image_generation.size`
  - `image_generation.timeout_seconds`
- Image generation can be slow; default timeouts should be 120–300 seconds.
- The endpoint may return either `b64_json` or `url`; render tooling should support both and save a local PNG. If a URL is returned, also keep `scene_XXX.url.txt` so the raw image can be restored later.

## Do not rely on the image model for readable comic text

Image models often omit dialogue or render Chinese text incorrectly. Also, common negative prompts such as `text`, `watermark`, and `signature` actively suppress text. For readable comics:

1. Generate clean, text-free panel art.
2. Parse the source episode markdown for `气泡`, `旁白`, and `拟声` fields.
3. Overlay speech bubbles and text with a deterministic script using a Chinese font such as Noto Sans CJK.
4. Default to dialogue/SFX only. Add narration boxes only when explicitly requested or when the page truly needs them; excessive narration makes the comic feel cluttered and less hand-drawn.

## Make output readable as manga pages, not isolated illustrations

A gallery of single square images feels like illustrations, not comics. After panel image generation and lettering:

- Compose panels into page images under `comic_pages/`.
- A simple readable layout is a vertical page with 2 columns × 3 rows, 6 panels per page.
- The Reader UI should prioritize `comic_pages/` for reading, with single panel images as secondary assets.

## Project naming and cleanup

- User-facing project directories should be named after the story title (`云端便利店`, `像素猫侦探社`) rather than technical batch names (`async_comic_001_...`).
- Failed/planning-only projects with zero episodes and zero images should be archived out of the Reader root so they do not appear as noisy English/technical names.

## Reader UI pitfalls

- Prefer a clean light theme when the user asks for it; make story names prominent.
- Left project lists inside flex/grid layouts need `min-height: 0`, `flex: 1`, and `overflow-y: auto` to scroll correctly.
- Expose project docs (`summary.md`, `characters.md`, `foreshadowing.md`, `style_guide.md`), episode stats, rendered images, and comic page outputs in the Reader API.

## Continuity caveat

If source episodes are template-like or repetitive, no amount of page composition will make them read like a true comic. For high-quality hand-drawn-style output, first write episode/page beats with explicit panel-to-panel action continuity, then generate panel art, then letter and compose pages.

---


## User-facing preferences learned

- Prefer a light, clean reader UI over dark/glassmorphism for this workflow.
- Project lists should show human story titles first, not technical directory names such as `async_comic_*` or `batch_*`.
- Left navigation must be independently scrollable on desktop and touch-scrollable on mobile; flex children that should scroll need `min-height: 0` and the list needs `flex: 1; overflow-y: auto; -webkit-overflow-scrolling: touch`.
- The user expects long batch jobs to run with safe parallelism and background tracking, then a concrete verification summary.

## Rendering pipeline lesson

For readable manga output, do **not** rely on the image model to generate Chinese dialogue text inside the image. It is unreliable and often produces no text or broken text. Use a two-stage pipeline:

1. Generate the illustration/background panel image without trying to force exact dialogue text.
2. Deterministically overlay speech bubbles, SFX, and optional narration with PIL or another layout engine using a CJK font.

Avoid putting `text` in the negative prompt if the intended output should contain text, but even without a negative prompt, exact Chinese dialogue is better handled by post-processing.

## Bubble / text overlay defaults

- Default to role dialogue bubbles and SFX only.
- Do **not** render narration/旁白 by default; it can make pages feel cluttered and less like readable comics.
- Add an explicit `--include-narration` flag or equivalent when narration boxes are desired.
- Install/use a CJK font such as `fonts-noto-cjk` / `NotoSansCJK-Regular.ttc` for reliable Chinese text rendering.
- If a previous overlay overwrote images, restore clean base images from saved image URLs or source originals before applying a revised overlay; avoid repeatedly drawing text on top of already-lettered images.

## Manga page composition lesson

Single generated panels displayed as a flat gallery feel like illustrations, not comics. For a more authentic readable result:

- Compose panels into page images (`comic_pages/`) after lettering.
- Use a consistent page canvas and panel gutters/borders, e.g. vertical page with 2 columns × 3 rows for 6 panels/page.
- Let the reader frontend prioritize composed pages for reading, while keeping individual panels available as secondary assets.

## Reader/API cleanup lesson

Failed/empty scaffold projects (`episodes=0`, `images=0`, `status=planning`) should be archived out of the visible project root, not shown in the reader. This keeps the UI focused on usable story projects and avoids exposing technical batch names.
