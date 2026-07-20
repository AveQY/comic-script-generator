# Market manga production lessons

Session-derived guidance for turning comic-script-generator output into readable, market-facing manga projects.

## User-facing expectations

- Prefer **story-title project names** over technical slugs such as `async_comic_001_*` or `batch_*`.
- If failed/test projects have no episodes or images, archive them out of the projects root so the Reader does not show confusing technical names.
- The Reader should use a **light, clean UI** by default for this user, with a scrollable left project list.
- The Reader should support image/script comparison: clicking a rendered panel, manga page, or localized long image should reveal the corresponding episode script below the image.
- Final delivery should be a readable manga artifact, not only a pile of panel images.

## Production pipeline that worked best

For each project:

1. Write a market-oriented 1-episode script using `Page -> Panel`, typically **2 pages x 6 panels = 12 panels** for a short complete test chapter.
2. Keep narration minimal. Put `旁白：无` unless it is truly needed.
3. Use short speech bubbles; let action and panel-to-panel continuity carry the scene.
4. Prompt image generation for **no text / no letters / no watermark**. Do not ask the image model to render readable Chinese.
5. Generate raw panel art with `scripts/render_images.py`.
6. Add readable Chinese dialogue with deterministic post-processing via `scripts/overlay_comic_text.py`.
7. Compose panels into page images with `scripts/compose_manga_pages.py`.
8. Stitch pages into a complete localized chapter image with `scripts/stitch_localized_chapter.py`.
9. Show in Reader in this priority order: localized long image -> comic pages -> rendered panel images -> script/docs.

## Why this matters

Image models often omit or garble Chinese text. The robust workflow is:

```text
no-text art generation -> deterministic Chinese lettering overlay -> page composition -> localized long-strip stitch
```

This produces a more readable manga than asking the image model to draw speech bubbles directly.

## Market-facing validation checklist

Hard checks:

- Project has a story-title directory and `config.json.title`.
- Episode has Page/Panel structure and continuous panel numbering.
- First 3 panels contain a hook or abnormal event.
- Each panel has action continuity from the previous panel.
- Dialogue is short; avoid exposition dumps.
- `旁白` is mostly `无` unless needed.
- Raw images exist for all panels, or missing panels are reported clearly.
- Lettered panel images are readable.
- `comic_pages/*.png` exists.
- `localized/*完整汉化长图.png` exists.
- Reader can display the project and compare images with the matching script.

Market score heuristic:

- 85+ = acceptable for small market testing.
- 75-84 = usable but needs pacing/visual continuity improvement.
- Below 75 = only a technical completion, not a market-ready comic.

## Reader/frontend lessons

- Left project list must be scrollable inside the sidebar: give the flex parent `min-height: 0` and the list `flex: 1; min-height: 0; overflow-y: auto; -webkit-overflow-scrolling: touch`.
- Favor light UI unless user asks otherwise.
- Avoid exposing archived/empty projects in the project root.
- Add `comic_pages` and localized chapter image metadata to the API response so the frontend can show finished artifacts, not just raw panels.
- Clicking images should call a JS helper that infers the episode from paths like `rendered/ep001.../scene_001.png` or `comic_pages/ep001_..._page_001.png`, then fetches `/episode?project=...&file=...`.

## VPN/proxy note for GitHub-dependent setup

When GitHub release downloads are slow or blocked, use the user's configured local proxy if available. For this server, Mihomo/Clash-style proxy can run on `127.0.0.1:7890`; commands can use:

```bash
curl -x http://127.0.0.1:7890 ...
```

If bootstrapping Mihomo itself from GitHub fails, a GitHub release mirror may be needed; capture the successful mirror pattern in session notes rather than hard-coding it into public docs.