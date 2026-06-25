# Comic Script Generator

<p align="center">
  <img src="https://img.shields.io/github/stars/AveQY/comic-script-generator?style=social" alt="GitHub stars">
  <img src="https://img.shields.io/github/forks/AveQY/comic-script-generator?style=social" alt="GitHub forks">
  <img src="https://img.shields.io/github/issues/AveQY/comic-script-generator" alt="GitHub issues">
  <img src="https://img.shields.io/github/license/AveQY/comic-script-generator" alt="License">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python Version">
</p>

<p align="center">
  <strong>An intelligent storyboard script creation tool</strong>
</p>

<p align="center">
  <a href="README.md">中文</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#examples">Examples</a> •
  <a href="#contributing">Contributing</a>
</p>

---

## 📖 Introduction

**Comic Script Generator** is an intelligent storyboard script creation tool designed for comic artists, illustrators, and content creators. It automatically generates detailed storyboard scripts based on user-provided outlines or trending topics, including scene descriptions, camera angles, character dialogues, and more.

### ✨ Core Features

#### 🎬 Multiple Creation Modes
- **Outline Mode**: Users provide story outlines, AI generates detailed storyboard scripts
- **Trending Mode**: Automatically captures trending topics and generates creative content
- **Batch Mode**: Fully automatic generation of multiple independent comic projects with resume support

#### 📁 Project Management System
- **Long-form Series Support**: Manage by episodes, support multi-episode serialized stories
- **Smart Summaries**: Automatically extract key content from each episode to avoid context overload
- **Character Profiles**: Automatically create and maintain character information database
- **Foreshadowing Tracker**: Record unresolved foreshadowing to prevent plot omissions

#### 🎨 Three Density Modes
- **Mode A**: Dialogue-heavy, fewer shots (traditional comic style, 30-40 scenes per episode)
- **Mode B**: Balanced mode (50-60 scenes per episode)
- **Mode C**: Cinematic style (150-250 scenes per episode)

#### 🤖 Automated Scripts
- `init_project.py` — Project initialization
- `update_project.py` — Auto-update project files
- `validate_episode.py` — Episode validation
- `consistency_check.py` — Character consistency check
- `batch_generate.py` — Batch generation with hot topics

### 🚀 Quick Start

#### Requirements
- Hermes Agent or compatible AI Agent framework
- Python 3.8+

#### Usage

1. **Load Skill**
```
Load comic-script-generator skill
```

2. **Initialize Project**
On first use, the system will guide you to set the project save location (default `~/comic-projects/`)

3. **Start Creating**

**Method 1: Provide Outline**
```
Help me write the first episode of a campus romance story

Outline:
- Male protagonist Amin meets female protagonist Xiaoyu on the rooftop
- Xiaoyu confesses to Amin
- Amin falls into memories
```

**Method 2: Scrape Trending Topics**
```
I have no inspiration, help me find trending topics
```

**Method 3: Batch Generation**
```
Help me batch generate 5 comic stories, mode B, fully automatic
```

### 📂 Project Structure

```
projects/<project-name>/
├── config.json          # Project configuration
├── summary.md           # Episode summary index
├── characters.md        # Character profiles
├── foreshadowing.md     # Foreshadowing tracker
├── outline.md           # Story outline
└── episodes/
    ├── ep001_<title>.md
    ├── ep002_<title>.md
    └── ...
```

### 📝 Storyboard Script Example

```markdown
# Episode 1: Rooftop Encounter

**Synopsis**: After school, male protagonist Amin meets female protagonist Xiaoyu on the rooftop, where Xiaoyu gathers courage to confess.

---

## Scene 1
**Shot**: Wide shot
**Scene**: A city rooftop at dusk, sunset dyes the sky orange-red. Protagonist Amin stands by the railing, back to camera, hands in pockets, side profile thoughtful. Wind blows his short hair and school uniform. Background shows blurred high-rise silhouettes.
**Dialogue**:
- Narration: "That day after school, I stood here for the first time."

---

## Scene 2
**Shot**: Close-up
**Scene**: Close-up of Amin's side profile, eyes determined yet slightly confused. Eyelashes cast subtle shadows in the sunset.
**Dialogue**:
- Amin (internal monologue): "If I had chosen another path back then..."

---

## Scene 3
**Shot**: Medium shot
**Scene**: Rooftop door suddenly opens, female lead Xiaoyu runs in, panting, cheeks flushed. She wears a white shirt and plaid skirt, ponytail swaying behind. Amin turns, expression surprised.
**Dialogue**:
- Xiaoyu: "Amin! You're still here!"
- Amin: "Xiaoyu? How did you..."

*End of Episode*
```

### 🎭 Character Profile Example

```markdown
# Character Profiles

## Amin
- **Full Name**: Li Ming
- **Age**: 17
- **Appearance**: Black short hair, slim build, usually wears school uniform. Sharp yet gentle eyes.
- **Personality**: Introverted, sensitive, strong sense of responsibility, poor at expressing emotions.
- **Background**: Single-parent family, father passed away early, lives with mother.
- **First Appearance**: Episode 1
- **Key Plot**: Meets Xiaoyu on rooftop (Episode 1)

## Xiaoyu
- **Full Name**: Chen Yuxin
- **Age**: 16
- **Appearance**: Shoulder-length ponytail, big eyes, dimples when smiling. Often wears white shirt + plaid skirt.
- **Personality**: Cheerful, proactive, optimistic, but sensitive inside.
- **Background**: Parents are busy with work, often feels lonely.
- **First Appearance**: Episode 1
- **Key Plot**: Confesses to Amin (Episode 1)
```

### 🔖 Foreshadowing Tracker Example

```markdown
# Foreshadowing Tracker

## Unresolved
- [ ] Amin's father's belongings (planted in Episode 2)
- [ ] Mysterious text on Xiaoyu's phone (planted in Episode 3)
- [ ] Graffiti on rooftop railing (planted in Episode 1)

## Resolved
- [x] Amin's transfer reason (planted in Episode 5, resolved in Episode 8)
- [x] Xiaoyu's family conflict (planted in Episode 4, resolved in Episode 7)
```

### 🛠️ Use Cases

- **Comic Creation**: Generate detailed storyboard scripts for direct illustration
- **Video Scripts**: Provide storyboard design for short videos and animations
- **Novel Adaptation**: Convert text into visual storyboards
- **AI Art**: Generate detailed scene descriptions for Stable Diffusion, Midjourney, etc.
- **Creative Inspiration**: Quickly generate creative content based on trending topics

### 💡 Tips

1. **Long-form Series**: When continuing, just provide the project name, the system will automatically read historical context
2. **Character Consistency**: System automatically maintains character profiles to ensure consistent descriptions
3. **Foreshadowing Management**: Regularly check `foreshadowing.md` to avoid missing plot points
4. **Summary Index**: `summary.md` provides quick overview of entire project progress
5. **Batch Generation**: Use `batch_generate.py` for automatic hot-topic-driven multi-project generation

### 🤝 Contributing

Issues and Pull Requests are welcome!

**Improvement Suggestions:**
- Add support for more trending platforms
- Optimize storyboard format templates
- Add more creation modes

### 📄 License

MIT License

### 📞 Contact

For questions or suggestions, please contact via GitHub Issues.

---

## 📊 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=AveQY/comic-script-generator&type=Date)](https://star-history.com/#AveQY/comic-script-generator&Date)

---

**Star ⭐ this repo if you find it helpful!**

## 🌟 Contributors

<a href="https://github.com/AveQY/comic-script-generator/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=AveQY/comic-script-generator" />
</a>
