#!/usr/bin/env python3
"""Restore raw generated images from saved *.url.txt files.

Use this when lettered images were overwritten and you want to re-apply cleaner
comic lettering from the original image URLs.
"""
import argparse
import urllib.request
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root', help='Project rendered directory or project directory')
    ap.add_argument('--overwrite', action='store_true')
    args = ap.parse_args()
    root = Path(args.root)
    count = 0
    for ufile in root.rglob('scene_*.url.txt'):
        png = ufile.with_suffix('').with_suffix('.png')  # scene_001.url.txt -> scene_001.png
        if png.exists() and not args.overwrite:
            continue
        url = ufile.read_text(encoding='utf-8').strip()
        if not url:
            continue
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                data = r.read()
            png.write_bytes(data)
            count += 1
            print('restored', png)
        except Exception as e:
            print('failed', ufile, repr(e))
    print({'restored': count})

if __name__ == '__main__':
    main()
