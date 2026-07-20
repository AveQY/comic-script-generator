# Image Generation Endpoint Configuration

Use this when `comic-script-generator` needs to render generated Page/Panel scripts into images through a private OpenAI-compatible image API.

## Private config location

**Hard rule:** real API tokens, private domains, server IPs, VPN/proxy details, cookies, and any credential-like values must stay in local private files. They must not be written to `SKILL.md`, README, public references, examples, committed project files, or git-tracked skill files.

Preferred locations:

1. `$COMIC_IMAGE_CONFIG` pointing to a private JSON file; or
2. `~/.config/comic-script-generator/image_config.json` with file mode `600`.

A public-safe template may live in the skill as `config.example.json`. The installed skill directory must not contain a real `config.json`; `.gitignore` keeps `config.json` ignored only as a last-resort safety net, not as the recommended location.

Setup example:

```bash
mkdir -p ~/.config/comic-script-generator
cp /path/to/comic-script-generator/config.example.json ~/.config/comic-script-generator/image_config.json
chmod 600 ~/.config/comic-script-generator/image_config.json
export COMIC_IMAGE_CONFIG=~/.config/comic-script-generator/image_config.json
```

Recommended schema:

```json
{
  "image_generation": {
    "base_url": "https://<host>/v1",
    "endpoint": "https://<host>/v1/images/generations",
    "authorization": "Bearer <private-token>",
    "model": "gpt-image-2",
    "size": "1024x1024",
    "timeout_seconds": 300
  }
}
```

## Request shape

POST JSON to `/images/generations`:

```json
{
  "model": "gpt-image-2",
  "prompt": "<panel or render prompt>",
  "size": "1024x1024"
}
```

Required headers:

```text
Authorization: Bearer <private-token>
Content-Type: application/json
```

## Response handling

The endpoint may return either:

- `data[0].b64_json` — decode and save as `.png`
- `data[0].url` — download URL to `.png`; if download fails, save the URL to `.url.txt`

## Performance profile (observed 2026-07-06)

| Metric | Value |
|--------|-------|
| `/v1/models` response time | ~0.5s (fast, always reachable) |
| `/v1/images/generations` response time | **~120–155s per 1024×1024 image** (very slow) |
| `/v1/images/generations` HTTP result | 200 (eventually succeeds; does NOT 4xx/5xx) |
| Timeout needed | 180–300s per request |
| Image size | 1024×1024 PNG, ~2.4 MB each |

**Key operational notes:**
- The generations endpoint is 200-300× slower than the models endpoint, but it **does** eventually return valid images. Do NOT treat 30s+ delays as failures.
- With `--workers 5`, effective throughput is ~2 images/minute (5 parallel × 120s each).
- With `--workers 3`, effective throughput is ~1.5 images/minute.
- For 280 images (full 6-episode project): at `/v1/models` check passes quickly but bulk generation takes significant wall-clock time. Estimate ~2-3 hours for a complete 6-episode render at `--workers 5`. Set `timeout=7200` (2 hours) on background terminal calls.
- If the request hangs past 180s without any response at all, the image generation service behind the proxy may be restarting or queued. Kill and retry after a few minutes.
- If `/v1/models` returns 200 but `/v1/images/generations` persistently times out at 180s+, the backend model worker is likely down. Check API provider status before retrying.

## Safe default behavior

When rendering from a full episode, default to rendering only the panels the user explicitly asks for (`--limit N`). The `render_images.py` script has `--limit` defaulting to **1** (one image), which is a cost-control measure.

**To render all panels in an episode**, always pass `--limit 999` or `--limit 0`. Without this flag, only 1 image per run is generated.

## Batch rendering pattern (for multi-episode projects)

For full-project rendering, use a background terminal loop:

```bash
cd /path/to/skill && \
for f in /path/to/project/render_input/*_render.md; do
  python3 scripts/render_images.py "$f" --limit 999 --workers 5 --sleep 0.2 --retries 2
done
```

**Critical details:**
- **Do NOT pass `--output-dir` when running multiple episodes** — without it, each episode saves to its own subdirectory `<project>/rendered/<prompt_file_stem>/`. With `--output-dir /same/path`, episodes overwrite each other's `scene_001.png`.
- Each episode's render output is automatically isolated by prompt file stem (e.g. `ep001___render/`, `ep002___render/`).
- `--sleep 0.2` adds 200ms between API calls to avoid rate limits.
- `--retries 2` provides 2 retries per transient failure.
- Set background process timeout to at least 7200 seconds for a full 6-episode project.
