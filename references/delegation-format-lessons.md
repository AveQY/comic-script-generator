# 子代理（delegate_task）生成漫画脚本的格式陷阱

本记录来自一次通过 `delegate_task` 并行生成 6 集合租漫画稿的实战，总结了子代理生成格式频频出错的根因和解决方案。

## 核心问题

**子代理（leaf agent）拿到指令后倾向于自己发明格式**，而不是严格遵循指令中描述的 markdown 格式。常见偏差：

| 期望格式 | 子代理实际产出 | 后果 |
|----------|---------------|------|
| `**格子**：横向大格` | `| 格子 \| 内容 \|` 表格格式 | `validate_episode.py` 无法解析 |
| `- 角色名："台词"` | `- **角色**：角色名` 或 YAML 键值 | `update_project.py` 误提取虚假角色 |
| `### Panel 1` | `### Panel 1-1` 带副编号 | 格式校验过但统计偏移 |
| Panel 后 `---` 分隔线 | 无分隔或 `\n---\n` 位置错误 | 无法正确分割 Panel |

## 根因分析

子代理没有完整的 skill 上下文，仅靠一段 prompt 理解格式。当 prompt 中格式描述与它训练数据中的常见漫画格式冲突时，它会选择自己在训练数据中看到的模式（表格、YAML、结构化数据）。

## 解决方案

### 1. 在 delegate_task 指令中嵌入完整示例（而不是描述）

**错误做法**——只用文字描述格式：
```
格式：每个 Panel 包含格子、画面、构图等字段
```

**正确做法**——嵌入完整可复制的 Panel 示例：
```
格式必须严格如下：

### Panel 1

**格子**：横向大格
**画面**：具体画面描述
**构图**：远景/中景/特写

**气泡**：
- 角色名："台词"

**旁白**：
- 旁白框（位置）："内容"

**拟声**：
- `拟声词`：描述

**转场**：动作转场

**AI 提示词**：
正向：
```text
masterpiece, best quality, [固定风格前缀], [场景描述]
```
反向：
```text
worst quality, low quality, [固定后缀]
```

---
```

### 2. 所有 delegate_task 生成后必须运行 validate_episode.py

```
# 快速验证格式
python3 scripts/validate_episode.py episodes/epXXX_xxx.md --project-dir projects/<项目名>
```

如果 `passed: false` 或 `panels` 异常（<30 或 >70 ），必须重新生成。

### 3. 气泡中"冠名注释"的格式陷阱

避免这样写（会导致 `update_project.py` 提取虚假角色）：
```
- 王乐乐咽下去："真的！"
- 门内传来闷闷的声音："唔……"
- 左格：苏然："客厅不是画室"
```

改为这样写（把位置/动作说明放在括号内）：
```
- 王乐乐（咽下去）："真的！"
- （门内）林默："唔……"
- （左格）苏然："客厅不是画室"
```

### 4. 先手动写第一集示范，再用 delegate_task 生成后续

- 自己手写第 1 集作为格式锚点
- 后续集数通过 delegate_task 并行生成
- 指令中加上 `参考同项目已有稿子的格式：cat episodes/ep001_xxx.md | head -50`

## render_images.py 常见陷阱

### `--limit` 默认值为 1

```
render_images.py <file>          # 只渲 1 张！
render_images.py <file> --limit 999   # 渲全部
```

**每次调用必须显式传 `--limit 999` 或明确指定数量。**

### `--output-dir` 会导致各 episode 输出互相覆盖

错误用法：
```
# 所有 episode 输出到同一目录，scene_001.png 被不断覆盖
for ep in *_render.md; do
  render_images.py $ep --output-dir rendered/
done
```

正确用法：不传 `--output-dir`，让脚本自动创建 `rendered/<prompt_file_stem>/` 子目录：
```
for ep in *_render.md; do
  render_images.py $ep --limit 999 --workers 5 --sleep 0.2
done
```

### 并发参数推荐值

- `--workers 5`：稳定并发数
- `--retries 2`：瞬时失败重试
- `--sleep 0.2`：请求间微小延迟避免限流

### API 不可用时的降级

如果 `/v1/images/generations` 超时或返回 000，说明后台生图服务不可用。此时可降级到：
- 系统内置 `image_generate` 工具（走 FAL.ai FLUX 2 Klein 9B）
- 先试渲 1-2 张确认 API 恢复后再批量