#!/usr/bin/env python3
import argparse, os, re, json
FIELDS=["**格子**","**画面**","**构图**","**气泡**","**旁白**","**拟声**","**转场**","**AI 提示词"]
GENERIC_VISUAL_PATTERNS=[
    "普通日常场景", "异常事件突然出现", "主角靠近异常源", "关键配角登场",
    "世界观第一次展开", "规则第一次被验证", "主角做出第一次主动选择",
    "危机升级", "情感冲突爆发", "关键线索出现", "结尾钩子",
    "环境信息明确", "结合本作设定"
]

def read(p):
    with open(p,encoding='utf-8') as f: return f.read()

def panels(c):
    ms=list(re.finditer(r'^### Panel\s+(\d+)\b.*$',c,re.M))
    out=[]
    for i,m in enumerate(ms):
        out.append((int(m.group(1)), c[m.end(): ms[i+1].start() if i+1<len(ms) else len(c)]))
    return out

def count_pages(c): return len(re.findall(r'^## Page\s+\d+\b',c,re.M))
def count_scenes(c): return len(re.findall(r'^## Scene\s+\d+\b',c,re.M))

def style_issues(project, ep):
    issues=[]; gp=os.path.join(project,'style_guide.md')
    if not os.path.exists(gp): return ['Missing style_guide.md - run init_project.py']
    g=read(gp)
    pm=re.search(r'## 正向提示词\s*\n(.+?)(?:\n##|$)',g,re.S)
    nm=re.search(r'## 反向提示词\s*\n(.+?)(?:\n##|$)',g,re.S)
    if not pm or not nm: return ['style_guide.md format invalid - missing 正向/反向提示词 sections']
    terms=[x.strip() for x in pm.group(1).split(',')[:3] if x.strip()]
    miss=[]
    for no,b in panels(read(ep)):
        if terms and not any(t.lower() in b.lower() for t in terms): miss.append(no)
    if miss: issues.append('Panels missing style_guide prompt keywords: '+str(miss[:10]))
    return issues

def quality_issues(c):
    issues=[]
    pages=re.split(r'^## Page\s+\d+\b.*$',c,flags=re.M)[1:]
    for i,pg in enumerate(pages,1):
        n=len(re.findall(r'^### Panel\s+\d+\b',pg,re.M))
        if n>8: issues.append(f'Page {i} has {n} panels; may be too dense')
    comps=[]; empty=0
    for no,b in panels(c):
        vm=re.search(r'\*\*画面\*\*：\s*(.+?)(?:\n\*\*构图\*\*|\Z)',b,re.S)
        visual=vm.group(1).strip() if vm else ''
        for pat in GENERIC_VISUAL_PATTERNS:
            if pat in visual:
                issues.append(f'Panel {no} visual is too generic/template-like: {pat}')
        if len(visual) < 35:
            issues.append(f'Panel {no} visual too short to render reliably ({len(visual)} chars)')
        m=re.search(r'\*\*构图\*\*：\s*(.+)',b); comps.append(m.group(1).strip() if m else '')
        bm=re.search(r'\*\*气泡\*\*：(.+?)(?:\n\*\*|\Z)',b,re.S)
        if bm:
            for q in re.findall(r'["“](.*?)["”]',bm.group(1)):
                if len(q)>50: issues.append(f'Panel {no} bubble text too long ({len(q)} chars)')
        if re.search(r'\*\*气泡\*\*：\s*无',b) and re.search(r'\*\*旁白\*\*：\s*无',b) and re.search(r'\*\*拟声\*\*：\s*无',b):
            empty+=1
            if empty>=5: issues.append(f'Panels ending at {no} have 5 consecutive panels without bubble/caption/SFX'); empty=0
        else: empty=0
    for i in range(4,len(comps)):
        w=comps[i-4:i+1]
        if w[0] and len(set(w))==1: issues.append(f'Panels {i-3}-{i+1} use same composition')
    return issues

def foreshadow_issues(project, epnum):
    fp=os.path.join(project,'foreshadowing.md')
    if not os.path.exists(fp): return []
    out=[]
    for m in re.finditer(r'- \[ \] (.+?)（第(\d+)集埋下）',read(fp)):
        if int(m.group(2)) <= epnum and int(m.group(2)) < epnum-2:
            out.append(f'Long-unrecovered foreshadowing: {m.group(1)}')
    return out

def validate_episode(ep, project, mode, mn, mx):
    res={'file':os.path.basename(ep),'passed':True,'issues':[],'stats':{}}
    if not os.path.exists(ep): res['passed']=False; res['issues'].append('File does not exist'); return res
    c=read(ep); ps=panels(c); pc=len(ps); pages=count_pages(c); sc=count_scenes(c)
    expected_m=re.search(r'\*\*预计 Panel 数\*\*\s*[：:]\s*(\d+)', c)
    if expected_m:
        expected=int(expected_m.group(1))
        if expected <= 20:
            mn=max(6, expected-2)
            mx=expected+4
    res['stats'].update({'panels':pc,'pages':pages,'legacy_scenes':sc,'dialogues':len(re.findall(r'^-\s*[^：:\n]+[：:]',c,re.M))})
    if sc: res['passed']=False; res['issues'].append(f'Legacy Scene headers found: {sc}; use ### Panel under ## Page')
    if pages==0: res['passed']=False; res['issues'].append('Missing ## Page headers')
    if pc<mn: res['passed']=False; res['issues'].append(f'Too few panels: {pc} (expected >= {mn})')
    elif pc>mx: res['issues'].append(f'More panels than expected: {pc} (expected <= {mx})')
    for no,b in ps:
        miss=[x for x in FIELDS if x not in b]
        if miss: res['passed']=False; res['issues'].append(f'Panel {no} missing fields: '+', '.join(miss))
    if '## 本集结尾钩子' not in c: res['passed']=False; res['issues'].append('Missing ## 本集结尾钩子')
    if '## 下集提示' not in c: res['passed']=False; res['issues'].append('Missing ## 下集提示')
    m=re.search(r'ep(\d+)',os.path.basename(ep))
    if m: res['issues'] += foreshadow_issues(project,int(m.group(1)))
    res['issues'] += style_issues(project,ep) + quality_issues(c)
    return res

def main():
    ap=argparse.ArgumentParser(description='Validate Page/Panel comic episode')
    ap.add_argument('episode_path'); ap.add_argument('--project-dir','-p',required=True); ap.add_argument('--mode','-m',choices=['A','B','C'],default='B'); ap.add_argument('--strict','-s',action='store_true')
    a=ap.parse_args(); mode=a.mode
    cp=os.path.join(a.project_dir,'config.json')
    if os.path.exists(cp): mode=json.load(open(cp,encoding='utf-8')).get('density_mode',mode)
    mn,mx={'A':(25,45),'B':(40,70),'C':(140,260)}.get(mode,(40,70))
    r=validate_episode(a.episode_path,a.project_dir,mode,mn,mx)
    print(json.dumps(r,ensure_ascii=False,indent=2))
    if not r['passed'] or (a.strict and r['issues']): raise SystemExit(1)
if __name__=='__main__': main()
