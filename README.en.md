# Comic Script Generator

<p align="center">
  <img src="https://img.shields.io/badge/version-v1.25.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/format-Page%2FPanel%20%2B%20Light%20Novel%20%2B%20Drama-orange.svg" alt="Format">
</p>

<p align="center">
  <strong>Comic storyboards, light novels, short-drama scripts & render-ready manga assets</strong><br>
  <strong>漫画分镜、轻小说正文、短剧分镜脚本与漫画渲染生产工具</strong>
</p>

<p align="center">
  <a href="README.md">中文</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#core-features">Core Features</a> •
  <a href="#security--credential-management">Security</a> •
  <a href="#scripts">Scripts</a>
</p>

---

## Introduction

**Comic Script Generator** is a Hermes skill for producing comic storyboard scripts, light-novel chapters, short-drama storyboard scripts, key-scene illustration lists, and render input files.

Main workflows:

1. **Comic workflow**: `Page → Panel` storyboard scripts. Each Panel includes panel shape, visual description, composition, speech bubbles, narration, sound effects, transitions, and AI prompts.
2. **Rendering workflow**: export comic scripts into `render_input/`, render through a private OpenAI-compatible image endpoint, overlay Chinese text, compose manga pages, and stitch localized long images.
3. **Light-novel workflow**: generate Chinese web-novel / light-novel chapters with key illustration lists, long-form context compression, and validation scripts.
4. **Short-drama workflow**: adapt existing novels into short-drama storyboard scripts (shot number / duration / framing & camera movement / dialogue VO / SFX), with C/S/P asset coding and tail-frame continuity between episodes.

---

## Core Features

### Page/Panel Comic Format

- Standard `## Page X` / `### Panel X` structure.
- Required Panel fields: panel shape, visual, composition, bubbles, narration, sound effects, transition, AI prompt.
- A single `style_guide.md` is shared across all episodes of a project for style consistency.

### Light-Novel / Web-Novel Route

- Native light-novel project structure: `light_novel/lnXXX_<chapter>.md`.
- Long-form target defaults to 200k+ characters.
- `update_long_novel_context.py` compresses context so continuation never needs the full text.
- `validate_light_novel.py` and `validate_long_novel.py` for acceptance checks.

### Short-Drama Storyboard Route

- Trigger: "novel → short drama / storyboard script".
- 5-phase workflow: event extraction → adaptation strategy → △-shot script → asset list (C/S/P) → storyboard.
- Two output formats: generic storyboard table, or Seedance 2.0 timeline format.
- One file per episode, ≤4000 chars, with tail-frame description for next-episode continuity.

### Rendering & Reader

- `export_for_render.py`: export story-renderer style `## 镜头 N` input.
- `render_images.py`: concurrent rendering via a private image endpoint.
- `overlay_comic_text.py`: overlay Chinese dialogue / SFX.
- `compose_manga_pages.py`: compose manga pages.
- `stitch_localized_chapter.py`: stitch localized long images.
- Reader supports comic / novel / drama-script modes, thumbnails, lazy loading, and prev/next navigation.

---

## Security & Credential Management

**Hard rule: the skill repository and skill directory must not contain real secrets or private deployment data.**

Never write these into `SKILL.md`, README files, references, examples, generated scripts, or any file intended for commit/release:

- API tokens / Authorization / Bearer / Cookies
- Private image API domains
- Public server IPs
- VPN/proxy subscription URLs
- Database passwords
- Personal local paths or production deployment paths

Store image-generation credentials only in a local private file:

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

This creates:

```text
projects/<project-name>/
├── config.json
├── summary.md
├── characters.md
├── foreshadowing.md
├── style_guide.md
└── episodes/
```

### 2. Generate and validate an episode

```bash
python3 scripts/update_project.py episodes/ep001_<title>.md --project-dir projects/<project-name> --episode-num 1
python3 scripts/validate_episode.py episodes/ep001_<title>.md --project-dir projects/<project-name>
python3 scripts/consistency_check.py episodes/ep001_<title>.md --project-dir projects/<project-name>
```

### 3. Export render input

```bash
python3 scripts/export_for_render.py episodes/ep001_<title>.md --project-dir projects/<project-name> --style-guide projects/<project-name>/style_guide.md
```

Output:

```text
projects/<project-name>/render_input/ep001_<title>_render.md
```

### 4. Render images

```bash
python3 scripts/render_images.py projects/<project-name>/render_input/ep001_<title>_render.md --limit 999 --workers 5 --sleep 0.2 --retries 2
```

Note: `--limit` defaults to 1 for cost control. Pass `--limit 999` or `--limit 0` to render all prompts.

---

## Density Modes

| Mode | Description | Recommended for |
|------|-------------|-----------------|
| A | Dialogue-heavy, fewer Panels, about 30-40 Panels per episode | Romance, slice of life |
| B | One shot per dialogue beat, about 50-60 Panels per episode | General comics |
| C | Multiple shots per dialogue beat, about 150-250 Panels per episode | Cinematic, action |
| LN | Light novel / web novel prose | Romance, healing, workplace, mystery |
| SD | Short-drama storyboard script | Novel-to-video adaptation |

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/check_update.py` | Check remote updates (skips when offline) |
| `scripts/privacy_check.py` | Pre-release safety scan |
| `scripts/init_project.py` | Initialize comic projects |
| `scripts/update_project.py` | Extract characters, foreshadowing, and summaries |
| `scripts/validate_episode.py` | Validate comic Page/Panel format |
| `scripts/consistency_check.py` | Check character consistency |
| `scripts/batch_generate.py` | Batch-generate comic projects |
| `scripts/export_for_render.py` | Export render input |
| `scripts/render_images.py` | Render images through private image API |
| `scripts/overlay_comic_text.py` | Overlay Chinese dialogue / SFX |
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
├── episodes/                 # Comic episode scripts
├── light_novel/              # Novel chapters
├── scripts/                  # Short-drama storyboard scripts
├── long_novel_context/       # Long-form context compression
├── render_input/             # Render input / illustration lists
├── rendered/                 # Per-panel rendered images
├── comic_pages/              # Composed manga pages
└── localized/                # Final localized long images
```

---

## Standard Panel Example

```markdown
## Page 1

### Panel 1

**格子**：横向大格
**画面**：黄昏的城市天台，夕阳将天空染成橙红色。主角站在栏杆边，风吹起校服衣摆。
**构图**：远景，人物置于画面右下角，天空占据大面积留白

**气泡**：
- 阿明（右侧，对话气泡）："今天也要结束了吗？"

**旁白**：
- 旁白框（左上）："那天的风，比往常更安静。"

**拟声**：
- `呼——`：细长字体，沿栏杆方向延伸

**转场**：情绪转场，接下一格人物特写

**AI 提示词**：
正向：
```text
<fixed style from style_guide.md>, dusk rooftop, wide shot, orange-red sky, lonely mood, no text, no letters, leave empty space for speech bubbles
```
反向：
```text
<fixed negative prompt from style_guide.md>
```
```

---

## Release Checklist

Run before publishing, copying to another environment, or pushing:

```bash
python3 -m py_compile scripts/*.py
python3 scripts/privacy_check.py
python3 scripts/check_update.py
```

Verify that:

- Python scripts compile.
- No real token / IP / private domain / local deployment path is leaked.
- `config.example.json` contains placeholders only.
- Real credentials live only in local private config.
- README version matches `SKILL.md` version.

---

## License

MIT

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=aveqy/comic-script-generator&type=Date)](https://star-history.com/#AveQY/comic-script-generator&Date)
