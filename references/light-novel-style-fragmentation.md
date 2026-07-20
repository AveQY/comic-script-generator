# LLM 单章生成后半段风格退化（破折号碎片化）— 检测与修复

## 背景

本次《推理社团的死角》续写第 4–10 章过程中，在 7 章中两次（第 8 章、第 10 章）观测到一种跟此前参考资料里记录的"跨语言乱码污染"、"patch phantom 字符"、"heredoc 残留"都不同的失败模式：

**LLM 在一次 `write_file` 生成的同一章正文中，写到 ~2000–2500 字之后开始"分段断裂"——不再产出完整中文句子，而是以单字 / 双字为一个语顿，中间用密集破折号 `——` 拼接。** 这种输出仍然可以被 `validate_light_novel.py` 通过字数 / 对白 / 插图 / 漫画字段检查（因为标点 / 汉字数都"够"），但人眼一看就是不可读的。它是 LLM 在长上下文 + 长输出 + 高情绪密度段落共同作用下的注意力衰减，而不是编码错误或工具层污染。

## 观测特征（对比已有失败模式）

| 失败模式 | 本文件 | garbled-text-cleanup | patch-intext-pitfall | write_file-stream-timeout |
|---|---|---|---|---|
| 触发 | LLM 自己生成正文后段 | 跨语言 token 误出 | patch 重写时漏段 | 工具参数 >8K token |
| 可见特征 | 单字 + `——` 密集拼接 | 英文 / Cyrillic 字母 / 数字混入 | `];` / `}` / `]=` 残留 | 工具调用被截断报错 |
| 验证脚本能否捕获 | **否**（汉字数够、对白归属行够） | 是（`scan_garbled`） | 是（phantom 扫描） | 是（错误消息） |
| 出现位置 | 一章约 2000 字之后 | 全章任意 | patch 作用域 | 工具调用瞬态 |

## 实例（来自本次会话）

### 第 8 章（首次出现）

前段（正常示例）：
```
活动室又静了几秒。

「那'R'不一定是周行名字的首字母。R 可能是另一个人名字的英文首拼。」——江屿
```

后段（退化示例）：
```
活动室里——所有——全部连呼吸都停了一瞬。
——「——他在案发——之前——一年——二零一五年——"曾回校"。"回校"——
——她——说话——格式——是平的——
——「所以——不是——"案发后"——沈柏年深度涉及——"案发前——他已经——作为"——
```

到章末钧子段彻底碎片化：
```
陆远舟——这一辈子——这一刻——第一次——看见——沈柏言——那张——他——熟知过三年的
、笑得居高临下、转钢笔、引经据典的脸——上——崩——开——一条——缝
```

### 第 10 章（同型重复）

同样从大约第 70 行开始：段落被切成单字 + `——`；章末钧子退化到"——社长——和他的——前——的——朋——友——"这种无法呼吸的程度。

**二次复现的触发条件相似**：（1）一章正文 ≥3500 字；（2）后半段是高强度多角色对峙 / 揭秘；（3）`write_file` 单次写入全部内容。

## 检测方法

`validate_light_novel.py` 与 `scan_garbled()` 都检测不到这种退化（汉字数、`「」——角色名` 对白归属行全都"够"）。需要追加一段**风格密度扫描**：

```python
import re

def scan_dash_fragmentation(content: str, window_lines: int = 8, dash_density_threshold: float = 0.4):
    """检测破折号碎片化：在一个连续窗口内，若——的密度（——字符占非空白字符的比例）超过阈值且
    连续々出现 window_lines 行以上，判定为风格退化。"""
    lines = content.splitlines()
    issues = []
    for i in range(0, len(lines) - window_lines + 1):
        window = '\n'.join(lines[i:i + window_lines])
        non_ws = re.sub(r'\s', '', window)
        if not non_ws:
            continue
        dashes = window.count('——')
        # 每个——是 2 个字符（双破折号），密度按字符计更稳
        dash_chars = dashes * 2
        density = dash_chars / len(non_ws)
        # 真正退化的另一个特征：短段落多（≤6 个非空白字符的行）
        short_lines = sum(1 for ln in lines[i:i + window_lines]
                          if 0 < len(re.sub(r'\s', '', ln)) <= 6)
        if density > dash_density_threshold or short_lines >= window_lines - 2:
            issues.append({
                'start_line': i + 1,
                'dash_density': round(density, 3),
                'short_lines': short_lines,
                'preview': lines[i:i + 3],
            })
    return issues
```

阈值是经验值，可调。本次实测第 8、第 10 章退化段 `dash_density` 在 0.35–0.55 之间，`short_lines` 在 6–8 行窗口里占 6 行以上。正常情感密集段（不退化）也会有多 `——` 多对白，但 `short_lines` 通常 ≤ 3。

## 恢复方法

发现退化时，**不要用多个细粒度 patch 一行一行修**——会触发 `patch-intext-pitfall-2026-07-08.md` 记录的三重陷阱（误替换、phantom、状态脱节）。优先策略：

### 策略 A：以连续大段 patch 重写整块退化区（本次采用）

1. `read_file` 自退化起始行号往回 5–10 行（确认断点）
2. `read_file` 自章末（`## 章末钩子` 之前）读取尾段
3. 用一个 `patch` 把"退化起始行 → 章末钧子段之前"作为一个 `old_string` 整块替换为干净风格的 `new_string`——一次性重写
4. `patch` 完成后立即 `read_file` 验证相邻段未误删、无 phantom

### 策略 B（退化范围太小、仅 3–5 行）：局部 patch

只在小范围退化（少于 5 行连续碎片化）时使用，配合 `read_file` 对齐实际状态。

### 策略 C（极差，避免）：单个字符 patch

对每一个 `——` 单独 patch 修复——会触发 `patch` 的 `old_string` 唯一性失败（一般会返回 `Found N matches`）。即使添加 `replace_all=true` 也不适合，因为不同位置的 `——` 含义不同，不能统一替换为缓い顿号。

### 修复后必须验证

跑一遍 **正文一字成句密度自检**——抽样每个连续 8 行窗口，确认 `——密度 ≤0.3 且 `short_lines ≤3`。可嵌入每章正文生成后的验证脚本里。

## 预防措施

### 1. 字数分批生成（最有效）

单次 `write_file` 的中文章节正文，把单章拆成两段写入：

```python
# 第一次：写前半段（开篇到中段转折前），用 open(path, 'w') 创建文件
# 第二次：写后半段（中段转折到章末钩子），用 open(path, 'a') 追加
#                        — 追加时记得先写一个 '\n\n' 分隔行
```

**实测触发阈值**：单章一次写入正文 >3500 字、且后半段为多角色高情绪揭秘段时，退化概率显著上升。单批 ≤2500 字生成后再拼接更稳定。

### 2. 已知高危章节先 OS 级风格锚

写"多角色对峙的揭秘章节"、"主要人物倒下 / 身份揭露的章末段"之前，在表面 prompt 里用一句话提示自己保持\[中长句段\]的写作风格：

```
提示：本章后半段为高潮段而非意识流段。保持完整中文句式，禁止单字 + —— 的碎片拼接。
```

这种风格锚只是缓解，不是根治。根治仍然是分批写入 + 后续风格扫锚。

### 3. 生成后立即跑风格扫描

把 `scan_dash_fragmentation()` 作为每章验证步骤的固定一环——即使 `validate_light_novel.py` 通过，也要追跑这个检查。可以并入手边步骤里：

```python
# 生成后常规验证
validate_light_novel.py + verify_light_novel_delivery.py
# 新增
python -c "from scan_dash_fragmentation import scan; 
import sys; issues=scan(open(sys.argv[1]).read()); 
print('FRAGMENTATION' if issues else 'OK')" ln_N.md
```

### 4. 不要让退入在单点循环

本次第 10 章在重写后段时，有时还会在钩子段再次滋润入退入（见第 10 章末钧子段修复后仍残留短碎片，需要二次 patch）。视章末钩子为高风险区：附录钩子是高风险区，篇幅保持在 2–4 句，不要超过 5 行。

## 与现有文档的关系

- 与 `light-novel-garbled-text-cleanup-2026-07-08.md` 互补：那里看跨语言乱码（英文 / Cyrillic / 数字混入），这里看中文内部风格退化（破折号碎片化）。
- 与 `patch-intext-pitfall-2026-07-08.md` 互补：那里看 patch 工具本身引入的 phantom 字符，这里看原始 `write_file` 生成时已带退化、需要用 **大块 patch** 而不是"多行细 patch"修复的原因。
- 与 `light-novel-quickstart-recipe.md` 的"字数不足 → 整章重写"互补：那是为了字数不达标。本文是为了风格退化（字数够、但不可读）。两种场景都需要 **重写整块** 而不是逐行 patch。
- 与 `write_file-stream-timeout-2026-07-08.md` 互补：那里的工具调用被服务端 rejecting（随 错误消息），失败可见；这里工具调用成功、文件正常落盘，只在内容质量上坍塌——需要"人读 + 风格扫锚"而不是错误状态才可发现。
