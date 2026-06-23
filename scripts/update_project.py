#!/usr/bin/env python3
"""
Comic Script Generator - Auto Update Project Files
Extracts structured info from episode markdown and updates project files.
"""

import os
import re
import json
import argparse
from datetime import datetime, timezone, timedelta


def extract_characters_from_episode(episode_path: str) -> list:
    """Extract character names from dialogue lines in episode."""
    with open(episode_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    characters = set()
    # Match dialogue lines like: - 角色名："台词" or - 角色名（心理独白）："台词"
    dialogue_pattern = r'^-\s*([^：\n]*?)[：\n]'
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('-'):
            match = re.match(r'^-\s*([^：\n]*?)[：\n]', line)
            if match:
                name = match.group(1).strip()
                name = re.sub(r'（[^）]*）', '', name).strip()
                # Filter out non-character names
                if name and len(name) <= 10 and not any(c in name for c in ['/', '\\', '[', ']']):
                    characters.add(name)
    
    # Also look for character profile sections in the episode
    profile_pattern = r'\*\*([^*]+)\*\*[：:]\s*([^\n]+)'
    for match in re.finditer(profile_pattern, content):
        label = match.group(1).strip()
        value = match.group(2).strip()
        if '角色' in label or '人物' in label or 'name' in label.lower():
            characters.add(value.split(' ')[0])
    
    return sorted(characters)


def extract_foreshadowing_candidates(episode_path: str) -> list:
    """Extract potential foreshadowing from episode content."""
    with open(episode_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    candidates = []
    # Keywords that suggest foreshadowing
    keywords = [
        '神秘', '奇怪', '疑惑', '不对劲', '总觉得', '好像', '似乎',
        '想起', '回忆', '往事', '旧', '遗物', '信件', '照片',
        '为什么', '怎么会', '居然', '竟然', '没想到',
        '秘密', '隐瞒', '逃避', '不敢', '犹豫'
    ]
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if any(kw in line for kw in keywords):
            # Get context (surrounding lines)
            start = max(0, i - 2)
            end = min(len(lines), i + 3)
            context = '\n'.join(lines[start:end])
            if len(context) > 20:  # Skip very short matches
                candidates.append({
                    'line': line,
                    'context': context,
                    'line_num': i + 1
                })
    
    return candidates


def count_stats(episode_path: str) -> dict:
    """Count scenes and dialogues in episode."""
    with open(episode_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    scenes = len(re.findall(r'^## Scene \d+', content, re.MULTILINE))
    dialogues = len(re.findall(r'^-\s*[^：\n]+[：\n]', content, re.MULTILINE))
    has_ai_prompts = '**AI 提示词**' in content or 'AI 提示词' in content
    
    # Extract episode title
    title_match = re.search(r'^#\s+第\d+集[：:]\s*(.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else os.path.basename(episode_path)
    
    return {
        'scenes': scenes,
        'dialogues': dialogues,
        'has_ai_prompts': has_ai_prompts,
        'title': title
    }


def update_summary(project_dir: str, episode_num: int, stats: dict, key_events: list = None):
    """Update summary.md with new episode info."""
    summary_path = os.path.join(project_dir, 'summary.md')
    
    # Read existing summary
    if os.path.exists(summary_path):
        with open(summary_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = f"# {os.path.basename(project_dir)} - 项目摘要\n\n"
    
    # Check if this episode already has an entry
    episode_header = f"## 第{episode_num}集："
    if episode_header in content:
        print(f"  [!] 第{episode_num}集摘要已存在，跳过更新")
        return
    
    # Add new episode entry
    entry = f"\n## 第{episode_num}集：{stats['title']}\n"
    entry += f"- **主要情节**：待补充\n"
    entry += f"- **关键转折**：待补充\n"
    entry += f"- **新增角色**：待补充\n"
    entry += f"- **伏笔**：待补充\n"
    entry += f"- **场景数**：{stats['scenes']}个\n"
    entry += f"- **对话数**：{stats['dialogues']}段\n"
    
    content += entry
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✓ 更新 summary.md")


def update_characters(project_dir: str, new_characters: list):
    """Update characters.md with new character profiles."""
    chars_path = os.path.join(project_dir, 'characters.md')
    
    if not new_characters:
        print("  [!] 未检测到新角色")
        return
    
    # Read existing characters
    if os.path.exists(chars_path):
        with open(chars_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = f"# {os.path.basename(project_dir)} - 角色档案\n\n"
    
    existing_chars = set()
    for line in content.split('\n'):
        if line.startswith('## ') and not line.startswith('## 未') and not line.startswith('## 已'):
            char_name = line.replace('## ', '').strip()
            if char_name:
                existing_chars.add(char_name)
    
    added = []
    for char in new_characters:
        if char not in existing_chars and char not in ['旁白', '内心', '心理独白', '字幕']:
            entry = f"\n## {char}\n"
            entry += f"- **全名**：待补充\n"
            entry += f"- **年龄**：待补充\n"
            entry += f"- **外貌**：待补充\n"
            entry += f"- **性格**：待补充\n"
            entry += f"- **背景**：待补充\n"
            entry += f"- **首次登场**：待补充\n"
            entry += f"- **关键情节**：待补充\n"
            content += entry
            added.append(char)
    
    if added:
        with open(chars_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ 新增角色到 characters.md: {', '.join(added)}")
    else:
        print("  [!] 没有新角色需要添加")


def update_foreshadowing(project_dir: str, candidates: list, episode_num: int):
    """Update foreshadowing.md with potential foreshadowing."""
    fs_path = os.path.join(project_dir, 'foreshadowing.md')
    
    if not candidates:
        print("  [!] 未检测到潜在伏笔")
        return
    
    # Read existing foreshadowing
    if os.path.exists(fs_path):
        with open(fs_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = f"# {os.path.basename(project_dir)} - 伏笔追踪\n\n## 未回收\n\n## 已回收\n"
    
    # Check if "未回收" section exists
    if '## 未回收' not in content:
        content = content.rstrip() + "\n\n## 未回收\n\n## 已回收\n"
    
    # Add candidates (limit to top 3 to avoid noise)
    added = []
    for cand in candidates[:3]:
        # Create a short description from the line
        desc = cand['line'][:50].strip()
        if len(desc) < 10:
            continue
        
        entry = f"- [ ] {desc}（第{episode_num}集埋下）\n"
        if entry not in content:
            content = content.replace('## 未回收\n', '## 未回收\n' + entry)
            added.append(desc[:30])
    
    if added:
        with open(fs_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ 新增伏笔到 foreshadowing.md: {len(added)} 条")
    else:
        print("  [!] 没有新伏笔需要添加")


def update_config(project_dir: str, episode_num: int):
    """Update config.json with current episode number and timestamp."""
    config_path = os.path.join(project_dir, 'config.json')
    
    if not os.path.exists(config_path):
        print("  [!] config.json 不存在")
        return
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    config['current_episode'] = max(config.get('current_episode', 0), episode_num)
    config['updated_at'] = datetime.now(timezone(timedelta(hours=8))).isoformat()
    config['status'] = 'writing' if config['current_episode'] < config.get('total_episodes', 6) else 'completed'
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"  ✓ 更新 config.json (current_episode={config['current_episode']}, status={config['status']})")


def main():
    parser = argparse.ArgumentParser(description="Update project files from episode")
    parser.add_argument("episode_path", help="Path to episode markdown file")
    parser.add_argument("--project-dir", "-p", required=True,
                        help="Project directory")
    parser.add_argument("--episode-num", "-n", type=int, required=True,
                        help="Episode number (e.g., 1 for ep001)")
    parser.add_argument("--dry-run", "-d", action="store_true",
                        help="Show what would be updated without writing")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.episode_path):
        print(f"Error: Episode file not found: {args.episode_path}")
        return
    
    print(f"\n{'='*50}")
    print(f"Updating project from: {os.path.basename(args.episode_path)}")
    print(f"{'='*50}")
    
    # Extract info
    stats = count_stats(args.episode_path)
    characters = extract_characters_from_episode(args.episode_path)
    foreshadowing = extract_foreshadowing_candidates(args.episode_path)
    
    print(f"\nEpisode: 第{args.episode_num}集 - {stats['title']}")
    print(f"Scenes: {stats['scenes']}, Dialogues: {stats['dialogues']}, AI Prompts: {'✓' if stats['has_ai_prompts'] else '✗'}")
    print(f"Characters detected: {len(characters)}")
    print(f"Potential foreshadowing: {len(foreshadowing)}")
    
    if args.dry_run:
        print("\n[DRY RUN] No files were modified.")
        return
    
    # Update files
    print(f"\nUpdating project files...")
    update_summary(args.project_dir, args.episode_num, stats)
    update_characters(args.project_dir, characters)
    update_foreshadowing(args.project_dir, foreshadowing, args.episode_num)
    update_config(args.project_dir, args.episode_num)
    
    print(f"\n✓ Project files updated successfully!")


if __name__ == "__main__":
    main()
