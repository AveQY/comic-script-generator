# 全脚本单次落盘模式与三口径验字（2026-07-08）

## 背景

第三次单批项目（《星际邮差》，2026-07-08 晚间）暴露了一个比 `light-novel-single-batch-generation-2026-07-08.md` 模式一更高效的落盘方式：**把元数据 + 全部章节正文塞进同一个 Python 脚本，用 `write_file` 写入该脚本，再用一次 `terminal` 执行**。全程只需 2 个工具调用（write_file + terminal），而非此前"1 脚本 + N 次 write_file"的 1+N 模式。

## 模式三：全脚本单次落盘

### 与此前两种模式的关系

| 模式 | 调用次数 | 适用场景 | 风险 |
|------|---------|---------|------|
| 模式一（single-batch ref） | 1 脚本 + N×write_file | 元数据互引、正文逐章独立 | 正文参数膨胀 |
| **模式三（本文档）** | **1 write_file(脚本) + 1 terminal** | **≤6 文件、总内容 <50KB** | **脚本超限、全有或全无** |
| 模式二（batch ref §4） | 短脚本读写现有文件 | 批量扩写/修复 | 不适用于首次生成 |

### 操作步骤

1. **用 `write_file` 写一个 Python 脚本**（如 `generate.py`），脚本内将每个文件的完整内容定义为 Python 字符串变量（`"""..."""`），然后用 `open().write()` 逐个写入目标路径。脚本末尾附内联验证段（打印每文件字数/插图数/钩子存在性）。
2. **用一次 `terminal` 执行** `python3 generate.py`，输出会包含每文件的写入确认 + 验证摘要。
3. **读 terminal 输出即可完成全部验收**，无需额外调用 `validate_light_novel.py`（除非用户明确要求跑权威脚本）。

### 适用边界与风险

- **上限**：单脚本 ≤50KB（`write_file` 已验证 48-50KB 稳定）。本次《星际邮差》脚本 50.8KB、6 文件（3 元数据 + 3 章节），一次成功。
- **超限信号**：如果 `write_file` 因 timeout 失败，说明总内容过大——降级为模式一（拆分元数据脚本 + 逐章 write_file）或分批写脚本文件。
- **全有或全无**：脚本执行失败则全部文件都不会写入（因为是一次性执行）——这是模式三相对模式一的劣势。模式一的部分成功（如元数据已写入但某章失败）在模式三中不会发生，但也意味着模式三失败时需要整体重跑。权衡：≤6 文件时模式三更简洁，>6 文件或单章 >10KB 时模式一更安全。

### 脚本结构模板

```python
# -*- coding: utf-8 -*-
import os

BASE = os.environ.get("COMIC_PROJECTS_ROOT", os.path.expanduser("~/comic-projects/projects")) + "/<书名>"
LN_DIR = os.path.join(BASE, "light_novel")
os.makedirs(LN_DIR, exist_ok=True)

# ========== characters.md ==========
characters = """# 角色档案
...（完整内容）...
"""

# ========== summary.md ==========
summary = """..."""

# ========== foreshadowing.md ==========
foreshadowing = """..."""

# ========== Chapter 1 ==========
chapter1 = """# 第一章　章名

正文段落...

「台词。」——角色名

<!-- ILLUST_1 -->

正文段落...

## 章末钩子
钩子内容
"""

# ... more chapters ...

# Write all files
files = {
    "characters.md": characters,
    "summary.md": summary,
    "foreshadowing.md": foreshadowing,
    os.path.join("light_novel", "ln001_第一章.md"): chapter1,
    # ...
}

for relpath, content in files.items():
    fullpath = os.path.join(BASE, relpath)
    os.makedirs(os.path.dirname(fullpath), exist_ok=True)
    with open(fullpath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"WROTE: {fullpath} ({len(content)} chars)")

# Inline verification
print("\n=== VERIFICATION ===")
for relpath in files:
    fullpath = os.path.join(BASE, relpath)
    with open(fullpath, "r", encoding="utf-8") as f:
        text = f.read()
    cn_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    illust_count = text.count("<!-- ILLUST_")
    has_hook = "## 章末钩子" in text
    print(f"{relpath}: total={len(text)}, cn_chars={cn_chars}, illust={illust_count}, hook={has_hook}")
```

### 验证段验证项

脚本末尾的内联验证应覆盖（与 SKILL.md 模式六要求对齐）：

| 验证项 | 校验方式 | 合格标准 |
|--------|---------|---------|
| 中文字数 | `sum(1 for c in text if '\u4e00' <= c <= '\u9fff')` | ≥2500（纯 CJK 口径） |
| 插图标记 | `text.count("<!-- ILLUST_")` | ≥3 |
| 章末钩子 | `"## 章末钩子" in text` | True |
| 对白格式 | `len(re.findall(r'^「.+?」——.+$', text, re.M))` | ≥8（对应 `validate_light_novel.py` 正则） |
| 漫画字段污染 | 扫描 `**格子**`/`### Panel`/`## Page`/`| 字段 |` | 0 处 |

注：本次实测三章纯 CJK 字数分别为 2721 / 2946 / 3023，全部 ≥2500 一次过，无需补足。插图标记 4/3/3 个，章末钩子全部存在。

## 三口径验字表（本次实测）

| 章 | 纯 CJK 汉字 | 总字符(含标点) | 插图 | 钩子 |
|----|------------|--------------|------|------|
| 第一章 | 2721 | 3241 | 4 | ✓ |
| 第二章 | 2946 | 3567 | 3 | ✓ |
| 第三章 | 3023 | 3673 | 3 | ✓ |

三口径差距约 520-650 字/章，与 `light-novel-batch-generation-lessons-2026-07-07.md` §3 记录的 200-400 字差距方向一致但差距更大——本次章节含更多对白标记和插图占位符（`<!-- ILLUST_N -->`），拉高了"总字符"口径。**结论不变：以纯 CJK ≥2600 为安全目标**。

## 网络中断恢复

本次会话经历过两次网络中断（mid-stream cut-off），恢复时系统提示"Continue exactly where you left off"。在模式三下，恢复方式简单：直接继续调用 `write_file` 写入 generate.py 脚本（因为脚本是一次性单元）。但需注意：

- **不要在中断后重新执行已完成的步骤**——如果 `write_file` 已成功写入脚本文件，中断恢复时直接跳到 `terminal` 执行步骤。
- **如果不确定脚本是否已写入**，用 `read_file` 读一次脚本文件确认内容完整，再执行。避免损坏文件被执行后写入乱码正文。

## 模式四：逐章生成器脚本（2026-07-08《深夜便利店》第4-6章实测）

### 何时用

当需要批量续写多章（9+ 章），且会话可能遭遇网络中断时，模式三的"一个脚本写全部文件"反而脆弱——脚本太大 `write_file` 容易超时，且网络恢复后要整体重写。模式四用**每章一个独立 `.py` 生成器脚本**，逐章 `write_file` + `terminal` 执行。

### 操作步骤

1. 为每章写一个 `gen_chN.py`，脚本内只包含该章正文字符串、`open().write()` 写入 `light_novel/lnXXX_第N章.md`、末尾附本章内联验证段（CJK/对白/插图/钩子/污染五项——见 SKILL.md note 14五项 SOP）。
2. `write_file` 写脚本 → `terminal` 执行 → 读输出验收。
3. 若某章 CJK 不足 2600，用 `patch` 做**主题锚点**段级增量补足（见 SKILL.md note 14「主题锚点」技巧——在已有自然情感转折点前后插入主题延续段），补后重跑验证命令确认达标。
4. 网络中断恢复后，先用 `search_files` 确认已落盘的章节文件列表，跳过已完成的章节，从断点继续。

### 与模式三的对比

| 维度 | 模式三（全脚本） | 模式四（逐章脚本） |
|------|----------------|------------------|
| 调用次数 | 2（1 write_file + 1 terminal） | 2N（N 章 × 2） |
| 适用场景 | ≤6 文件、总内容 <50KB | N 章、网络不稳定、需逐章验收 |
| 中断恢复 | 需整体重写大脚本 | 跳过已完成章节，从断点继续 |
| 字数补足 | 整批补时需改大脚本 | 单章 `patch` 即可，互不干扰 |
| 脚本大小 | 48-50KB 易超限 | 每脚本 ~10KB，永不超限 |

### 实测数据（《深夜便利店》第4-6章）

| 章 | 脚本大小 | 正文字符 | 纯CJK | 对白 | 插图 | 补足 |
|----|---------|---------|-------|------|------|------|
| 第四章 | 10KB | 3153 | 2639 | 10 | 3 | 无需 |
| 第五章 | 9.5KB | 3008 → 3180+ | 2416 → 2621 | 19 | 3 | patch 1段 |
| 第六章 | 11KB | 3564 | 2942 | 12 | 3 | 无需 |

第五章首稿 CJK=2416（低于 2600），用 `patch` 在苏念离场段后补入一段环境+心理描写（湿气、青苔味、咖啡豆香、林晚意识到自己站在谜面正中央），补后 2621 一次过。**注意**：`patch` 补段后应立即重跑五项自检命令确认 CJK达标，不可凭"补了就行"结束。

### 优点

- **中断韧性**：每章独立，断在哪补哪，不丢已写文件
- **逐章验收**：每章 `terminal` 输出立即显示 CJK/对白/插图/钩子/污染，当章不达标当章修
- **脚本不超限**：单章脚本 9-12KB，远低于 `write_file` 48KB 稳定上限
- **补足隔离**：单章 `patch` 不影响其他已写章节，避免连环污染

### 缺点

- **工具调用次数翻倍（2N vs 2）**，大量章节时更耗轮次
- **可能撞上工具调用迭代上限**——这是比"耗时"更硬的约束（2026-07-09 实测，见下文「工具调用预算与模式选择」）
- 每个脚本有重复的脚手架代码（import/os.makedirs/验证段），略冗余

### 脚本模板

```python
# -*- coding: utf-8 -*-
import os, re

BASE = os.environ.get("COMIC_PROJECTS_ROOT", os.path.expanduser("~/comic-projects/projects")) + "/<书名>"
LN_DIR = os.path.join(BASE, "light_novel")
os.makedirs(LN_DIR, exist_ok=True)

chapter = """# 第N章：章名

---

正文段落...

「台词。」——角色名

<!-- ILLUST_1 -->

正文段落...

## 章末钩子
钩子内容
"""

with open(os.path.join(LN_DIR, "lnNNN_第N章.md"), "w", encoding="utf-8") as f:
    f.write(chapter)
print(f"WROTE lnNNN ({len(chapter)} chars)")

# Inline verification（五项自检，覆盖 SKILL.md note 14 SOP）
with open(os.path.join(LN_DIR, "lnNNN_第N章.md"), "r", encoding="utf-8") as f:
    t = f.read()
cjk = sum(1 for c in t if '\u4e00' <= c <= '\u9fff')
fmt = len(re.findall(r'^「.+?」——.+$', t, re.M))
illust = t.count('<!-- ILLUST_')
hook = '## 章末钩子' in t
pollution = bool(re.search(r'\*\*格子\*\*|### Panel|## Page|^\|.*\|.*\|', t, re.M))
print(f"lnNNN: CJK={cjk}, 对白={fmt}, 插图={illust}, 钩子={hook}, 污染={pollution}")
```

## 与 heredoc 禁令的关系

模式三和模式四都用 `write_file` 写 **Python 脚本身**，脚本内容是 Python 字符串字面量（`"""..."""`），而非 Shell heredoc。因此不违反 SKILL.md 中"禁止 Shell heredoc 写入正文"的规则。正文是从 Python 字符串变量写入文件的，绕开了 heredoc 定界层。**如果脚本太大导致 `write_file` 也失败**，降级方案是：把脚本拆成多个 `.py` 文件分别 `write_file`，分别执行（即模式四），而不是改用 heredoc。

## 工具调用预算与模式选择（2026-07-09 实测，强制）

### 背景

本次《DemoProjectD》续写第6-14章（共9章）实测暴露了一个比"耗时"更硬的约束：**会话有工具调用迭代上限**。逐章 `write_file` 直接写正文（非模式四的脚本路线，而是 main-session 直接 `write_file` 每章正文 + 逐章 terminal 自检 + 逐章 patch 补字数/修污染）消耗了全部预算，仅完成4章（ln006-009）即被截断。

### 单章实际调用开销

| 步骤 | 调用数 |
|------|--------|
| 1× `write_file`（整章正文） | 1 |
| 1× `terminal`（五项自检 Python） | 1 |
| 1-3× `patch`（修 Cyrillic/英文/伪标记/转义引号等污染） | 1-3 |
| 0-1× `patch`（主题锚点补字数到 ≥2500 CJK） | 0-1 |
| 1× `terminal`（补后重新自检）或1× `validate_light_novel.py` | 0-1 |
| **单章合计** | **3-7 调用/章** |

9章 × 3-7调用 = **27-63 次工具调用**，远超单轮工具调用上限。ln006实测6调用、ln007实测5调用、ln008实测8调用（污染多）、ln009实测6调用——已用约25调用完成4章。

### 模式选择规则（当 N≥6 章时强制评估）

| 章节数 | 推荐模式 | 理由 |
|--------|---------|------|
| ≤3章 | 逐章 `write_file` + 自检 | 调用开销可控，逐章验收精度高 |
| 4-5章 | 逐章 `write_file` 或模式三 | 临界——若每章污染风险高则逐章，若干净则模式三更省 |
| **6-8章** | **模式三（单脚本全落盘）** | 2调用覆盖全部章节+元数据，留足预算给后续验证和补修 |
| **9+章** | **模式三分批（每批≤6文件）** 或 **模式四（逐章脚本）** | 模式三单脚本超50KB风险高；模式四2N调用但可中断恢复 |

### 关键洞察

1. **"逐章 `write_file`"不是免费午餐**：虽然 `write_file` 单次稳定（48KB验证），但每章后续的"自检→patch→重自检"循环平均3-5次额外调用，让单章真实开销远超"1次write_file"。此前文档只强调 write_file 的单次稳定性，未提累积调用预算。
2. **模式三的2调用优势在 N≥6 时决定性**：即使后续需要 patch 修污染（假设50%章节有1处污染 = 3×patch + 3×terminal重检 = 6调用），总开销仍远低于逐章write_file的27-63调用。
3. **污染多寡应在模式选择前预判**：若项目角色名复杂、中英文混生成场景多（如本作闻砚/闻小满/陈嘉多人名混排），污染概率高 → 模式三的"一次性2调用 + 事后批量patch"比逐章write_file的"每章即时patch"更省预算，因为 patch 无需配套 write_file。
4. **本会话正是该选模式三而误选逐章write_file的案例**：9章正文若用模式三，2调用写脚本 + 1调用执行 + 6-9调用批量patch修污染 + 1调用validate = 约12调用，可在预算内完成全部9章。实际走了逐章路线，25调用仅完成4章后被截断。

### 第二批实测数据（《DemoProjectD》第4-12章续写，2026-07-09，强制补录）

《DemoProjectD》9章续写（ln004–ln012）二次实测完全验证上述模式选择规则：

| 章号 | write_file | terminal 自检 | patch 修污染 | patch 补字数 | 合计调用 | CJK(body)终值 | 备注 |
|------|-----------|-------------|------------|------------|---------|--------------|------|
| ln004 | 2（首稿对白0+整章重写） | 2 | 0 | 0 | 4 | 2751 | 零计数陷阱→整章重写一次过 |
| ln005 | 1 | 2 | 1（修"omer"漏字+patch引起重复段→二次patch删重复）| 2 | 7 | 2715 | patch 引入一轮邻段重复，需二次patch清理 |
| ln006 | 2（首稿太短对白2+重写） | 2 | 2（"good"×4、"groundwater"、"đêm"逐条修）| 1 | 7 | 2722 | 四处英文token+一处拉丁扩展字符，本session最多 |
| ln007 | 1 | 2 | 2（"features"、"Lin"各一） | 2 | 7 | 2704 | 含一次patch在 new_string 中又意外注入"Lin"，需补修 |
| ln008 | 1 | 2 | 0 | 2 | 5 | 2548（未补到2600） | 差52字未补齐即被迭代上限截断 |
| ln009–ln012 | — | — | — | — | — | — | 未创建，被工具迭代上限截断 |
| **合计** | 7 | 10 | 5 | 7 | **30次调用** | **完成5/9章** |

实测与第一批数据完全吻合：5章共消耗30次调用（平均6次/章），与首批《深夜便利店》4章25调用（6.25/章）几乎一致。两批不同项目、不同时间、不同模型，均验证"逐章write_file → 平均6调用/章 → N章需6N调用 → N≥6时必撞迭代上限"。

### patch new_string 与 write_file 的 token 幻觉高发对比（2026-07-09 实测新增，引用）

**反直觉发现**：本session 4/5章存在英文token泄露，但泄露源**主要不在 write_file 本身**，而是在 `patch` 的 `new_string` 参数中构造新一段中文长文本时。具体频次：

| 项目 | 首次 write_file 正文中混入英文token | patch new_string 中混入英文token |
|------|------------------------------|-------------------------------|
| ln005 | 1处（"omer"）| 0 |
| ln006 | 3处（"good"×4、"groundwater"、"đêm"）| 0 |
| ln007 | 0 | 2处（增补段落里混入"features"、"Lin"）|
| ln008 | 1处（"堂."误用西文句点）| 0 |

**底层机理**：`patch` 的 `new_string` 通常需要"复制旧句+增补一段同主题新段"，LLM 在此过程中容易因记忆中残留的邻近 script 或代码段误切到拉丁字符 token。**关键信号**：`patch` 的 old_string 通常是干净中文（因为源自已写文件），但 new_string 属于新生成，因此污染检测必须在**每次 patch 应用后立即重跑**五项自检——不能假设 write_file 后干净则 patch 后也干净。

**对应策略**：
- write_file 首稿污染检测：在 `terminal` 自检命令里追加 `[a-zA-Z]{3,}` 扫描（SKILL.md note 14 已含）
- patch 后污染检测：**第二次** terminal 自检命令——不是"在原命令上追加"，而是每次 patch 后重新跑同一组五项自检
- 高频污染的做法：同一段对两次 patch（一次修污染+一次重新跑自检）较高效，而非合并多段一次补改（合并易引入新污染）

### 零计数对白陷阱——首稿全叙述式归因的频次数据（2026-07-09 实测补录）

本session 5章节，首稿对白为 0 的占 2/5（40%）——ln004 首稿全部叙述式归因（"沈默摇了摇头。"式）、ln006 首稿全叙述式，`re.findall(r'^「.+?」——.+$', t, re.M)` 计数皆为 0。这进一步证实 SKILL.md note 5「写作时最常犯的错误」段将"叙述式归因与 `——角色名` 格式混用甚至只用前者"列为首稿头号风险是正确的，且频率不可忽略——两个不同写法倾向的 LLM 实例在同一session均有该问题。

**结论**：批量生成时应默认假设每两章首稿会出现一次零计数陷阱，提前规划"整章重写一次过"为兜底方案，而非期望逐条 patch 补回 `——角色名` 并分行拆叙述句（实测沿此路径往往更慢且更易引入错位/重复段）。

### 预判检查清单

批量续写前（≥6章），先快速评估：
- [ ] 总章数是否≥6？是→强制评估模式三/四
- [ ] 项目是否多角色复杂人名（>3个）？是→污染概率高→优先模式三（批量patch比逐章即时patch省调用）
- [ ] 是否需逐章验收且章节独立性强？是→模式四（2N但中断韧性好）
- [ ] 单脚本预估是否>50KB？是→模式三分批或模式四
- [ ] 会话是否已有工具调用消耗？是→剩余预算可能不足以逐章路线，降级到模式三
