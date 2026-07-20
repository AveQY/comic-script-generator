#!/usr/bin/env python3
"""Export comic episode to light novel format with key scene illustrations.

Reads a Page/Panel episode file and produces:
1. A light-novel-style Markdown file (narrative + dialogue, no panel jargon)
2. A render manifest of 5-8 key scenes per episode for illustration

Usage:
    python3 scripts/export_light_novel.py episodes/ep001_xxx.md --project-dir projects/<name>
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path


def parse_episode(path: Path):
    """Parse episode file, return list of panels with their content."""
    text = path.read_text(encoding='utf-8')
    
    # Split by Panel markers
    panel_pattern = re.compile(r'^### Panel (\d+)', re.M)
    panels = []
    
    parts = panel_pattern.split(text)
    # parts[0] = header, then alternating [num, content, num, content...]
    for i in range(1, len(parts), 2):
        panel_num = int(parts[i])
        panel_text = parts[i + 1] if i + 1 < len(parts) else ''
        panels.append({'num': panel_num, 'text': panel_text})
    
    return panels


def extract_field(panel_text: str, field: str) -> str:
    """Extract a field value from panel text. Returns empty string if not found."""
    # Pattern: **字段**：内容
    pattern = re.compile(r'\*\*' + re.escape(field) + r'\*\*[：:]\s*(.*?)(?=\n\*\*|\n---|\Z)', re.S)
    m = pattern.search(panel_text)
    if m:
        return m.group(1).strip()
    return ''


def extract_dialogues(panel_text: str) -> list:
    """Extract dialogue lines from panel bubbles."""
    dialogues = []
    for line in panel_text.split('\n'):
        line = line.strip()
        # Skip narration / 旁白 lines (handled separately)
        if re.match(r'^-?\s*旁白', line):
            continue
        m = re.match(r'^-\s*(?:（[^）]*）)?\s*([^：:]+)[：:]\s*"(.+)"', line)
        if m:
            speaker = m.group(1).strip()
            line_text = m.group(2).strip()
            # Clean up: remove action descriptors from speaker for readability
            speaker_clean = re.sub(r'[（(][^）)]*[）)]', '', speaker).strip()
            dialogues.append({'speaker': speaker_clean, 'line': line_text})
    return dialogues


def extract_narration(panel_text: str) -> str:
    """Extract narration/旁白 text."""
    narration = extract_field(panel_text, '旁白')
    if narration and narration != '无':
        # Clean up the raw format
        narration = re.sub(r'^[-−]?\s*', '', narration)
        narration = re.sub(r'旁白框[（(][^）)]*[）)]?\s*[：:]\s*', '', narration)
        narration = re.sub(r'^["""\u201c\u201d]|["""\u201c\u201d]$', '', narration)
        narration = narration.strip()
        return narration
    return ''


def extract_scene_desc(panel_text: str) -> str:
    """Extract the 画面 (scene visual) description."""
    return extract_field(panel_text, '画面')


def pick_key_scenes(panels, total_key=7):
    """Pick key scenes for illustration. Distributes across the episode."""
    total = len(panels)
    if total <= total_key:
        return list(range(total))
    
    # Always include first, last, and evenly spaced in between
    indices = [0]  # first panel
    step = (total - 1) / (total_key - 1)
    for i in range(1, total_key - 1):
        idx = round(i * step)
        if idx >= total:
            idx = total - 1
        if idx not in indices:
            indices.append(idx)
    if total - 1 not in indices:
        indices.append(total - 1)
    
    return sorted(indices)


def gen_light_novel(panels, key_indices, episode_title, episode_num):
    """Generate light novel format text."""
    lines = []
    lines.append(f"# 第{episode_num}集：{episode_title}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    for i, panel in enumerate(panels):
        scene = extract_scene_desc(panel['text'])
        narr = extract_narration(panel['text'])
        dials = extract_dialogues(panel['text'])
        
        # Scene description → narrative text
        if scene and scene != '无':
            desc = scene
            lines.append(desc)
            lines.append("")
        
        # Narration (only if it has real content)
        if narr:
            lines.append(f"> {narr}")
            lines.append("")
        
        # Dialogues - clean up doubled quotes
        for d in dials:
            line_text = d['line'].strip('"').strip('"').strip('\u201c').strip('\u201d')
            lines.append(f"「{line_text}」——{d['speaker']}")
        if dials:
            lines.append("")
        
        # Key scene illustration marker
        if i in key_indices:
            scene_num = key_indices.index(i) + 1
            lines.append(f"<!-- ILLUST_{scene_num} -->")
            lines.append("")
        
        # Light panel separator (skip if we just had dialogue or narration)
        if lines[-1:] != ['']:
            lines.append("")
    
    return '\n'.join(lines)


def gen_render_manifest(panels, key_indices, ep_name, project_dir):
    """Generate a render manifest for key scenes only."""
    manifest = {
        'episode': ep_name,
        'project': str(project_dir),
        'total_panels': len(panels),
        'key_scenes': [],
        'render_instructions': {
            'model': 'gpt-image-2',
            'size': '1024x1024',
            'style_prefix': 'masterpiece, best quality, modern manga style, bold lines, screentone, dynamic angles, sharp details, anime aesthetic',
            'style_suffix': 'cinematic lighting, no text, no letters, leave empty space for speech bubbles',
        }
    }
    
    for idx in key_indices:
        panel = panels[idx]
        scene = extract_scene_desc(panel['text'])
        composition = extract_field(panel['text'], '构图')
        dials = extract_dialogues(panel['text'])
        
        entry = {
            'panel_num': panel['num'],
            'index': idx,
            'scene': scene,
            'composition': composition,
            'dialogues': [f"{d['speaker']}：{d['line']}" for d in dials],
        }
        manifest['key_scenes'].append(entry)
    
    return manifest


def main():
    parser = argparse.ArgumentParser(description='Export comic episode to light novel format')
    parser.add_argument('episode', help='Episode markdown file path')
    parser.add_argument('--project-dir', required=True, help='Project directory')
    parser.add_argument('--output', '-o', help='Output path override')
    parser.add_argument('--illustrations', '-i', type=int, default=7, help='Number of key scene illustrations (default: 7)')
    args = parser.parse_args()
    
    ep_path = Path(args.episode)
    project_dir = Path(args.project_dir)
    
    if not ep_path.exists():
        print(json.dumps({'status': 'error', 'message': f'Episode not found: {ep_path}'}))
        sys.exit(1)
    
    # Parse episode
    panels = parse_episode(ep_path)
    if not panels:
        print(json.dumps({'status': 'error', 'message': 'No panels found'}))
        sys.exit(1)
    
    # Extract episode title
    ep_text = ep_path.read_text(encoding='utf-8')
    title_match = re.search(r'^#\s*(第\d+集[：:]\s*(.+))', ep_text, re.M)
    episode_title = title_match.group(2).strip() if title_match else ep_path.stem
    episode_num = re.search(r'(\d+)', ep_path.stem)
    episode_num = int(episode_num.group(1)) if episode_num else 1
    
    # Pick key scenes
    key_indices = pick_key_scenes(panels, args.illustrations)
    
    # Generate light novel text
    novel = gen_light_novel(panels, key_indices, episode_title, episode_num)
    
    # Generate key scene manifest
    manifest = gen_render_manifest(panels, key_indices, ep_path.stem, project_dir)
    
    # Create output directories
    novel_dir = project_dir / 'light_novel'
    novel_dir.mkdir(parents=True, exist_ok=True)
    manifest_dir = project_dir / 'render_input'
    manifest_dir.mkdir(parents=True, exist_ok=True)
    
    # Save light novel
    novel_filename = ep_path.stem.replace('ep', 'ln') + '.md'
    novel_path = novel_dir / novel_filename
    novel_path.write_text(novel, encoding='utf-8')
    
    # Save render manifest
    manifest_filename = ep_path.stem.replace('ep', 'key_scenes') + '.json'
    manifest_path = manifest_dir / manifest_filename
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    
    # Print summary
    print(json.dumps({
        'status': 'ok',
        'project': str(project_dir),
        'episode': ep_path.stem,
        'panels': len(panels),
        'key_scenes': len(key_indices),
        'key_scene_indices': key_indices,
        'light_novel': str(novel_path),
        'render_manifest': str(manifest_path),
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()