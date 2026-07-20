#!/usr/bin/env python3
"""Validate long-form novel project length and compressed context readiness."""
import argparse, json, re
from pathlib import Path

def chars(p): return len(''.join(p.read_text(encoding='utf-8',errors='ignore').split()))
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('project_dir')
    ap.add_argument('--target-chars', type=int, default=200000)
    ap.add_argument('--min-chapter-chars', type=int, default=2500)
    ap.add_argument('--min-chapters', type=int, default=40)
    args=ap.parse_args()
    p=Path(args.project_dir); files=sorted((p/'light_novel').glob('ln*.md'))
    lens=[chars(f) for f in files]
    total=sum(lens)
    issues=[]
    if len(files)<args.min_chapters: issues.append(f'too few chapters: {len(files)} < {args.min_chapters}')
    if total<args.target_chars: issues.append(f'total chars too low: {total} < {args.target_chars}')
    bad=[(f.name,n) for f,n in zip(files,lens) if n<args.min_chapter_chars]
    if bad: issues.append(f'chapters below min chars: {bad[:10]}')
    ctx=p/'long_novel_context'
    for fn in ['chapter_index.json','running_summary.md','recent_continuity.md','character_state.md','open_threads.md']:
        if not (ctx/fn).exists(): issues.append('missing context file: '+fn)
    print(json.dumps({'passed':not issues,'chapters':len(files),'total_chars':total,'min_chars':min(lens) if lens else 0,'max_chars':max(lens) if lens else 0,'issues':issues},ensure_ascii=False,indent=2))
    raise SystemExit(0 if not issues else 1)
if __name__=='__main__': main()
