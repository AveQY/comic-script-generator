# Skill Privacy Hardening and Release Readiness

## Trigger
Use this reference when maintaining, publishing, syncing, or packaging `comic-script-generator`, especially after adding render/API/provider configuration, Reader deployment notes, or local server paths.

## Durable lesson
Sensitive operational details must live outside the skill tree. The skill should contain reusable procedures, scripts, templates, and placeholders only.

## Hard rules
- Do not store real `Authorization`, `Bearer`, API keys, cookies, VPN/proxy subscriptions, private domains, public server IPs, or personal deployment paths in `SKILL.md`, README, `references/`, examples, generated project files, or any git-tracked skill file.
- Public repository URLs are not secrets. If the skill is owner-specific, hardcode the canonical repo URL instead of leaving `YOUR_GITHUB_USERNAME` placeholders.
- Store private image/API configuration in a local file such as `~/.config/comic-script-generator/image_config.json` with mode `600`.
- Prefer config discovery order: explicit `--config` → `$COMIC_IMAGE_CONFIG` → `~/.config/comic-script-generator/image_config.json`.
- Keep only `config.example.json` in the skill tree, with placeholder values like `<your-image-api-domain>` and `<your-private-token>`.
- Treat `.gitignore` as a safety net, not permission to keep secrets in the skill directory.

## Required release check
Before publishing, pushing, syncing to another machine, or packaging this skill, run:

```bash
cd /path/to/comic-script-generator
python3 -m py_compile scripts/*.py
python3 scripts/privacy_check.py
```

Expected successful privacy result:

```text
PRIVACY CHECK PASSED: no credential/private deployment findings
```

If the check fails, replace real values with placeholders or move them into local private config before release.

## Template setup
```bash
mkdir -p ~/.config/comic-script-generator
cp /path/to/comic-script-generator/config.example.json ~/.config/comic-script-generator/image_config.json
chmod 600 ~/.config/comic-script-generator/image_config.json
export COMIC_IMAGE_CONFIG=~/.config/comic-script-generator/image_config.json
```

## What to preserve from this session
- The production-safe model is: skill tree = reusable code/docs/templates; local config = secrets and deployment-specific endpoints.
- `render_images.py` should not default to reading a real `config.json` inside the skill directory.
- `privacy_check.py` belongs in `scripts/` and should flag real-looking tokens, private IP/domain/path leaks, and accidental real `config.json` files.
