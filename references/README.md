# Comic Script Generator

<p align="center">
  <img src="https://img.shields.io/github/stars/AveQY/comic-script-generator?style=social" alt="GitHub stars">
  <img src="https://img.shields.io/github/forks/AveQY/comic-script-generator?style=social" alt="GitHub forks">
  <img src="https://img.shields.io/github/issues/AveQY/comic-script-generator" alt="GitHub issues">
  <img src="https://img.shields.io/github/license/AveQY/comic-script-generator" alt="License">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python Version">
</p>

<p align="center">
  <strong>一个智能化的漫画分镜脚本创作工具</strong><br>
  <strong>An intelligent storyboard script creation tool</strong>
</p>

<p align="center">
  <a href="#中文版">中文版</a> •
  <a href="#english-version">English</a> •
  <a href="#快速开始">快速开始</a> •
  <a href="#示例">示例</a> •
  <a href="#贡献">贡献</a>
</p>

---

## 中文版

### 📖 简介

**Comic Script Generator（漫画脚本生成器）** 是一个智能化的漫画分镜脚本创作工具，专为漫画家、插画师、内容创作者设计。它可以根据用户提供的大纲或热点话题，自动生成详细的分镜脚本，包含画面描述、镜头角度、角色对话等完整内容。

### ✨ 核心特性

#### 🎬 两种创作模式
- **大纲模式**：用户提供故事大纲，AI 生成详细分镜脚本
- **热点模式**：自动抓取热门话题，生成创意内容

#### 📁 项目管理系统
- **长篇连载支持**：按集数管理，支持多集连载故事
- **智能摘要**：自动提取每集关键内容，避免上下文过载
- **角色档案**：自动创建和维护角色信息库
- **伏笔追踪**：记录未回收的伏笔，防止剧情遗漏

#### 🔥 热点话题抓取
支持从以下平台抓取热点：
- 哔哩哔哩（B站）
- 抖音
- 微博热搜
- 知乎热榜
- 百度热搜
- 豆瓣评分

**时效性**：15天内热点  
**类型**：全类型覆盖

#### 🎨 详细分镜格式
每个场景包含：
- **镜头类型**：远景 / 中景 / 特写 / 俯拍 / 仰拍
- **画面描述**：人物表情、动作、环境细节、光线氛围
- **对话/旁白**：角色对话、心理独白、旁白说明

### 🚀 快速开始

#### 安装要求
- Hermes Agent 或兼容的 AI Agent 框架
- Python 3.8+（用于文件操作）

#### 使用方法

1. **加载 Skill**
```
加载 comic-script-generator skill
```

2. **初始化项目**
首次使用时，系统会引导你设置项目保存位置（默认 `~/comic-projects/`）

3. **开始创作**

**方式一：提供大纲**
```
帮我写一个校园恋爱故事的第一集

大纲：
- 男主角阿明在天台遇见女主角小雨
- 小雨向阿明表白
- 阿明陷入回忆
```

**方式二：抓取热点**
```
我没有灵感，帮我找热点话题
```

系统会自动抓取并展示 TOP10 热点，你选择后即可生成创意内容。

### 📂 项目结构

```
<保存位置>/
├── projects/                      # 所有项目
│   └── <项目名>/
│       ├── summary.md             # 每集摘要索引
│       ├── characters.md          # 角色档案
│       ├── foreshadowing.md       # 伏笔追踪
│       └── episodes/              # 分集稿子
│           ├── ep001_天台相遇.md
│           ├── ep002_回忆往昔.md
│           └── ...
├── hotspots/                      # 热点记录
│   └── YYYY-MM-DD.md
└── config.json                    # 配置文件
```

### 📝 分镜脚本示例

```markdown
# 第1集：天台相遇

**故事梗概**：放学后，男主角阿明在天台遇见女主角小雨，小雨鼓起勇气向他表白。

---

## Scene 1
**镜头**：远景  
**画面**：黄昏的城市天台，夕阳将天空染成橙红色。主角阿明站在栏杆边，背对镜头，双手插兜，侧脸若有所思。风吹起他的短发和校服衣摆。背景是模糊的高楼剪影。  
**对话**：  
- 旁白："那天放学后，我第一次站在这里。"

---

## Scene 2
**镜头**：特写  
**画面**：阿明的侧脸特写，眼神坚定但带着一丝迷茫。睫毛在夕阳下投下细微阴影。  
**对话**：  
- 阿明（心理独白）："如果我当时选择了另一条路……"

---

## Scene 3
**镜头**：中景  
**画面**：天台门突然打开，女主小雨跑进来，喘着气，脸颊微红。她穿着白色衬衫和格子裙，马尾辫在身后晃动。阿明转身，表情惊讶。  
**对话**：  
- 小雨："阿明！你还在这里啊！"  
- 阿明："小雨？你怎么……"

*本集完*
```

### 🎭 角色档案示例

```markdown
# 角色档案

## 阿明
- **全名**：李明
- **年龄**：17岁
- **外貌**：黑色短发，偏瘦，常穿校服。眼神锐利但温柔。
- **性格**：内向、细腻、责任感强，不善表达情感。
- **背景**：单亲家庭，父亲早逝，与母亲相依为命。
- **首次登场**：第1集
- **关键情节**：在天台遇见小雨（第1集）

## 小雨
- **全名**：陈雨欣
- **年龄**：16岁
- **外貌**：齐肩马尾辫，大眼睛，笑起来有酒窝。常穿白衬衫 + 格子裙。
- **性格**：开朗、主动、乐观，但内心敏感。
- **背景**：父母工作忙碌，常感到孤独。
- **首次登场**：第1集
- **关键情节**：向阿明表白（第1集）
```

### 🔖 伏笔追踪示例

```markdown
# 伏笔追踪

## 未回收
- [ ] 阿明父亲的遗物（第2集埋下）
- [ ] 小雨手机里的神秘短信（第3集埋下）
- [ ] 天台栏杆上的涂鸦（第1集埋下）

## 已回收
- [x] 阿明的转学原因（第5集埋下，第8集回收）
- [x] 小雨的家庭矛盾（第4集埋下，第7集回收）
```

### 🛠️ 适用场景

- **漫画创作**：生成详细分镜脚本，直接用于绘画
- **视频脚本**：为短视频、动画提供分镜设计
- **小说改编**：将文字转换为视觉化分镜
- **AI 绘画**：生成详细的画面描述，用于 Stable Diffusion、Midjourney 等工具
- **创意灵感**：基于热点话题快速生成创意内容

### 💡 使用技巧

1. **长篇连载**：续写时只需提供项目名称，系统会自动读取历史上下文
2. **角色一致性**：系统会自动维护角色档案，确保前后描述一致
3. **伏笔管理**：定期检查 `foreshadowing.md`，避免伏笔遗漏
4. **摘要索引**：`summary.md` 可以快速了解整个项目进展

### 🤝 贡献

欢迎提交 Issue 和 Pull Request！

**改进建议：**
- 新增热点平台支持
- 优化分镜格式模板
- 增加更多创作模式

### 📄 许可证

MIT License

### 📞 联系方式

如有问题或建议，欢迎通过 GitHub Issues 联系。

---

## English Version

### 📖 Introduction

**Comic Script Generator** is an intelligent storyboard script creation tool designed for comic artists, illustrators, and content creators. It automatically generates detailed storyboard scripts based on user-provided outlines or trending topics, including scene descriptions, camera angles, character dialogues, and more.

### ✨ Core Features

#### 🎬 Two Creation Modes
- **Outline Mode**: Users provide story outlines, AI generates detailed storyboard scripts
- **Trending Mode**: Automatically captures trending topics and generates creative content

#### 📁 Project Management System
- **Long-form Series Support**: Manage by episodes, support multi-episode serialized stories
- **Smart Summaries**: Automatically extract key content from each episode to avoid context overload
- **Character Profiles**: Automatically create and maintain character information database
- **Foreshadowing Tracker**: Record unresolved foreshadowing to prevent plot omissions

#### 🔥 Trending Topic Scraping
Supports scraping from the following platforms:
- Bilibili
- Douyin (TikTok China)
- Weibo Hot Search
- Zhihu Hot List
- Baidu Hot Search
- Douban Ratings

**Timeliness**: Within 15 days  
**Type**: All categories covered

#### 🎨 Detailed Storyboard Format
Each scene includes:
- **Shot Type**: Wide shot / Medium shot / Close-up / High angle / Low angle
- **Scene Description**: Character expressions, actions, environmental details, lighting atmosphere
- **Dialogue/Narration**: Character dialogue, internal monologue, narration

### 🚀 Quick Start

#### Requirements
- Hermes Agent or compatible AI Agent framework
- Python 3.8+ (for file operations)

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

The system will automatically scrape and display TOP10 trending topics. Select one to generate creative content.

### 📂 Project Structure

```
<save-location>/
├── projects/                      # All projects
│   └── <project-name>/
│       ├── summary.md             # Episode summary index
│       ├── characters.md          # Character profiles
│       ├── foreshadowing.md       # Foreshadowing tracker
│       └── episodes/              # Episode scripts
│           ├── ep001_rooftop_encounter.md
│           ├── ep002_memories.md
│           └── ...
├── hotspots/                      # Trending records
│   └── YYYY-MM-DD.md
└── config.json                    # Configuration file
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
