# Batch Generation Reference

## 设计约束（来自用户原话）

- "自行抉择热点话题，每一个独立项目去生成"
- "完成一个项目，不要留存记忆的去完成下一个项目，避免超出你的上下文"
- "驱动方式你可以通过脚本或者其他方式去自行驱动自己完成，直至完成用户的量"
- "每次批量生成前让用户选择模式，然后后面都遵循这个模式"

## 实际实现结构

```
scripts/batch_generate.py
├── fetch_baidu_hotspots()      # 百度热搜抓取
├── fallback_hot_topics()       # LLM/硬编码兜底
├── generate_outline()          # 生成完整大纲（不截断）
├── generate_episode()          # 单集生成，传入完整大纲
├── run_validation()            # 验证脚本包装，容错处理
├── run_batch()                 # 主控制器
│   ├── load_checkpoint()       # 断点续传
│   ├── estimate_cost()         # 启动前成本估算
│   ├── init_project()          # 调用 init_project.py
│   ├── generate_outline_and_episodes()
│   ├── run_validation()
│   └── save_checkpoint()
└── main()                      # CLI 入口
```

## 关键参数默认值

| 参数 | 默认值 | 说明 |
|------|--------|------|
| --count | 必填 | 故事数量 |
| --mode | B | A/B/C，所有项目统一 |
| --episodes | 5 | 每故事集数 |
| --output | ~/comic-projects | 输出目录 |
| --auto | false | 全自动模式 |
| --art-style | (default) | AI 绘图风格 |

## 错误处理矩阵

| 错误类型 | 处理方式 | 用户可见 |
|----------|----------|----------|
| 网络超时/Connection reset | 指数退避重试 3 次 | RETRY 1/3... |
| HTTP 429/500/502/503/504 | 指数退避重试 3 次 | RETRY 1/3... |
| LLM 返回空 | 标记 FAILED，继续下一个 | X FAILED |
| 验证脚本超时 60s | 跳过该集，标记 WARN | [WARN] timeout |
| 百度抓取失败 | 回退 LLM 生成话题 | Baidu failed, using fallback |
| 无可用话题 | 回退 20 个硬编码安全话题 | (silent fallback) |
| 用户 Ctrl+C | 保存 checkpoint，安全退出 | Batch interrupted |

## 速率限制配置

- episode 间延迟：random.uniform(1.5, 3.0) 秒
- story 间冷却：random.uniform(2.0, 5.0) 秒（auto 模式）
- 手动模式无冷却，靠用户按 Enter 控制节奏

## Token 估算公式

```
outline_tokens = 4000
ep_tokens = {A: 4000, B: 8000, C: 20000}[mode]

total_llm_calls = stories * (1 + episodes)
total_input_tokens = stories * (outline_tokens + episodes * 2000)
total_output_tokens = stories * (outline_tokens + episodes * ep_tokens)
time_per_call = {A: 15, B: 25, C: 35} 秒
```

## 项目命名规则

```
batch_{YYYYMMDD}_{HHMMSS}_{index}_{uuid8}
例：batch_20260625_143022_001_a1b2c3d4
```

## 报告文件格式

```json
{
  "timestamp": "2026-06-25T14:30:22+08:00",
  "mode": "B",
  "episodes_per_story": 5,
  "total_time": 1234.5,
  "total_tokens_estimate": 150000,
  "results": [
    {
      "name": "batch_20260625_143022_001_a1b2c3d4",
      "topic": "上班族的周末治愈日常",
      "status": "OK",
      "episodes": 5,
      "time": "123s"
    }
  ]
}
```
