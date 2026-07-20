# Long Novel Production + Reader Lessons (2026-07-07)

Session lessons from upgrading `comic-script-generator` from short light-novel samples to long-form web-novel production.

## User correction to preserve

The user explicitly corrected the workflow: a real novel should not be treated like a 3-chapter sample. For “完整小说 / 生成一篇小说”, assume a long-form target around **200k Chinese characters** unless the user says it is only a short test.

## Required production shape

For formal novel projects:

- Target length: **>= 200,000 Chinese characters**.
- Recommended structures:
  - 40–60 chapters × 4,000–6,000 chars, or
  - 80–100 chapters × 2,500–3,500 chars.
- Short 3-chapter projects are only “短测”; mark them explicitly with `test_project: true` and never report them as complete long novels.
- Store in `config.json`:
  - `content_mode: light_novel`
  - `script_unit: light_novel`
  - `density_mode: LN`
  - `category: <channel>`
  - `target_total_chars: 200000`
  - `planned_chapters: <N>`
  - `generation_status: in_progress|completed`

## Context compression workflow

Do not load all chapter files for a long novel. Generate in batches:

1. Generate 3–5 chapters.
2. Run:
   ```bash
   python scripts/update_long_novel_context.py projects/<小说名>
   ```
3. Continue the next batch using only:
   - `summary.md`
   - `characters.md`
   - `foreshadowing.md`
   - `long_novel_context/running_summary.md`
   - `long_novel_context/recent_continuity.md`
   - `long_novel_context/character_state.md`
   - `long_novel_context/open_threads.md`
4. Read full chapter text only when repairing that specific chapter.

This prevents context blowups when approaching 200k+ characters.

## Validation lessons

Use `validate_light_novel.py` for per-chapter quality and `validate_long_novel.py` for complete long-form acceptance.

Useful commands:

```bash
python scripts/validate_light_novel.py projects/<小说名> --min-chars 2500 --min-dialogues 8
python scripts/validate_long_novel.py projects/<小说名> --target-chars 200000 --min-chapters 40
```

The validator counts non-whitespace characters, so generated chapters that appear long visually may still fail. In this session, chapters around 1,500 chars failed; expanded chapters around 3,175–3,249 chars passed the short-batch validator.

## Reader / frontend lessons

The user wants a novel-first front end:

- Enter via a homepage, not directly into one project detail screen.
- Show category navigation and a bookshelf of novels.
- Book cards should display novel title, category, chapter count, and tags.
- Clicking a book opens the novel chapter list/reader.
- Keep manga mode available, but novel mode is the default for novel projects.

When editing the single-file Reader frontend, always extract and syntax-check the `<script>` block before declaring the UI fixed:

```bash
python3 - <<'PY'
from pathlib import Path
import re
html = Path('/path/to/comic-script-generator-api/reader.html').read_text(encoding='utf-8')
m = re.search(r'<script>([\s\S]*)</script>', html)
Path('/tmp/reader_script.js').write_text(m.group(1), encoding='utf-8')
PY
node --check /tmp/reader_script.js
```

A single extra `}` previously caused the UI to remain stuck on “加载中”.

## Tool-use pitfall

Avoid huge `write_file`, `execute_code`, or `terminal` payloads when generating/updating long text. Use small scripts that read existing files and transform them locally, or patch smaller chunks. Large tool arguments may time out before delivery.
