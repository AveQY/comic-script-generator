# 批量生成失败时的会话内兜底流程

## 触发条件

用户要求批量生成完整漫画稿子项目，优先运行 `scripts/batch_generate.py`。如果脚本已完成项目初始化，但在调用 LLM 生成大纲或分集时失败，而当前 Hermes 会话仍可继续生成文本，应切换到会话内兜底，不要只向用户报告失败。

常见表现：
- `Generating outline... [LLM HTTP 403]`
- `HTTP 503 auth_unavailable`
- 子代理/后台脚本无鉴权，但主会话仍可回复

这些是当次执行路径的问题，不应固化为“脚本不可用”的永久结论。

## 兜底步骤

1. 为每个目标项目创建唯一目录，建议：
   - `/path/to/comic-projects/projects/async_comic_001_<timestamp>`
   - `/path/to/comic-projects/projects/async_comic_002_<timestamp>`
2. 写入基础文件：
   - `config.json`
   - `style_guide.md`
   - `summary.md`
   - `characters.md`
   - `foreshadowing.md`
   - `episodes/ep001_*.md ...`
3. 自选安全、适合漫画的题材；避开灾难、过重时政、真实人物争议。
4. 每集使用 Page/Panel 结构。即使为了速度降低 Panel 数，也必须完整：开端、推进、转折、结尾钩子、下集提示。
5. 每个 Panel 必须包含：
   - `格子`
   - `画面`
   - `构图`
   - `气泡`
   - `旁白`
   - `拟声`
   - `转场`
   - `AI 提示词`（正向/反向）
6. 生成后做基础验证：
   - 项目数是否正确
   - 每项目集数是否正确
   - 每集 Page/Panel 数
   - 必填字段是否存在
   - `summary.md`、`characters.md`、`foreshadowing.md` 是否非空
7. 回复用户时明确区分：
   - 脚本路径失败原因
   - 已采用会话兜底完成
   - 项目绝对路径与验证结果

## 最小验证脚本思路

```python
from pathlib import Path
import re, json
for proj in projects:
    cfg = json.loads((proj/'config.json').read_text(encoding='utf-8'))
    eps = sorted((proj/'episodes').glob('ep*.md'))
    for ep in eps:
        s = ep.read_text(encoding='utf-8')
        panels = len(re.findall(r'^### Panel \\d+', s, re.M))
        pages = len(re.findall(r'^## Page \\d+', s, re.M))
        required = all(x in s for x in [
            '**格子**','**画面**','**构图**','**气泡**','**旁白**','**拟声**','**转场**','**AI 提示词**',
            '## 本集结尾钩子','## 下集提示'
        ])
```

## 回复格式建议

简洁列出：
- 项目名
- 绝对路径
- 题材一句话
- 集数 / Panel 数
- 验证：PASS 或 WARN
