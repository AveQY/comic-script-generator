#!/usr/bin/env python3
"""Overlay comic speech bubbles/captions onto rendered panel images.

This fixes the common image-model issue where generated art lacks readable dialogue text.
It reads the source episode markdown (Page/Panel format) and draws the 气泡/旁白/拟声
fields onto rendered scene_XXX.png files deterministically with PIL.
"""
import argparse
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def find_font():
    candidates = [
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
        '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    return None


def parse_panels(md: str):
    panels = []
    parts = re.split(r'(?m)^###\s+Panel\s+(\d+)\s*$', md)
    # parts: header, num, body, num, body...
    for i in range(1, len(parts), 2):
        num = int(parts[i])
        body = parts[i+1]
        fields = {}
        matches = list(re.finditer(r'(?m)^\*\*(气泡|旁白|拟声)\*\*\s*[：:]\s*$', body))
        for idx, m in enumerate(matches):
            key = m.group(1)
            start = m.end()
            end = matches[idx+1].start() if idx+1 < len(matches) else len(body)
            # stop at next non-target bold field if earlier
            rest = body[start:end]
            next_field = re.search(r'(?m)^\*\*[^*]+\*\*\s*[：:]', rest)
            if next_field:
                rest = rest[:next_field.start()]
            text = rest.strip()
            fields[key] = text
        panels.append((num, fields))
    return panels


def clean_lines(text):
    if not text or text.strip() == '无':
        return []
    lines = []
    for line in text.splitlines():
        s = line.strip().lstrip('-').strip()
        if not s or s == '无':
            continue
        # 角色（位置，气泡类型）:"台词" -> 角色：台词
        m = re.match(r'(.+?)（.*?）\s*[：:]\s*["“](.*?)["”]\s*$', s)
        if m:
            s = f'{m.group(1).strip()}：{m.group(2).strip()}'
        m = re.match(r'(.+?)\s*[：:]\s*["“](.*?)["”]\s*$', s)
        if m:
            s = f'{m.group(1).strip()}：{m.group(2).strip()}'
        lines.append(s)
    return lines


def wrap_text(draw, text, font, max_width):
    out = []
    for raw in text.splitlines():
        cur = ''
        for ch in raw:
            test = cur + ch
            if draw.textbbox((0,0), test, font=font)[2] <= max_width:
                cur = test
            else:
                if cur:
                    out.append(cur)
                cur = ch
        if cur:
            out.append(cur)
    return out


def draw_bubble(draw, xy, text_lines, font, fill=(255,255,255,238), outline=(20,30,45,255), text_fill=(15,23,42,255)):
    x, y, w = xy
    pad = 18
    line_h = font.size + 8
    h = pad*2 + line_h*len(text_lines)
    draw.rounded_rectangle((x, y, x+w, y+h), radius=24, fill=fill, outline=outline, width=3)
    ty = y + pad
    for line in text_lines:
        draw.text((x+pad, ty), line, font=font, fill=text_fill)
        ty += line_h
    return h


def overlay_one(img_path: Path, fields, output_path: Path, font_path: str | None, include_narration: bool = False):
    im = Image.open(img_path).convert('RGBA')
    W, H = im.size
    layer = Image.new('RGBA', im.size, (0,0,0,0))
    draw = ImageDraw.Draw(layer)
    main_size = max(28, W//34)
    small_size = max(24, W//42)
    font = ImageFont.truetype(font_path, main_size) if font_path else ImageFont.load_default()
    small = ImageFont.truetype(font_path, small_size) if font_path else ImageFont.load_default()

    bubbles = clean_lines(fields.get('气泡',''))
    narr = clean_lines(fields.get('旁白',''))
    sfx = clean_lines(fields.get('拟声',''))

    if include_narration and narr:
        text = '\n'.join(narr[:2])
        lines = wrap_text(draw, text, small, int(W*0.82))[:4]
        draw.rounded_rectangle((40, 34, W-40, 34 + 28 + (small_size+7)*len(lines)), radius=12, fill=(15,23,42,225))
        yy = 48
        for line in lines:
            draw.text((58, yy), line, font=small, fill=(255,255,255,255)); yy += small_size+7

    if bubbles:
        left = bubbles[0::2]
        right = bubbles[1::2]
        maxw = int(W*0.43)
        y = int(H*0.58)
        if left:
            lines = wrap_text(draw, '\n'.join(left[:2]), font, maxw-36)[:5]
            draw_bubble(draw, (34, y, maxw), lines, font)
        if right:
            lines = wrap_text(draw, '\n'.join(right[:2]), font, maxw-36)[:5]
            draw_bubble(draw, (W-maxw-34, y+70, maxw), lines, font)

    if sfx:
        txt = re.sub(r'[`：:，,].*$', '', sfx[0]).strip()[:8]
        sfx_font = ImageFont.truetype(font_path, max(54, W//16)) if font_path else ImageFont.load_default()
        draw.text((W*0.08, H*0.18), txt, font=sfx_font, fill=(255,208,0,245), stroke_width=4, stroke_fill=(40,20,0,230))

    out = Image.alpha_composite(im, layer).convert('RGB')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.save(output_path, quality=95)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('episode')
    ap.add_argument('--render-dir', required=True, help='Directory containing scene_001.png etc')
    ap.add_argument('--output-dir', help='Default: overwrite render-dir')
    ap.add_argument('--overwrite', action='store_true', help='Overwrite existing images; otherwise writes *_lettered.png')
    ap.add_argument('--include-narration', action='store_true', help='Draw 旁白 boxes too; default is dialogue/SFX only for cleaner manga pages')
    args = ap.parse_args()
    episode = Path(args.episode)
    render_dir = Path(args.render_dir)
    output_dir = Path(args.output_dir) if args.output_dir else render_dir
    font_path = find_font()
    panels = parse_panels(episode.read_text(encoding='utf-8'))
    done = 0
    for num, fields in panels:
        src = render_dir / f'scene_{num:03d}.png'
        if not src.exists():
            continue
        if args.overwrite:
            dst = output_dir / f'scene_{num:03d}.png'
        else:
            dst = output_dir / f'scene_{num:03d}_lettered.png'
        overlay_one(src, fields, dst, font_path, include_narration=args.include_narration)
        done += 1
    print({'episode': str(episode), 'render_dir': str(render_dir), 'font': font_path, 'processed': done})

if __name__ == '__main__':
    main()
