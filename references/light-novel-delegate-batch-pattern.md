# 轻小说批量生成：delegate_task 并发模式

2026-07-08 实战 40+ 本批量生成经验。`batch_generate.py` 只支持漫画项目（mode A/B/C）；轻小说批量必须用 `delegate_task` 直接驱动。

## 并发节奏

| 参数 | 值 |
|------|-----|
| 每批任务数 | 3（受 `max_concurrent_children` 限制）|
| 启动节奏 | 前一批 dispatch 后立即启动下一批，不等待 |
| 每本书交付 | 6 个文件：chars/summary/foreshadowing + 3 章正文 |
| 每章目标 | 纯 CJK ≥2600（留钩子段缓冲），body-only ≥2500 |

## Subagent context 必须包含

```text
要求:
- chars.md≥N个角色
- summary.md全书设定
- foreshadowing.md前N章伏笔
- 3章正文各≥2500中文字符
- UTF-8,禁止漫画字段,段落80-180字,对白「」——角色名
- 每章≥3个<!-- ILLUST_N -->, 有## 章末钩子
- 用Python写入文件,中文
- 文件名必须是 ln001_xxx.md ln002_xxx.md ln003_xxx.md, 在 light_novel/ 目录下
```

## 关键陷阱：子 agent 找不到文件（2026-07-20 实测）

**问题**：向子 agent 委托「读取 ln009_第九章.md 并生成分镜脚本」时，子 agent 因文件路径模糊（只有文件名不带绝对路径）而搜索失败，返回空结果。

**根因**：子 agent 的搜索范围受限，`search_files(pattern='ln009*')` 可能跨目录搜索但返回空，agent 无法推断项目根目录。

**修复**：在 context 中**显式给出绝对路径**：

```text
# ❌ 会失败（路径模糊）
target: 读取 ln009_第九章.md 并生成脚本

# ✅ 成功（绝对路径）
target: 读取 /root/comic-projects/projects/深夜电台主持人/light_novel/ln009_第九章.md 并生成脚本
```

**规则**：
- 涉及文件读取的 delegate_task，context 中必须包含**绝对路径**
- 输出目录同理：`写入 /root/comic-projects/projects/深夜电台主持人/scripts/sd009_EP*.md`
- 不要假设子 agent 知道 `COMIC_PROJECTS_ROOT` 环境变量
- 如果源文件路径含中文，子 agent 的 `read_file` 工具能正确处理，无需 encode

## 交付后规范化

Subagent 可能把章节写成各种格式乱放，必须统一处理：

```python
from pathlib import Path
base = Path(os.environ.get('COMIC_PROJECTS_ROOT', os.path.expanduser('~/comic-projects/projects')))
for pdir in base.iterdir():
    lndir = pdir / 'light_novel'
    if not lndir.exists(): continue
    # 把 chapter*.md / 第*.md / chapters/*.md 复制到 light_novel/
    for src in pdir.rglob('*.md'):
        if 'light_novel' in str(src) or src.name in {'config.json','summary.md','characters.md','foreshadowing.md','style_guide.md'}:
            continue
        if not any(x in src.stem for x in ['chapter','第','ln']):
            continue
        if src.parent == lndir and src.name.startswith('ln'): continue
        dst = lndir / f"ln{idx:03d}_{src.stem}.md"
        shutil.copy2(src, dst)
```

规范化后检查：

```bash
ls projects/*/light_novel/*.md | wc -l                          # 总章数
for d in projects/*/; do echo "$d $(ls "$d/light_novel"/*.md 2>/dev/null | wc -l)"; done  # 每本章数
```

## 失败恢复

常见的 Cloudflare HTTP 522 中断，不影响已写入的文件。重新 dispatch 失败的 subagent 即可恢复。如果同一个项目同时收到新 batch 的 dispatch 和旧 batch 的 522 结果，以新 batch 为准，旧结果直接忽略。

## 命名去重

注意不要重复定义相同设定的项目。2026-07-08 已出现的重复：
- `DemoProjectD`（新 20 本）vs `DemoProjectD`（前 20 本，已有 5 章）——相同设定 `旧书店收到一本会归还未完故事的无名书`。新项目生成时自动跳过，保留旧项目。