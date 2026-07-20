# 轻小说单项目快速生成 —— 实操食谱

从零开始生成一个完整轻小说项目（characters.md + summary.md + foreshadowing.md + 前N章）的紧凑流程，适用于用户直接提出完整项目请求的场景。

## 流程概述

```
怀才不遇 → 规划内容（全书设定+角色+伏笔+每章正文）
  → 写 single Python script（全部内容塞一个文件）
  → 用 write_file 写脚本 → terminal 执行
  → 内联验证（字数/插图/对白/钩子/污染）
  → 字数不足时整章重写（不是 patch）
  → 最终验证通过
```

## 步骤

### Step 1: 目录与技能加载
```bash
mkdir -p projects/<项目名>/light_novel
skill_view(name='comic-script-generator')  # 加载轻小说模式六
```

### Step 2: 规划内容
先构思：
- 全书卖点、类型、基调、主线 → 放入 `summary.md`
- 主要角色（全名、年龄、外貌、性格、背景、说话风格、欲望/恐惧/秘密）→ `characters.md`（每个≥4属性）
- 每章伏笔 → `foreshadowing.md`（未回收列表）
- 每章 beats：开场钩子 → 场景建立 → 触发事件 → 互动推进 → 情绪转折 → 章末钩子
- 每章至少 3 个插图点（`<!-- ILLUST_N -->`）

### Step 3: 编写单脚本
把全部 6 个文件的内容塞进同一个 Python 脚本：

```python
content = r"""..."""
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
```

关键规则：
- 用 `r"""..."""` 规避转义问题（对 `「」`、`——`、反斜杠友好）
- 每章正文用 `# 第N章：标题\n\n---\n\n` 开头
- 对白格式：`「台词」——角色名`（独占一行）
- 段落 80-180 字，移动端阅读友好
- 禁止漫画字段：`**格子**`、`**构图**`、`**转场**`、`### Panel`、`## Page`
- 每章末尾写 `## 章末钩子`

### Step 4: 内联验证
脚本末尾附验证段：

```python
def count_cjk(text):
    # body-only: 去掉 --- 前标题、## 章末钩子 之后、ILLUST标记、引用块
    body = text.split('---\\n\\n', 1)[1]
    body = body.split('## 章末钩子')[0]
    body = re.sub(r'<!-- ILLUST_\\d+ -->', '', body)
    return sum(1 for c in body if '\\u4e00' <= c <= '\\u9fff')
```

检查四项：
1. **纯CJK body-only ≥2600**（脚本口径全非空白 ≥3000）
2. **`<!-- ILLUST_\\d+ -->` ≥3**
3. **`## 章末钩子` 存在**
4. **无漫画字段污染**

### Step 5: 字数不足 → 整章重写
| 缺字数 | 策略 |
|--------|------|
| <200 | 可以 `patch` 段级增补（对白前加心理/环境，对白后加余韵） |
| 200+ | **整章重写**——用 `write_file` 覆盖完整新内容 |

整章重写技巧：在关键场景中增加：
- 环境细节（光线、声音、气味、温度、质感）
- 角色心理描写（犹豫、恐惧、回忆、联想）
- 梦境/幻想片段
- 对话交换增加一来一回

### Step 6: 验证通过后交付
确认：
- 所有文件路径正确
- 无 heredoc 残留（不在此流程中发生）
- 字数以 body-only 纯CJK 口径为准，比 bundled 脚本口径更严格
- 无 Unicode 块越界污染（Cyrillic/Hebrew/扩展Latin混入）

## 与漫画项目的关系

- 元数据目录 = `projects/<项目名>/`（与漫画项目共用 `characters.md`/`summary.md`/`foreshadowing.md` 定义）
- 正文目录 = `light_novel/lnXXX_标题.md` 而非 `episodes/epXXX_标题.md`
- 漫画 skill 的 `validate_light_novel.py` 自动验证小说项目
- 漫画 skill 的 Reader 书架通过 `content_mode: light_novel` 识别小说项目

## 陷阱

- **对白格式**：所有被脚本统计的对白必须 `「台词」——角色名` 同行格式，叙述式归因不计入对白数
- **字数口径**：body-only 纯CJK 比 bundled 脚本整文计数少 200-500 字。安全目标：纯CJK ≥2600
- **插图标记**：`<!-- ILLUST_N -->` 中 `N` 是数字，不能有空格，不能写成 `ILLUST_1_`
- **章末钩子**：必须在 `## 章末钩子` 后面有正文内容，不能只有空行