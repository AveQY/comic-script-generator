# Comic Script Generator

根据大纲或热点生成漫画分镜稿。支持三种分镜密度模式、项目管理、角色档案、伏笔追踪，以及全自动批量生成。

## 特性

- **三种分镜密度**：A（对话多/镜头少）、B（平衡）、C（电影短剧风）
- **每个场景附带 AI 绘图提示词**：正向/反向提示词，适配 Midjourney / Stable Diffusion / DALL-E
- **自动化脚本**：初始化、更新项目文件、验证分集、角色一致性检查、批量生成
- **热点驱动**：自动抓取百度热搜，筛选适合创作的话题
- **批量模式**：全自动生成多个独立漫画项目，支持断点续传

## 快速开始

### 初始化项目

```bash
python scripts/init_project.py "我的漫画" --mode B --episodes 5
```

### 生成分镜

使用 Hermes 对话生成，或调用 LLM API 直接生成。

### 验证与更新

```bash
python scripts/update_project.py episodes/ep001_xxx.md --project-dir projects/我的漫画 --episode-num 1
python scripts/validate_episode.py episodes/ep001_xxx.md --project-dir projects/我的漫画
python scripts/consistency_check.py episodes/ep001_xxx.md --project-dir projects/我的漫画
```

### 批量生成

```bash
python scripts/batch_generate.py --count 5 --mode B --auto
python scripts/batch_generate.py -n 3 -m C -e 4 --art-style "宫崎骏风格"
python scripts/batch_generate.py -n 2 -m A -o ./my-comics
```

参数说明：
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--count` / `-n` | 生成故事数量（必填） | — |
| `--mode` / `-m` | 分镜密度 A/B/C | B |
| `--episodes` / `-e` | 每故事集数 | 5 |
| `--output` / `-o` | 输出目录 | ~/comic-projects |
| `--art-style` / `-a` | AI 绘图风格描述 | (default) |
| `--auto` | 全自动模式，不暂停确认 | false |

## 项目结构

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

## 分镜密度模式

| 模式 | 风格 | 每集场景数 | 适用类型 |
|------|------|-----------|---------|
| A | 对话多，镜头少 | 30-40 | 恋爱、日常、推理 |
| B | 平衡模式 | 50-60 | 通用 |
| C | 电影短剧风 | 150-250 | 动作、悬疑、剧情 |

## 更新地址

源仓库：https://github.com/AveQY/comic-script-generator

## 更新检查

每次使用前运行 `python scripts/check_update.py` 检查是否有新版本。网络不通时自动跳过。

## License

MIT
