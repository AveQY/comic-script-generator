# 文件写入与兜底生成实战经验（2026-07-06）

## 场景

为「DemoProjectA」项目生成第3集《大扫除战争》脚本（10页 / 54 Panel / 48KB Markdown）。

## 工具选择教训

### 1. Shell heredoc 不可用于漫画脚本写入

**问题**：先用 `write_file` 写入 Pages 1-5（24335 字节）成功，然后尝试用 `cat >> << 'EOF'` 追加 Pages 6-10。结果：Pages 1-5 内容被无声抹除，文件从 24335 字节缩至 23696 字节，仅剩 Pages 6-10。

**根因**：脚本内容包含：
- 反引号（AI 提示词的 fenced code block）
- 中文标点（全角冒号、引号、破折号、问号）
- Markdown 粗体标记（`**`）
- 日语拟声词（`バサッ`、`ピキ` 等包含全角字符）
- 表格竖线 `|`

Shell heredoc 在处理这些混合字符时可能在某些 shell 环境中无声截断，且无任何错误提示。

**结论**：**禁止使用 Shell heredoc 写入漫画脚本文件**。始终使用 Python `open().write()` 或直接 `write_file` 工具。

### 2. `write_file` 实际能力 > 文档所述

skill 文档中此前写 `write_file` 超 5000 字符可能超时失败，但本次实测：
- `write_file` 写入 48KB / 723 行 / 纯中文 Markdown 一次性成功，无超时无截断

**更新建议**：优先尝试 `write_file`，失败时降级到 Python 写入，而非反过来。

### 3. 追加写入可能引入内容重复/错位

**问题**：将脚本分成 3 批写入时，首批用 `write_file`（'w' 模式），第二、三批用 `terminal` 内嵌 Python `open(path, 'a')` 追加。结果文件出现严重内容重复/错位：

- `---## Page 3` 头尾标识连在一起缺少换行
- Panel 内容章节被重复插入（如 Page 4-7 的 Panel 出现两次）
- 最终文件 1965 行 / 76KB，其中约 660 行为无用的重复内容
- `grep -c "^### Panel"` 返回 74（预期 50），因为重复内容和代码块内的"Panel"都被计入

**根因分析**：
- 可能原因 1：`write_file` 写入首批后，Hermes 的 sibling subagent 机制导致文件状态不同步，`write_file` 返回了 `"modified by sibling subagent 'sa-1-...'"` 警告
- 可能原因 2：文件写入后到下次 `'a'` 追加之间，底层文件系统缓存或并发写入导致内容重叠
- 最可能原因：首批 `write_file` 的最终内容与预期不完全一致（多出了某些尾部内容），追加时与其叠加

**预防措施**：
- 写入首批后立即用 `wc -l -c` 和 `grep -c "^### Panel"` 验证文件基线与预期一致
- **不推荐分批追加**：如果能一次写完 50 Panel / 10 Pages（53KB），优先单次写入
- 如果必须分批，每批写完后都验证页面结构完整性，不要等到全部写完再检查
- 使用 `grep "^## Page"` 验证 Page 数，`grep "^### Panel"` 验证 Panel 数

### 4. 追加写入内容被污染后的修复方案

如果追加写入后出现内容重复/错位，可按以下模式修复：

```python
# 1. 先读取完整文件，找到 3 个干净段落的起止行号
# 2. 用 Python 提取干净段并重新写入

with open("corrupted.md", "r") as f:
    lines = f.readlines()

# lines 是 0-indexed，假设：
#   干净段 A: lines[0:527]   （Pages 1-4）
#   干净段 B: lines[798:1181] （Pages 5-7）
#   干净段 C: lines[1570:]    （Pages 8-10 + hooks）
clean = lines[0:527] + lines[798:1181] + lines[1570:]

with open("fixed.md", "w") as f:
    f.writelines(clean)
```

修复后必须验证：
```bash
grep "^## Page" fixed.md       # 预期 10 行
grep "^### Panel" fixed.md     # 预期 50 行
grep "^## 本集结尾钩子" fixed.md  # 预期 1 行
grep "^## 下集提示" fixed.md      # 预期 1 行
wc -l -c fixed.md               # 行数和字节数合理
```

### 5. 验证命令的选择

在包含 fenced code block 的文件中，搜索 Panel 数要使用行首匹配：

```bash
# ✅ 正确：只匹配行首的 ### Panel（排除 AI 提示词代码块内的"panels"）
grep "^### Panel" file.md | wc -l

# ❌ 错误：会匹配到代码块中描述文字里的"Panel"
grep -c "### Panel" file.md
```

同理搜索 Page：
```bash
grep "^## Page" file.md        # ✅
grep -c "## Page" file.md      # ❌ 会匹配到大纲、注释等
```

## 格式变体：Markdown 表格 vs 多行字段

本集使用了与 skill 标准模板不同的格式：**Markdown 表格** 将每个 Panel 的 8 个字段（格子/画面/构图/气泡/旁白/拟声/转场/AI提示词）放在一行内，而不是 skill 标准的多行独立字段。

```markdown
### Panel 1-1
| 字段 | 内容 |
|------|------|
| 格子 | 全页跨页大格子（1/1） |
| 画面 | 客厅全景，清晨阳光透过半拉开的窗帘洒进来... |
| 构图 | 从阳台门方向俯视整个客厅，呈三角形构图... |
| 气泡 | 无对话 |
| 旁白 | 「周日早晨十点——DemoProjectA的常规瘫痪状态。」 |
| 拟声 | 无 |
| 转场 | 淡入 |
| AI提示词 | masterpiece, best quality, modern manga style, bold lines, screentone, dynamic angles, sharp details, anime aesthetic, messy living room morning sunlight... |
```

**注意**：此格式可读性高，但 `validate_episode.py` 的 AI 提示词正则按 `\\`\\`\\`text` fenced code block 解析，表格格式中的 AI 提示词行不会被正确识别。如果后续需要运行验证脚本，必须转换为 fenced code block 格式或修改验证脚本。

## AI 提示词格式

本集使用的固定正向/反向提示词格式：

**正向**：`masterpiece, best quality, modern manga style, bold lines, screentone, dynamic angles, sharp details, anime aesthetic, [场景描述], [构图], [光线]`

**反向**：`worst quality, low quality, blurry, deformed, bad anatomy, extra limbs, watermark, text, signature`

与 skill 标准模板的区别：
- 正向词中未包含 `no text/no letters/leave empty space for speech bubbles`（这些用于生图阶段）
- 反向词中包含 `watermark, text, signature` 防止生图模型添加文字水印
- 风格词统一为 `modern manga style, bold lines, screentone, dynamic angles, sharp details, anime aesthetic`

## 缺少的流程步骤

本集生成过程跳过了 `comic-script-generator` 的以下标准步骤：

1. **未初始化项目骨架**：没有运行 `init_project.py`，没有创建 `style_guide.md` / `config.json` / `characters.md` / `foreshadowing.md`
2. **未加载 skill**：`comic-script-generator` 在可用技能列表中，但未在生成前通过 `skill_view()` 加载
3. **未运行验证脚本**：没有运行 `validate_episode.py` / `update_project.py` / `consistency_check.py`
4. **未创建角色档案**：三个角色（林默、苏然、王乐乐）的信息仅在稿子头部列出，未写入 `characters.md`
5. **未设置风格指南**：AI 提示词风格由用户直接指定，而非从 `style_guide.md` 读取

**教训**：当 `comic-script-generator` 技能可用时，即使项目已存在，也应先加载 skill 并按流程操作，否则会丢失项目结构收益（角色档案、伏笔追踪、验证脚本等）。

## 项目上下文

- 项目路径：`/path/to/comic-projects/projects/DemoProjectA/`
- 第3集文件：`episodes/ep003_大扫除战争.md`
- 角色：林默（23岁男·自由插画师·邋遢随性）/ 苏然（26岁女·行政主管·洁癖强迫症·嘴硬心软）/ 王乐乐（19岁女·大一新生·乐天派吃货）
- 集数：10页 / 54 Panel / 约 300 段对话 / 约 50 个 AI 提示词
- 结尾钩子：苏然约饭 + 林默暗说「还挺可爱的」
- 下集提示：林默接到医院电话，苏然发现纸条