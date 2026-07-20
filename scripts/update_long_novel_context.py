#!/usr/bin/env python3
"""Update compressed long-novel context after chapters are written.

This script is intentionally heuristic and local: it extracts compact summaries,
recent continuity, character mentions, objects, and unresolved hook text so the
next generation batch does not need to load the full 200k-word manuscript.
"""
import argparse, json, re
from pathlib import Path
from datetime import datetime


def read(p): return p.read_text(encoding='utf-8', errors='ignore')
def write(p,s): p.parent.mkdir(parents=True, exist_ok=True); p.write_text(s, encoding='utf-8')
def compact(s,n=260):
    s=re.sub(r'<!--.*?-->', '', s, flags=re.S)
    s=re.sub(r'[#>*_`\-]+','',s)
    s=re.sub(r'\s+',' ',s).strip()
    return s[:n]

def chapter_num(p):
    m=re.search(r'(\d+)', p.stem)
    return int(m.group(1)) if m else 0

def dialogues(txt):
    return re.findall(r'^「(.+?)」——([^\n]+)$', txt, re.M)

def proper_names(txt):
    # Chinese 2-4 char names before dialogue marker or common action verbs
    names=set()
    for _,sp in dialogues(txt):
        sp=re.sub(r'[（(].*?[）)]','',sp).strip()
        if 1<len(sp)<=6: names.add(sp)
    return sorted(names)

def update(project):
    p=Path(project)
    ln=p/'light_novel'
    files=sorted(ln.glob('ln*.md'), key=chapter_num)
    ctx=p/'long_novel_context'
    ctx.mkdir(exist_ok=True)
    entries=[]
    character_mentions={}
    hooks=[]
    recent=[]
    total_chars=0
    for f in files:
        txt=read(f); total_chars += len(''.join(txt.split()))
        title=re.search(r'^#\s+(.+)',txt,re.M)
        title=title.group(1).strip() if title else f.stem
        h=re.search(r'##\s*章末钩子\s*(.*)$',txt,re.S)
        hook=compact(h.group(1),180) if h else compact('\n'.join(txt.splitlines()[-8:]),180)
        first=compact('\n'.join(txt.splitlines()[:28]),220)
        names=proper_names(txt)
        for n in names: character_mentions[n]=character_mentions.get(n,0)+1
        entries.append({'file':f.name,'title':title,'chars':len(''.join(txt.split())),'summary':first,'hook':hook,'characters':names})
        if hook: hooks.append(f'- {title}：{hook}')
        recent.append(f'## {title}\n- 摘要：{first}\n- 章末钩子：{hook}\n- 出场：{", ".join(names) or "未知"}')
    # Keep last 5 chapters as recent continuity
    recent=recent[-5:]
    write(ctx/'chapter_index.json', json.dumps({'updated_at':datetime.now().isoformat(),'total_chapters':len(files),'total_chars':total_chars,'chapters':entries},ensure_ascii=False,indent=2))
    write(ctx/'running_summary.md', '# 长篇压缩摘要\n\n'+'\n\n'.join([f"## {e['title']}\n- 字数：{e['chars']}\n- 摘要：{e['summary']}\n- 钩子：{e['hook']}" for e in entries]))
    write(ctx/'recent_continuity.md', '# 最近5章连续性上下文\n\n'+'\n\n'.join(recent))
    write(ctx/'character_state.md', '# 角色状态（自动提取）\n\n'+'\n'.join([f'- {k}：出现 {v} 章/次，续写时保持称呼、关系和说话风格一致。' for k,v in sorted(character_mentions.items(), key=lambda x:-x[1])]))
    write(ctx/'open_threads.md', '# 未回收伏笔/章末钩子\n\n'+'\n'.join(hooks[-30:]))
    print(json.dumps({'status':'ok','project':str(p),'chapters':len(files),'total_chars':total_chars,'context_dir':str(ctx)},ensure_ascii=False,indent=2))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('project_dir')
    args=ap.parse_args()
    update(args.project_dir)
if __name__=='__main__': main()
