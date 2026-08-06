---
name: csg-mode4-batch
description: >-
  批量生成多个独立漫画项目，自动抓取热点话题，循环创建项目骨架、生成脚本、验证。支持 batch_generate.py 驱动。
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, terminal
---

### 模式四：批量生成（热点驱动）

**触发条件**：用户明确要求"批量生成"或指定了故事数量。

**前置选择（只选一次）**：
- 分镜密度模式：A / B / C（后续所有项目统一遵循）
- 每集集数：默认 5 集
- AI 绘图风格：可选
- 自动模式：`--auto` 参数表示全自动，不加则每完成一个项目暂停等待用户确认

**执行流程**：

1. **抓取热点**（只执行一次）
   - 调用 `fetch_baidu_hotspots()` 获取百度热搜
   - 如果抓取失败，回退到 `fallback_hot_topics()` 用 LLM 生成候选话题
   - 过滤掉时政、灾难、暴力等不适合漫画的内容

2. **循环生成**（独立项目，不保留上下文）
   - 从候选话题中轮流选择（避免重复）
   - 每个项目：
     a. 调用 `init_project.py` 创建独立项目骨架和 `style_guide.md`
     b. 调用 LLM 生成大纲 + Page/Panel 格式的分集漫画脚本
     c. 运行 `update_project.py` 自动更新项目文件
     d. 运行 `validate_episode.py` + `consistency_check.py` 验证
     e. 保存汇总结果，**清空上下文**，继续下一个
   - 脚本通过 `batch_generate.py` 驱动，不依赖 Hermes 会话记忆

3. **输出汇总**
   - 控制台输出每个项目的状态（✓ / ⚠ / ✗）
   - 生成 `batch_report_YYYYMMDD_HHMMSS.json` 报告文件

**运行命令**：
```bash
python scripts/batch_generate.py --count 5 --mode B --auto
python scripts/batch_generate.py --count 3 --mode C --episodes 4 --art-style "宫崎骏风格"
python scripts/batch_generate.py -n 2 -m A -o ./my-comics
```

**参数说明**：
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--count` / `-n` | 生成故事数量（必填） | — |
| `--mode` / `-m` | 分镜密度 A/B/C | B |
| `--episodes` / `-e` | 每故事集数 | 5 |
| `--output` / `-o` | 输出目录 | ~/comic-projects |
| `--art-style` / `-a` | AI 绘图风格描述，支持预设 key 或自定义描述 | `japanese-modern` |
| `--auto` | 全自动模式，不暂停确认 | false |

**设计要点**：
- 每个项目完全独立，生成完成后不保留 LLM 上下文
- 热点话题只抓取一次，轮换使用
- 失败的项目跳过并记录，不影响其他项目
- 验证不通过标记为 WARN 而非终止
