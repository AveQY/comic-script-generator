# Comic Script Generator

<p align="center">
  <img src="https://img.shields.io/badge/version-v1.8.1-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/format-Page%2FPanel-orange.svg" alt="Page/Panel Format">
</p>

<p align="center">
  <strong>Generate Page/Panel comic scripts, then export them for image/video rendering</strong>
</p>

<p align="center">
  <a href="README.md">中文</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#core-features">Core Features</a> •
  <a href="#scripts">Scripts</a> •
  <a href="#project-structure">Project Structure</a>
</p>

---

## Introduction

**Comic Script Generator** is a Hermes skill for generating comic storyboard scripts from outlines, trending topics, or serialized project context.

The current output format is **Page → Panel**, not film-style `Scene`. Each Panel includes panel shape, visual description, composition, speech bubbles, narration, sound effects, transition notes, and AI image prompts.

Since v1.8.1, it can bridge into a `story-renderer` workflow: generate and review the comic script first, then export selected episodes into render-ready scripts for image or video generation.

---

## Core Features

### Page/Panel Comic Format

- Uses `## Page X` / `### Panel X`
- Required fields for every Panel:
  - `Panel shape`
  - `Visual`
  - `Composition`
  - `Speech bubbles`
  - `Narration`
  - `Sound effects`
  - `Transition`
  - `AI prompt`
- Each episode includes:
  - Story summary
  - Density mode
  - Core emotion
  - Episode hook
  - Ending hook
  - Next episode teaser

### Creation Modes

- **Outline mode**: Generate episodes from a user-provided outline
- **Trending mode**: Fetch accessible trending topics and adapt them into story ideas
- **Continuation/editing mode**: Continue from project context and the last 3 Panels of the previous episode
- **Batch mode**: Generate multiple independent comic projects with resume and retry support
- **Render bridge mode**: Export generated episodes into story-renderer compatible scripts

### Project Management

- `summary.md`: Episode summary index
- `characters.md`: Character profiles
- `foreshadowing.md`: Foreshadowing tracker
- `style_guide.md`: Fixed art style and negative prompts
- `episodes/`: Episode scripts
- `render_input/`: Exported render input scripts

### Style Consistency

All episodes in the same project must use the same `style_guide.md`. The model should read the fixed style guide instead of inventing ad-hoc art styles or negative prompts per episode.

---

## Quick Start

### 1. Initialize a project

```bash
python scripts/init_project.py "Project Name" --output ~/comic-projects --mode B --episodes 6
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

### 2. Generate an episode

Example prompt:

```text
Write episode 1 of a school romance comic in mode B.
```

Save output to:

```text
projects/<project-name>/episodes/ep001_<title>.md
```

### 3. Update project files

```bash
python scripts/update_project.py episodes/ep001_<title>.md --project-dir projects/<project-name> --episode-num 1
```

### 4. Validate quality

```bash
python scripts/validate_episode.py episodes/ep001_<title>.md --project-dir projects/<project-name>
python scripts/consistency_check.py episodes/ep001_<title>.md --project-dir projects/<project-name>
```

### 5. Export to story-renderer

```bash
python scripts/export_for_render.py episodes/ep001_<title>.md --project-dir projects/<project-name> --style-guide projects/<project-name>/style_guide.md
```

Output:

```text
projects/<project-name>/render_input/ep001_<title>_render.md
```

The generated file can then be rendered by story-renderer into images or video.

---

## Density Modes

| Mode | Description | Recommended for |
|------|-------------|-----------------|
| A | Dialogue-heavy, fewer Panels, about 30-40 Panels per episode | Romance, daily life, dialogue-heavy stories |
| B | Balanced mode, about 50-60 Panels per episode | General comic scripts |
| C | Cinematic mode, about 150-250 Panels per episode | Action, short-drama pacing, cinematic scenes |

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/init_project.py` | Initialize project files and `style_guide.md` |
| `scripts/update_project.py` | Extract characters, foreshadowing, and summaries from episodes |
| `scripts/validate_episode.py` | Validate Page/Panel format and required fields |
| `scripts/consistency_check.py` | Check character consistency and missing profile entries |
| `scripts/check_update.py` | Check whether the remote repository has updates |
| `scripts/batch_generate.py` | Generate multiple comic projects in batch |
| `scripts/export_for_render.py` | Export Panels into story-renderer compatible render input |

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
│   ├── ep001_<title>.md
│   └── ep002_<title>.md
├── render_input/
│   └── ep001_<title>_render.md
└── rendered/
    └── ep001/
```

---

## Render Bridge Workflow

v1.8.1 adds `export_for_render.py`, which converts generated Page/Panel episodes into story-renderer compatible `## 镜头 N` manual storyboard scripts.

Workflow:

1. Generate and review the comic script
2. Select the episode to render
3. Run `export_for_render.py`
4. Review the generated file under `render_input/`
5. Use story-renderer to generate images or video

This keeps the workflow staged:

- Stage 1: Generate and review scripts only
- Stage 2: Spend image/video generation quota only after the script is approved

---

## Privacy and Configuration Policy

The skill itself should not contain user-specific information. Real data belongs in user-owned configuration or project directories, such as:

- GitHub username
- API keys
- Server IPs
- Production domains
- Local user paths
- Model provider configuration

README files and scripts should use placeholders such as `YOUR_DOMAIN`, `YOUR_SERVER_IP`, and `YOUR_MODEL_PROVIDER`.

---

## Changelog

### v1.8.1

- Fixed render export format to story-renderer's manual storyboard standard: `## 镜头 N`
- Replaced username-dependent badges with static generic badges

### v1.8.0

- Integrated story-renderer bridge workflow
- Added `scripts/export_for_render.py`
- Supports exporting generated episodes into `render_input/*.md`
- Updated README to Page/Panel format and removed old Scene examples
- Removed user-specific information from skill documentation

### v1.7.0

- Upgraded comic format to Page/Panel
- Added panel shape, bubbles, narration, sound effects, transition fields
- Added ending hook and next episode teaser
- Continuation must read the previous episode's last 3 Panels
- Art style is read from `style_guide.md`

---

## License

MIT
