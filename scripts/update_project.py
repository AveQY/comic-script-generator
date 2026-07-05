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
    """Extract character names from dialogue bubbles in episode."""
    with open(episode_path, 'r', encoding='utf-8') as f:
        content = f.read()

    characters = set()
    for line in content.split('\n'):
        stripped = line.strip()
        if not stripped.startswith('-'):
            continue
        # Skip SFX, captions, foreshadowing items, and generated stats.
        if stripped.startswith('- `') or stripped.startswith('- 旁白框') or stripped.startswith('- ['):
            continue
        if stripped.startswith('- 总') or stripped.startswith('- 验证状态'):
            continue
        match = re.match(r'^-\s*([^：\n]+)[：]', stripped)
        if not match:
            continue
        name = match.group(1).strip()
        name = re.sub(r'（[^）]*）', '', name).strip()
        if name and name not in ('旁白框', '总 Panel 数', '总对话数', '验证状态'):
            characters.add(name)

    return sorted(characters)

def strip_ai_prompt_blocks(content: str) -> str:
    """Remove fenced code blocks and AI prompt sections before heuristic extraction."""
    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    content = re.sub(r'\*\*AI 提示词\*\*：.*?(?=\n---|\n### Panel|\n## |\Z)', '', content, flags=re.DOTALL)
    return content


def extract_foreshadowing_candidates(episode_path: str) -> list:
    """Extract explicit foreshadowing candidates only.

    Conservative by design: do not auto-write synopsis, hook blocks, visual fields,
    prompts, SFX, transitions, or next-episode marketing copy into foreshadowing.md.
    Authors/LLM should add explicit lines like:
    - **伏笔**：银色手链会在蓝色霓虹下发热
    - **新增伏笔**：祁远相机会拍到未来一分钟
    """
    with open(episode_path, 'r', encoding='utf-8') as f:
        raw = f.read()

    content = strip_ai_prompt_blocks(raw)
    candidates = set()
    patterns = [
        r'\*\*(?:伏笔|新增伏笔|埋设伏笔)\*\*：\s*([^\n]+)',
        r'^-\s*(?:伏笔|新增伏笔|埋设伏笔)[：:]\s*([^\n]+)',
    ]
    for pat in patterns:
        for m in re.finditer(pat, content, flags=re.MULTILINE):
            desc = m.group(1).strip()
            desc = re.sub(r'[。；;，,]\s*$', '', desc)
            if 6 <= len(desc) <= 80:
                candidates.add(desc)
    return sorted(candidates)[:5]



def extract_episode_summary_info(episode_path: str, characters: list = None, foreshadowing: list = None) -> dict:
    """Extract human-readable summary fields from a Page/Panel episode."""
    with open(episode_path, 'r', encoding='utf-8') as f:
        content = f.read()
    def one(pattern, default='无'):
        m = re.search(pattern, content, flags=re.MULTILINE | re.DOTALL)
        if not m:
            return default
        value = m.group(1).strip()
        value = re.sub(r'\n+', ' ', value).strip()
        return value or default
    summary = one(r'\*\*故事梗概\*\*[：:]\s*(.+?)(?:\n\*\*|\n---|\Z)', '无')
    hook = one(r'\*\*本集钩子\*\*[：:]\s*(.+?)(?:\n\*\*|\n---|\Z)', '无')
    ending_hook = one(r'\*\*钩子台词\*\*[：:]\s*["“]?(.+?)["”]?(?:\n|\Z)', '')
    if ending_hook and ending_hook != '无':
        hook = hook + ' / ' + ending_hook if hook != '无' else ending_hook
    chars = '、'.join(characters or []) or '无'
    fs = '、'.join(foreshadowing or []) or '无'
    return {
        'summary': summary,
        'turning_point': hook,
        'characters': chars,
        'foreshadowing': fs,
    }

def count_stats(episode_path: str) -> dict:
    """Count panels, pages, dialogues, and prompt presence in episode."""
    with open(episode_path, 'r', encoding='utf-8') as f:
        content = f.read()
    panels = len(re.findall(r'^### Panel \d+', content, re.MULTILINE))
    pages = len(re.findall(r'^## Page \d+', content, re.MULTILINE))
    dialogues = 0
    for line in content.split('\n'):
        stripped = line.strip()
        if not stripped.startswith('-'):
            continue
        if stripped.startswith('- `') or stripped.startswith('- 旁白框') or stripped.startswith('- 总') or stripped.startswith('- 验证状态'):
            continue
        if re.match(r'^-\s*[^：\n]+[：]', stripped):
            dialogues += 1
    has_ai_prompts = '**AI 提示词**' in content or 'AI 提示词' in content
    title_match = re.search(r'^#\s+第\d+集[：:]\s*(.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else os.path.basename(episode_path)
    return {
        'panels': panels,
        'pages': pages,
        'dialogues': dialogues,
        'has_ai_prompts': has_ai_prompts,
        'title': title
    }


def update_summary(project_dir: str, episode_num: int, stats: dict, summary_info: dict = None):
    """Update summary.md with extracted episode info, avoiding placeholder-only summaries."""
    summary_path = os.path.join(project_dir, 'summary.md')
    summary_info = summary_info or {}

    if os.path.exists(summary_path):
        with open(summary_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = "# " + os.path.basename(project_dir) + " - 项目摘要\n\n"

    episode_header = f"## 第{episode_num}集："
    if episode_header in content:
        print(f"  [!] 第{episode_num}集摘要已存在，跳过更新")
        return

    entry = "\n## 第" + str(episode_num) + "集：" + stats['title'] + "\n"
    entry += "- **主要情节**：" + summary_info.get('summary', '无') + "\n"
    entry += "- **关键转折**：" + summary_info.get('turning_point', '无') + "\n"
    entry += "- **新增角色**：" + summary_info.get('characters', '无') + "\n"
    entry += "- **伏笔**：" + summary_info.get('foreshadowing', '无') + "\n"
    entry += "- **Panel 数**：" + str(stats.get('panels', 0)) + "个\n"
    entry += "- **对话数**：" + str(stats['dialogues']) + "段\n"

    content += entry

    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("  ✓ 更新 summary.md")

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
        desc = (cand.get('line') if isinstance(cand, dict) else str(cand))[:80].strip()
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
    config['script_unit'] = 'page_panel'
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
    print(f"Panels: {stats.get('panels', 0)}, Pages: {stats.get('pages', 0)}, Dialogues: {stats['dialogues']}, AI Prompts: {'✓' if stats['has_ai_prompts'] else '✗'}")
    print(f"Characters detected: {len(characters)}")
    print(f"Potential foreshadowing: {len(foreshadowing)}")
    
    if args.dry_run:
        print("\n[DRY RUN] No files were modified.")
        return
    
    # Update files
    print(f"\nUpdating project files...")
    summary_info = extract_episode_summary_info(args.episode_path, characters, foreshadowing)
    update_summary(args.project_dir, args.episode_num, stats, summary_info)
    update_characters(args.project_dir, characters)
    update_foreshadowing(args.project_dir, foreshadowing, args.episode_num)
    update_config(args.project_dir, args.episode_num)
    
    print(f"\n✓ Project files updated successfully!")


if __name__ == "__main__":
    main()
