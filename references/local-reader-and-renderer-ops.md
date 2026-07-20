# Local Reader, Renderer, and Parallel Ops Notes

Session-derived operational notes for `comic-script-generator`.

## Private image-generation config

Keep provider credentials out of README/SKILL.md. Put them in the skill-local `config.json` or a private config pointed to by `COMIC_IMAGE_CONFIG`.

Expected shape:

```json
{
  "image_generation": {
    "base_url": "https://example/v1",
    "endpoint": "https://example/v1/images/generations",
    "authorization": "Bearer <private-key>",
    "model": "gpt-image-2",
    "size": "1024x1024",
    "timeout_seconds": 300
  }
}
```

The image endpoint may return either `b64_json` or `url`; renderer tooling should handle both and save a local PNG where possible. Use long timeouts (120–300s) because generation can be slow. Render a small test batch first (for example `--limit 1`) before launching a full project render.

## Parallel execution preference

For batch generation/export/render tasks, prefer parallel execution when outputs are independent:

- Export render inputs for multiple projects concurrently.
- Render one test image per project concurrently before scaling up.
- Keep each worker isolated by project directory.
- Always verify real output files after parallel work: existence, byte size, image dimensions/format.

Avoid presenting a task as complete until the actual files have been checked.

Example shell pattern:

```bash
for P in /path/to/comic-projects/projects/async_comic_*; do
  (
    cd /path/to/.hermes/skills/comic-script-generator
    EP=$(find "$P/episodes" -maxdepth 1 -type f -name 'ep001_*.md' | head -n1)
    python3 scripts/export_for_render.py "$EP" --project-dir "$P" --style-guide "$P/style_guide.md"
    RENDER=$(find "$P/render_input" -maxdepth 1 -type f -name '*_render.md' | head -n1)
    python3 scripts/render_images.py "$RENDER" --limit 1 --sleep 0
  ) &
done
wait
```

## Local Reader/API fallback

The documented online Reader may be an external deployment and not present on the current server. If `/path/to/comic-script-generator-api` is missing, create a small local Reader/API rather than claiming the site is unavailable.

Minimum useful API endpoints:

- `GET /reader` — HTML UI
- `GET /health` — root/path/time health check
- `GET /projects` — list projects with status, episode count, rendered image count, description
- `GET /projects/<name>` — full project detail, including config, episode metadata, rendered images, render inputs, docs, and aggregate stats
- `GET /episode?project=<name>&file=<file>` — full episode markdown
- `GET /doc?project=<name>&file=<file>` — project docs such as summary/characters/foreshadowing/style guide
- `GET /file?project=<name>&path=<relpath>` — serve rendered images safely from within the project directory

Run it on `0.0.0.0:8081` by default with `COMIC_PROJECTS_ROOT=/path/to/comic-projects/projects`.

Verification commands:

```bash
python3 -m py_compile /path/to/comic-script-generator-api/app.py
COMIC_PROJECTS_ROOT=/path/to/comic-projects/projects COMIC_READER_PORT=8081 python3 app.py
curl -s http://127.0.0.1:8081/health
curl -s http://127.0.0.1:8081/projects
curl -s http://127.0.0.1:8081/projects/<project-name>
ss -ltnp | grep :8081
```

Run the server as a tracked background process when working interactively.

## Reader UI quality bar

A minimal list/detail page is not enough. The Reader should display all important project material:

- Search/filterable project sidebar
- Project hero/description and status badges
- Stats cards: episodes, pages, panels, rendered images
- Episode cards with title, pages, panels, excerpt, ending hook
- Rendered image gallery with thumbnails and links
- Tabs for `summary.md`, `characters.md`, `foreshadowing.md`, `style_guide.md`, and `config.json`
- Full episode reader area without truncating content
- Responsive layout for mobile

Use a polished visual design (dark/glassmorphism or similarly cohesive styling) unless the user asks for plain HTML. If the user says the frontend is incomplete or ugly, fix both backend data completeness and frontend presentation.

## Security setup reminder

When opening a local Reader port, also consider basic server hardening:

- UFW: default deny incoming, allow outgoing, allow SSH, allow the Reader port if external access is desired, and optionally 80/443 for future Nginx.
- fail2ban: enable an `sshd` jail with `backend=systemd`, `banaction=ufw`, reasonable `maxretry/findtime/bantime`.

Repeatable commands:

```bash
apt-get update
apt-get install -y ufw fail2ban
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 8081/tcp comment 'Comic Reader'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw --force enable
cat > /etc/fail2ban/jail.d/sshd.local <<'EOF'
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5
backend = systemd
banaction = ufw

[sshd]
enabled = true
port = ssh
filter = sshd
backend = systemd
maxretry = 5
findtime = 10m
bantime = 1h
EOF
systemctl restart fail2ban
ufw status numbered
systemctl is-enabled fail2ban
systemctl is-active fail2ban
fail2ban-client status sshd
```

Use terminal/sudo for `/etc` writes; generic file-write tools may intentionally refuse sensitive system paths. Do not record one-off package installation failures as durable constraints; capture only the repeatable configuration pattern.
