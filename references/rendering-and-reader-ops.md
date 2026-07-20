# Rendering and Reader Ops Notes

Session-derived operational notes for `comic-script-generator`.

## Private image generation configuration

Keep provider credentials in the skill-local private `config.json` or a user-owned config referenced by `COMIC_IMAGE_CONFIG`; do **not** put bearer tokens in README, public references, or generated project files.

Expected shape:

```json
{
  "image_generation": {
    "endpoint": "https://.../v1/images/generations",
    "authorization": "Bearer <token>",
    "model": "gpt-image-2",
    "size": "1024x1024",
    "timeout_seconds": 300
  }
}
```

The provider may return either `data[0].b64_json` or `data[0].url`; rendering scripts should support both and save a local PNG when possible, keeping `.url.txt` as a trace when URL responses are used.

## End-to-end render chain

1. Export an episode to render input:
   ```bash
   python3 scripts/export_for_render.py \
     <project>/episodes/ep001_xxx.md \
     --project-dir <project> \
     --style-guide <project>/style_guide.md
   ```
2. Render images from the generated `render_input/*_render.md`:
   ```bash
   python3 scripts/render_images.py <project>/render_input/ep001_xxx_render.md --limit 1
   ```
3. Verify actual image files, not just API success: check file exists, non-zero size, and image dimensions/format if possible.

Use `--limit 1` for first smoke tests to avoid burning quota; increase only after one image succeeds.

## Parallel execution pattern

For multiple independent projects, run export+render per project in background subshells and `wait`:

```bash
for P in <project1> <project2> <project3>; do
  (
    EP=$(find "$P/episodes" -maxdepth 1 -type f -name 'ep001_*.md' | head -n1)
    python3 scripts/export_for_render.py "$EP" --project-dir "$P" --style-guide "$P/style_guide.md"
    RENDER=$(find "$P/render_input" -maxdepth 1 -type f -name '*_render.md' | head -n1)
    python3 scripts/render_images.py "$RENDER" --limit 1 --sleep 0
  ) &
done
wait
```

Use tracked background processes with completion notification for long render batches.

## Reader/frontend deployment reality check

The reader/frontend described in `references/online-reader-deployment.md` is not necessarily part of this skill directory. Before saying it is running, check for:

- process listening on the documented port, usually `8081`
- expected service/process (`comic-api.service`, `app.py`, Flask/FastAPI/etc.)
- deployment directory such as `/path/to/comic-script-generator-api`

If those are absent, say the reader is not currently running and offer to scaffold or start a local Reader/API rather than implying the documented remote deployment exists on the current host.
