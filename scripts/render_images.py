#!/usr/bin/env python3
"""Render images through OpenAI-compatible image generation endpoint.

Sensitive configuration rule:
- Never store real API tokens, private domains, or credentials inside this skill.
- Keep them in a local private JSON file and point COMIC_IMAGE_CONFIG to it.
- A safe template is provided as config.example.json.

Config priority:
1. --config
2. $COMIC_IMAGE_CONFIG
3. ~/.config/comic-script-generator/image_config.json

Expected config shape:
{
  "image_generation": {
    "endpoint": "https://<your-image-api-domain>/v1/images/generations",
    "authorization": "Bearer <your-private-token>",
    "model": "gpt-image-2",
    "size": "1024x1024",
    "timeout_seconds": 300
  }
}
"""
import argparse
import base64
import json
import os
import re
import sys
import time
import concurrent.futures
import urllib.error
import urllib.request
from pathlib import Path


def load_config(path: str | None):
    candidates = []
    if path:
        candidates.append(Path(path).expanduser())
    if os.environ.get('COMIC_IMAGE_CONFIG'):
        candidates.append(Path(os.environ['COMIC_IMAGE_CONFIG']).expanduser())
    candidates.append(Path.home() / '.config' / 'comic-script-generator' / 'image_config.json')
    for p in candidates:
        if p.exists():
            return json.loads(p.read_text(encoding='utf-8')), p
    raise FileNotFoundError(
        'No image config found. Store private credentials locally and pass --config, '
        'set COMIC_IMAGE_CONFIG, or create ~/.config/comic-script-generator/image_config.json. '
        'Do not put real credentials in the skill directory; use config.example.json only as a template.'
    )


def parse_prompt_file(path: Path):
    text = path.read_text(encoding='utf-8')
    prompts = []
    # Prefer story-renderer export blocks: ## 镜头 N ... **正向提示词** fenced block
    for m in re.finditer(r'^##\s+镜头\s+(\d+).*?\*\*正向提示词\*\*：\s*```(?:text)?\s*(.*?)```', text, re.S | re.M):
        prompts.append((int(m.group(1)), m.group(2).strip()))
    if prompts:
        return prompts
    # Fallback: Panel AI prompt positive section
    for i, m in enumerate(re.finditer(r'正向[：:]\s*```(?:text)?\s*(.*?)```', text, re.S), 1):
        prompts.append((i, m.group(1).strip()))
    if prompts:
        return prompts
    return [(1, text.strip())]


def call_image_api(endpoint, auth, model, prompt, size, timeout):
    payload = json.dumps({'model': model, 'prompt': prompt, 'size': size}, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={'Authorization': auth, 'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode('utf-8')
    return json.loads(raw)


def save_result(result, out_dir: Path, stem: str):
    out_dir.mkdir(parents=True, exist_ok=True)
    data = result.get('data') or []
    if not data:
        (out_dir / f'{stem}.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        return str(out_dir / f'{stem}.json')
    item = data[0]
    if item.get('b64_json'):
        img = base64.b64decode(item['b64_json'])
        path = out_dir / f'{stem}.png'
        path.write_bytes(img)
        return str(path)
    if item.get('url'):
        url = item['url']
        (out_dir / f'{stem}.url.txt').write_text(url, encoding='utf-8')
        try:
            with urllib.request.urlopen(url, timeout=120) as resp:
                img = resp.read()
            path = out_dir / f'{stem}.png'
            path.write_bytes(img)
            return str(path)
        except Exception:
            return str(out_dir / f'{stem}.url.txt')
    path = out_dir / f'{stem}.json'
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    return str(path)


def main():
    ap = argparse.ArgumentParser(description='Generate images from comic/story-renderer prompt markdown')
    ap.add_argument('prompt_file', help='Markdown file containing render prompts')
    ap.add_argument('--config', help='Image config JSON path')
    ap.add_argument('--output-dir', '-o', help='Output directory; default: <project>/rendered/<prompt_file_stem>')
    ap.add_argument('--limit', type=int, default=1, help='How many prompts to render; default 1 for cost control')
    ap.add_argument('--start', type=int, default=1, help='1-based prompt index to start')
    ap.add_argument('--sleep', type=float, default=0.5, help='Delay between requests')
    ap.add_argument('--workers', type=int, default=1, help='Concurrent image requests; use 2-3 to speed up while avoiding rate limits')
    ap.add_argument('--retries', type=int, default=2, help='Retries per image for transient 5xx/network errors')
    args = ap.parse_args()

    cfg, cfg_path = load_config(args.config)
    img_cfg = cfg.get('image_generation', cfg)
    endpoint = img_cfg['endpoint']
    auth = img_cfg['authorization']
    model = img_cfg.get('model', 'gpt-image-2')
    size = img_cfg.get('size', '1024x1024')
    timeout = int(img_cfg.get('timeout_seconds', 300))

    prompt_file = Path(args.prompt_file).expanduser()
    prompts = parse_prompt_file(prompt_file)
    selected = prompts[args.start-1: args.start-1 + args.limit]
    if args.output_dir:
        out_dir = Path(args.output_dir).expanduser()
    else:
        out_dir = prompt_file.parent.parent / 'rendered' / prompt_file.stem

    def render_one(item):
        seq, prompt = item
        last = None
        for attempt in range(args.retries + 1):
            try:
                if args.sleep and attempt == 0:
                    time.sleep(args.sleep * max(0, (seq - args.start) % max(1, args.workers)))
                result = call_image_api(endpoint, auth, model, prompt, size, timeout)
                saved = save_result(result, out_dir, f'scene_{seq:03d}')
                return {'scene': seq, 'status': 'ok', 'output': saved}
            except urllib.error.HTTPError as e:
                body = e.read().decode('utf-8', 'ignore')
                last = {'scene': seq, 'status': 'http_error', 'code': e.code, 'body': body[:500]}
                if e.code in (429, 500, 502, 503, 504) and attempt < args.retries:
                    time.sleep((2 ** attempt) * 2 + (seq % 3))
                    continue
                return last
            except Exception as e:
                last = {'scene': seq, 'status': 'error', 'error': repr(e)}
                if attempt < args.retries:
                    time.sleep((2 ** attempt) * 2 + (seq % 3))
                    continue
                return last
        return last or {'scene': seq, 'status': 'error', 'error': 'unknown'}

    workers = max(1, int(args.workers or 1))
    if workers == 1:
        outputs = [render_one(item) for item in selected]
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
            outputs = list(ex.map(render_one, selected))
    outputs.sort(key=lambda x: x.get('scene', 0))

    print(json.dumps({'status': 'done', 'config': str(cfg_path), 'prompt_file': str(prompt_file), 'outputs': outputs}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
