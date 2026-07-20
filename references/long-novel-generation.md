# Long-novel generation lessons — 2026-07-07

## Trigger
Use these notes whenever the user asks for “完整小说 / 长篇小说 / 20万字小说 / 批量小说项目” in `comic-script-generator` mode six.

## What went wrong in this session
A batch generator produced 40 chapters × 10 projects and then padded each book to 20万字 with repeated structural paragraphs. It passed early length-only validation but failed user review because chapters repeated the same beats and paragraphs.

This is a durable workflow lesson: **word-count compliance is not story compliance**.

## Required long-novel workflow
1. **Do not one-shot template 40 chapters.** Generate in batches of 3–5 chapters.
2. **Each chapter needs a unique beat sheet before prose:** opening hook, scene goal, conflict, new information, relationship movement, chapter-end hook.
3. **After every batch, run context compression:**
   ```bash
   python scripts/update_long_novel_context.py projects/<小说名>
   ```
4. **Next batch reads compressed context only:** `summary.md`, `characters.md`, `foreshadowing.md`, and `long_novel_context/{running_summary.md,recent_continuity.md,character_state.md,open_threads.md}`.
5. **Do not load the full manuscript for continuation.** Only read a full chapter when repairing that specific chapter.
6. **Do not claim a long novel is complete** unless `validate_long_novel.py --target-chars 200000 --min-chapters 40` passes *and* the prose quality validator passes.

## Quality gates beyond word count
Run:
```bash
python scripts/validate_light_novel.py projects/<小说名> \
  --min-chars 2500 \
  --min-dialogues 8 \
  --max-duplicate-rate 0.18 \
  --max-adjacent-similarity 0.82
```

This catches:
- template phrases such as `第1段里` / `【长篇深化段落】`
- repeated or near-repeated paragraphs inside a chapter
- adjacent chapters with overly similar text
- comic fields leaking into novel prose

Then run the long-novel acceptance check:
```bash
python scripts/validate_long_novel.py projects/<小说名> --target-chars 200000 --min-chapters 40
```

## Artifact handling
- If a generated set fails repetition/similarity review, delete or quarantine it. Do not keep it in Reader as a finished novel.
- If only the first 3–5 chapters are generated, mark `config.json` with:
  - `generation_status: in_progress`
  - `target_total_chars: 200000`
  - `planned_chapters: 40` (or higher)
- Reader can show in-progress works, but final replies must clearly call them “第一批/连载中”, not “完整20万字小说”.

## User preference reinforced by this session
The user expects real readable novels, not formal artifacts that satisfy metrics. If they ask to execute, delete failed outputs and regenerate using the corrected pipeline rather than explaining only.

## Extra implementation notes from this session
- Update `validate_light_novel.py` before regenerating if it lacks repetition checks. Add detection for:
  - explicit template phrases (`第1段里`, `第2段里`, `【长篇深化段落】`, etc.)
  - exact duplicate paragraphs after punctuation/whitespace normalization
  - near-duplicate paragraphs using bounded `SequenceMatcher`
  - adjacent chapter similarity, default threshold around `0.82`
- Use small incremental patches/scripts for chapter repair. Large `write_file`, `execute_code`, or `terminal` payloads can time out; prefer reading existing chapters and appending targeted per-chapter prose in small chunks.
- A valid first batch may be only 5 chapters, but every chapter still must pass the prose validator. Report it as “第一批 5 章通过质量验证 / 长篇连载中”, not as a finished novel.
- For Reader cleanup, deleting all project directories except the one being regenerated is acceptable when the user explicitly says “旧项目清除，重新生成”. Verify `/projects` afterward.