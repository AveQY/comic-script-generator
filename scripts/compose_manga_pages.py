#!/usr/bin/env python3
"""Compose rendered panel images into manga pages with dynamic comic layouts.

Reads Page/Panel structure and each Panel's **格子** field, then places panels into
more manga-like page layouts instead of a fixed 2x3 grid. The goal is readable
page rhythm: establishing wide panel, small reaction/details, vertical tension,
and a larger hook/impact panel.
"""
import argparse
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def find_font():
    for c in ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if Path(c).exists():
            return c
    return None


def parse_pages(md):
    pages=[]; current=[]; panel_bodies={}
    ms=list(re.finditer(r'^###\s+Panel\s+(\d+)\b.*$', md, re.M))
    for i,m in enumerate(ms):
        no=int(m.group(1)); end=ms[i+1].start() if i+1<len(ms) else len(md)
        panel_bodies[no]=md[m.end():end]
    lines=md.splitlines()
    cur_page=[]
    for line in lines:
        pm=re.match(r'^##\s+Page\s+(\d+)', line)
        if pm:
            if cur_page: pages.append(cur_page); cur_page=[]
            continue
        m=re.match(r'^###\s+Panel\s+(\d+)', line)
        if m: cur_page.append(int(m.group(1)))
    if cur_page: pages.append(cur_page)
    if not pages:
        nums=sorted(panel_bodies)
        pages=[nums[i:i+6] for i in range(0,len(nums),6)]
    return pages, panel_bodies


def panel_kind(body):
    m=re.search(r'\*\*格子\*\*\s*[：:]\s*(.+)', body)
    return m.group(1).strip() if m else ''


def cover_crop(im, size):
    W,H=im.size; w,h=size
    scale=max(w/W,h/H)
    nw,nh=int(W*scale),int(H*scale)
    im=im.resize((nw,nh), Image.Resampling.LANCZOS)
    left=max(0,(nw-w)//2); top=max(0,(nh-h)//2)
    return im.crop((left,top,left+w,top+h))


def rects_for_page(n, page_num, W, H, margin, gutter, header):
    """Return manga-like rectangles for common 6-panel pages."""
    x0=margin; y0=header; ww=W-2*margin; hh=H-header-margin
    # 6-panel template: wide opener, two small beats, vertical tension + mid beat, wide hook.
    if n>=6:
        h1=int(hh*0.23); h2=int(hh*0.24); h3=int(hh*0.26); h4=hh-h1-h2-h3-3*gutter
        y1=y0; y2=y1+h1+gutter; y3=y2+h2+gutter; y4=y3+h3+gutter
        half=(ww-gutter)//2
        narrow=int(ww*0.36); wide=ww-narrow-gutter
        # Alternate pages so the vertical narrow panel changes side.
        if page_num % 2:
            row3=[(x0,y3,narrow,h3),(x0+narrow+gutter,y3,wide,h3)]
        else:
            row3=[(x0,y3,wide,h3),(x0+wide+gutter,y3,narrow,h3)]
        return [
            (x0,y1,ww,h1),
            (x0,y2,half,h2),
            (x0+half+gutter,y2,half,h2),
            row3[0],
            row3[1],
            (x0,y4,ww,h4),
        ][:n]
    # fallback for fewer panels
    cols=2 if n>1 else 1
    rows=(n+cols-1)//cols
    cw=(ww-(cols-1)*gutter)//cols; ch=(hh-(rows-1)*gutter)//rows
    return [(x0+(i%cols)*(cw+gutter), y0+(i//cols)*(ch+gutter), cw, ch) for i in range(n)]


def compose_page(render_dir, panels, bodies, out, title='', page_num=1):
    W,H=1240,1754
    margin=38; gutter=16; header=70
    canvas=Image.new('RGB',(W,H),'white')
    draw=ImageDraw.Draw(canvas)
    font_path=find_font()
    title_font=ImageFont.truetype(font_path,30) if font_path else ImageFont.load_default()
    small=ImageFont.truetype(font_path,20) if font_path else ImageFont.load_default()
    draw.text((margin,20), f'{title}  第{page_num}页', fill=(20,28,44), font=title_font)
    rects=rects_for_page(len(panels), page_num, W, H, margin, gutter, header)
    for idx,n in enumerate(panels):
        if idx>=len(rects): break
        x,y,w,h=rects[idx]
        img=render_dir/f'scene_{n:03d}.png'
        if img.exists():
            im=Image.open(img).convert('RGB')
            im=cover_crop(im,(w,h))
            canvas.paste(im,(x,y))
        else:
            draw.rectangle((x,y,x+w,y+h),fill=(245,247,251),outline=(200,210,225),width=3)
            draw.text((x+18,y+18),f'MISSING scene {n:03d}',fill=(120,130,150),font=small)
        # Manga page gutters/borders
        draw.rectangle((x,y,x+w,y+h),outline=(10,15,25),width=5)
        # Small panel number for debugging/review; unobtrusive.
        draw.rounded_rectangle((x+8,y+8,x+52,y+34),radius=8,fill=(255,255,255),outline=(20,28,44),width=2)
        draw.text((x+16,y+9),str(n),fill=(20,28,44),font=small)
    out.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(out,quality=94)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('episode')
    ap.add_argument('--render-dir',required=True)
    ap.add_argument('--output-dir',required=True)
    args=ap.parse_args()
    ep=Path(args.episode); rd=Path(args.render_dir); od=Path(args.output_dir)
    txt=ep.read_text(encoding='utf-8')
    title=re.search(r'^#\s+(.+)$',txt,re.M)
    title=title.group(1) if title else ep.stem
    pages,bodies=parse_pages(txt)
    count=0
    for i,panels in enumerate(pages,1):
        compose_page(rd,panels,bodies,od/f'{ep.stem}_page_{i:03d}.png',title,i)
        count+=1
    print({'episode':str(ep),'pages':count,'output_dir':str(od),'layout':'dynamic_manga'})

if __name__=='__main__':
    main()
