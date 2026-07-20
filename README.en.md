# Comic Script Generator

<p align="center">
  <img src="https://img.shields.io/badge/version-v1.11.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/format-Page%2FPanel%20%2B%20Light%20Novel-orange.svg" alt="Format">
</p>

<p align="center">
  <strong>Generate Page/Panel comic scripts, light novels, and render-ready manga assets</strong>
</p>

<p align="center">
  <a href="README.md">中文</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#privacy-and-local-configuration">Privacy Config</a> •
  <a href="#scripts">Scripts</a> •
  <a href="#release-checklist">Release Checklist</a>
</p>

---

## Introduction

**Comic Script Generator** is a Hermes skill for producing comic storyboard scripts, light-novel chapters, key-scene illustration lists, and render input files.

Main workflows:

1. **Comic workflow**: Page → Panel storyboard scripts with panel shape, visual description, composition, speech bubbles, narration, sound effects, transitions, and AI prompts.
2. **Rendering workflow**: export comic scripts into `render_input/`, render through a private OpenAI-compatible image endpoint, overlay Chinese text, compose manga pages, and stitch localized long images.
3. **Light-novel workflow**: generate Chinese web-novel/light-novel chapters with key illustration lists, long-form context compression, and validation scripts.

---

## Core Features

- Standard `## Page X` / `### Panel X` comic format.
- Required Panel fields: panel shape, visual, composition, bubbles, narration, sound effects, transition, AI prompt.
- Fixed `style_guide.md` per project for style consistency.
- Light-novel project structure under `light_novel/`.
- Long-novel context compression under `long_novel_context/`.
- Reader-compatible outputs for comic and novel modes.

---

## Privacy and Local Configuration

**Hard rule: the skill repository and skill directory must not contain real secrets or private deployment data.**

Do not write these into `SKILL.md`, README files, references, examples, generated scripts, or files intended for commit/release:

- API tokens / Authorization / Bearer / Cookies
- Private image API domains
- Public server IPs
- VPN/proxy subscription URLs
- Database passwords
- Personal local paths or production deployment paths

Store image-generation credentials only in a local private file, preferably:

```bash
mkdir -p ~/.config/comic-script-generator
cp config.example.json ~/.config/comic-script-generator/image_config.json
chmod 600 ~/.config/comic-script-generator/image_config.json
export COMIC_IMAGE_CONFIG=~/.config/comic-script-generator/image_config.json
```

`render_images.py` config priority:

```text
1. --config
2. $COMIC_IMAGE_CONFIG
3. ~/.config/comic-script-generator/image_config.json
```

Before release or sync, run:

```bash
python3 scripts/privacy_check.py
```

---

## Quick Start

### 1. Initialize a comic project

```bash
python3 scripts/init_project.py "Project Name" --output ~/comic-projects --mode B --episodes 6
```

### 2. Update and validate an episode

```bash
python3 scripts/update_project.py episodes/ep001_<title>.md --project-dir projects/<project-name> --episode-num 1
python3 scripts/validate_episode.py episodes/ep001_<title>.md --project-dir projects/<project-name>
python3 scripts/consistency_check.py episodes/ep001_<title>.md --project-dir projects/<project-name>
```

### 3. Export render input

```bash
python3 scripts/export_for_render.py episodes/ep001_<title>.md --project-dir projects/<project-name> --style-guide projects/<project-name>/style_guide.md
```

### 4. Render images

```bash
python3 scripts/render_images.py projects/<project-name>/render_input/ep001_<title>_render.md --limit 999 --workers 5 --sleep 0.2 --retries 2
```

`--limit` defaults to 1 for cost control. Pass `--limit 999` or `--limit 0` to render all prompts.

---

## Density Modes

| Mode | Description | Recommended for |
|------|-------------|-----------------|
| A | Dialogue-heavy, fewer Panels, about 30-40 Panels per episode | Romance, slice of life |
| B | Balanced mode, about 50-60 Panels per episode | General comics |
| C | Cinematic mode, about 150-250 Panels per episode | Action, cinematic pacing |
| LN | Light novel / web novel prose | Romance, healing, workplace, mystery |

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/check_update.py` | Check remote updates |
| `scripts/privacy_check.py` | Scan for accidental secrets/private deployment data |
| `scripts/init_project.py` | Initialize comic projects |
| `scripts/update_project.py` | Extract characters, foreshadowing, and summaries |
| `scripts/validate_episode.py` | Validate comic Page/Panel format |
| `scripts/consistency_check.py` | Check character consistency |
| `scripts/batch_generate.py` | Batch-generate comic projects |
| `scripts/export_for_render.py` | Export render input |
| `scripts/render_images.py` | Render images through private image API |
| `scripts/overlay_comic_text.py` | Overlay Chinese dialogue/SFX |
| `scripts/compose_manga_pages.py` | Compose manga pages |
| `scripts/stitch_localized_chapter.py` | Stitch localized long images |
| `scripts/export_light_novel.py` | Export light-novel-compatible text from comic scripts |
| `scripts/validate_light_novel.py` | Validate light-novel chapters |
| `scripts/update_long_novel_context.py` | Build compressed long-novel context |
| `scripts/validate_long_novel.py` | Validate long-novel length/chapter/context requirements |

---

## Project Structure

```text
projects/<project-name>/
├── config.json
├── summary.md
├── characters.md
├── foreshadowing.md
├── style_guide.md
├── episodes/
├── light_novel/
├── long_novel_context/
├── render_input/
├── rendered/
├── comic_pages/
└── localized/
```

---

## Release Checklist

Run before publishing, copying to another environment, or pushing:

```bash
python3 -m py_compile scripts/*.py
python3 scripts/privacy_check.py
python3 scripts/check_update.py
```

Check that:

- Python scripts compile.
- No real token/IP/private domain/local deployment path is leaked.
- `config.example.json` contains placeholders only.
- Real credentials live only in local private config.
- README version matches `SKILL.md` version.

---

## Changelog

### v1.11.0

- Upgraded light-novel workflow for 200k-character long-form production.
- Added `update_long_novel_context.py` and `validate_long_novel.py`.
- Added strict local-private configuration rules for sensitive data.
- Added `config.example.json` and `scripts/privacy_check.py`.

### v1.10.0

- Formalized standalone light-novel/web-novel workflow.
- Added `validate_light_novel.py`.

### v1.9.0

- Added light-novel + key illustration route.
- Added `export_light_novel.py`.

### v1.8.x

- Added story-renderer bridge and image rendering workflow.
- Added render limit/output directory/concurrency guidance.

### v1.7.0

- Upgraded comic scripts to Page/Panel format.

---

## License

MIT
