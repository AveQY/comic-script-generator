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
  <a href="#快速开始">快速开始</a> •
  <a href="#示例">示例</a> •
  <a href="#贡献">贡献</a> •
  <a href="README.en.md">English</a>
</p>

---

## 📖 简介

**Comic Script Generator（漫画脚本生成器）** 是一个智能化的漫画分镜脚本创作工具，专为漫画家、插画师、内容创作者设计。它可以根据用户提供的大纲或热点话题，自动生成详细的分镜脚本，包含画面描述、镜头角度、角色对话等完整内容。

### ✨ 核心特性

#### 🎬 多种创作模式
- **大纲模式**：用户提供故事大纲，AI 生成详细分镜脚本
- **热点模式**：自动抓取热门话题，生成创意内容
- **批量模式**：全自动生成多个独立漫画项目，支持断点续传

#### 📁 项目管理系统
- **长篇连载支持**：按集数管理，支持多集连载故事
- **智能摘要**：自动提取每集关键内容，避免上下文过载
- **角色档案**：自动创建和维护角色信息库
- **伏笔追踪**：记录未回收的伏笔，防止剧情遗漏

#### 🎨 三种分镜密度模式
- **模式 A**：对话多，镜头少（传统漫画风，每集 30-40 场景）
- **模式 B**：一个对话对应一个镜头（平衡模式，每集 50-60 场景）
- **模式 C**：一段对话多个镜头（电影短剧风，每集 150-250 场景）

#### 🤖 自动化脚本
- `init_project.py` — 项目初始化，自动创建目录结构和配置文件
- `update_project.py` — 自动更新项目文件，提取角色/伏笔/摘要
- `validate_episode.py` — 分集验证，检查场景数、AI 提示词完整性
- `consistency_check.py` — 角色一致性检查
- `batch_generate.py` — 批量生成，自动抓取热点并生成多个独立项目

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

**方式三：批量生成**
```
帮我批量生成 5 个漫画故事，模式 B，全自动
```

系统会自动抓取热点，循环生成 5 个独立项目，每个项目包含完整的大纲和分集脚本。

### 📂 项目结构

```
projects/<项目名>/
├── config.json          # 项目配置
├── summary.md           # 每集摘要索引
├── characters.md        # 角色档案
├── foreshadowing.md     # 伏笔追踪
├── outline.md           # 故事大纲
└── episodes/
    ├── ep001_<标题>.md
    ├── ep002_<标题>.md
    └── ...
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
5. **批量生成**：使用 `batch_generate.py` 可自动抓取热点并生成多个独立项目

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

## 📊 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=AveQY/comic-script-generator&type=Date)](https://star-history.com/#AveQY/comic-script-generator&Date)

---

**Star ⭐ this repo if you find it helpful!**

## 🌟 Contributors

<a href="https://github.com/AveQY/comic-script-generator/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=AveQY/comic-script-generator" />
</a>
