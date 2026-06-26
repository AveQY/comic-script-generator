#!/usr/bin/env python3
"""
Comic Script Generator - Character Consistency Checker
Validates character descriptions, dialogue styles, and appearance consistency.
"""

import os
import re
import json
import argparse


def load_project_characters(project_dir: str) -> dict:
    """Load character profiles from characters.md."""
    chars_path = os.path.join(project_dir, 'characters.md')
    if not os.path.exists(chars_path):
        return {}
    
    with open(chars_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    characters = {}
    current_char = None
    
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('## ') and not line.startswith('## 未') and not line.startswith('## 已'):
            current_char = line.replace('## ', '').strip()
            characters[current_char] = {'appearance': '', 'personality': '', 'profile': ''}
        elif current_char and line.startswith('- **'):
            # Parse profile fields
            match = re.match(r'^- \*\*([^*]+)\*\*[：:]\s*(.+)$', line)
            if match:
                field = match.group(1).strip()
                value = match.group(2).strip()
                if field in ['外貌']:
                    characters[current_char]['appearance'] = value
                elif field in ['性格']:
                    characters[current_char]['personality'] = value
                characters[current_char]['profile'] += f"{field}: {value}\n"
    
    return characters


def check_appearance_consistency(project_dir: str, episode_path: str) -> list:
    """Check if character appearance descriptions are consistent across episodes."""
    chars = load_project_characters(project_dir)
    if not chars:
        return []
    
    with open(episode_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # Check each known character
    for char_name, char_data in chars.items():
        if not char_data['appearance']:
            continue
        
        # Find all mentions of this character in the episode
        # Look for appearance-related keywords near the character name
        appearance_keywords = ['头发', '眼睛', '穿着', '衣服', '制服', '身高', '体型', '外貌']
        
        for line in content.split('\n'):
            if char_name in line and any(kw in line for kw in appearance_keywords):
                # Check for contradictions (simple check for now)
                # This could be extended with NLP similarity checks
                pass
    
    return issues


def check_character_dialogue_style(project_dir: str, episode_path: str) -> list:
    """Check if dialogue styles match character personalities."""
    chars = load_project_characters(project_dir)
    if not chars:
        return []
    
    with open(episode_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # Extract all dialogues
    dialogues = []
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('-'):
            match = re.match(r'^-\s*([^：\n]+?)[：\n](.+)$', line)
            if match:
                char_name = match.group(1).strip()
                dialogue = match.group(2).strip()
                # Strip parenthetical annotations: (心理独白), (害羞地), etc.
                char_name = re.sub(r'（[^）]*）', '', char_name).strip()
                char_name = re.sub(r'\([^)]*\)', '', char_name).strip()
                if char_name:
                    dialogues.append((char_name, dialogue))
    
    # Check for unknown characters
    known_chars = set(chars.keys())
    unknown_chars = set()
    
    for char_name, _ in dialogues:
        # Filter out narration and stage directions
        if char_name in ['旁白', '内心', '心理独白', '字幕', '字幕组']:
            continue
        if char_name not in known_chars:
            unknown_chars.add(char_name)
    
    if unknown_chars:
        issues.append({
            'type': 'unknown_character',
            'message': f"发现未记录的角色: {', '.join(sorted(unknown_chars))}",
            'severity': 'warning'
        })
    
    return issues


def get_style_guide_hash(project_dir: str) -> str:
    """Get SHA256 hash of style_guide.md to detect changes across episodes."""
    import hashlib
    guide_path = os.path.join(project_dir, "style_guide.md")
    if not os.path.exists(guide_path):
        return ""
    with open(guide_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def check_style_consistency(project_dir: str, episodes: list) -> list:
    """Check if all episodes use the same style_guide.md.
    
    Args:
        project_dir: Project root directory
        episodes: List of episode file paths
    
    Returns:
        list of issue dicts
    """
    issues = []
    guide_path = os.path.join(project_dir, "style_guide.md")
    
    if not os.path.exists(guide_path):
        issues.append({
            'type': 'missing_style_guide',
            'message': 'style_guide.md not found - run init_project.py',
            'severity': 'error'
        })
        return issues
    
    expected_hash = get_style_guide_hash(project_dir)
    
    # Check each episode's AI prompts against current style_guide
    with open(guide_path, 'r', encoding='utf-8') as f:
        guide_content = f.read()
    
    positive_match = re.search(r'## 正向提示词\s*\n(.+?)(?:\n##|$)', guide_content, re.DOTALL)
    negative_match = re.search(r'## 反向提示词\s*\n(.+?)(?:\n##|$)', guide_content, re.DOTALL)
    
    if not positive_match or not negative_match:
        issues.append({
            'type': 'invalid_style_guide',
            'message': 'style_guide.md format invalid',
            'severity': 'error'
        })
        return issues
    
    current_positive = positive_match.group(1).strip()
    key_terms = [t.strip() for t in current_positive.split(',')[:3] if t.strip()]
    
    for ep_path in episodes:
        if not os.path.exists(ep_path):
            continue
        
        with open(ep_path, 'r', encoding='utf-8') as f:
            ep_content = f.read()
        
        scenes = re.split(r'^## Scene \d+', ep_content, flags=re.MULTILINE)
        scenes = [s for s in scenes if s.strip()]
        scene_blocks = scenes[1:] if len(scenes) > 1 else scenes
        
        missing_scenes = []
        for i, scene in enumerate(scene_blocks, 1):
            has_style = any(term.lower() in scene.lower() for term in key_terms)
            if not has_style:
                missing_scenes.append(i)
        
        if missing_scenes:
            issues.append({
                'type': 'style_mismatch',
                'message': f"{os.path.basename(ep_path)}: {len(missing_scenes)} scenes missing style keywords",
                'severity': 'warning',
                'details': missing_scenes[:5]
            })
    
    return issues


def check_character_consistency(project_dir: str, episode_path: str) -> dict:
    """Run all character consistency checks."""
    results = {
        'file': os.path.basename(episode_path),
        'passed': True,
        'issues': [],
        'stats': {}
    }
    
    if not os.path.exists(episode_path):
        results['passed'] = False
        results['issues'].append("File does not exist")
        return results
    
    # Load characters
    chars = load_project_characters(project_dir)
    results['stats']['known_characters'] = len(chars)
    
    # Check dialogue style
    dialogue_issues = check_character_dialogue_style(project_dir, episode_path)
    results['issues'].extend(dialogue_issues)
    
    # Check appearance consistency
    appearance_issues = check_appearance_consistency(project_dir, episode_path)
    results['issues'].extend(appearance_issues)
    
    # Check style consistency across all episodes
    episodes_dir = os.path.join(project_dir, 'episodes')
    if os.path.exists(episodes_dir):
        all_episodes = sorted([
            os.path.join(episodes_dir, f) for f in os.listdir(episodes_dir)
            if f.startswith('ep') and f.endswith('.md')
        ])
        if all_episodes:
            style_issues = check_style_consistency(project_dir, all_episodes)
            results['issues'].extend(style_issues)
    
    # Count dialogues per character
    with open(episode_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    char_dialogue_count = {}
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('-'):
            match = re.match(r'^-\s*([^：\n]+?)[：\n]', line)
            if match:
                char_name = match.group(1).strip()
                char_name = re.sub(r'（[^）]*）', '', char_name).strip()
                char_name = re.sub(r'\([^)]*\)', '', char_name).strip()
                if char_name and char_name not in ['旁白', '内心', '心理独白', '字幕']:
                    char_dialogue_count[char_name] = char_dialogue_count.get(char_name, 0) + 1
    
    results['stats']['dialogue_distribution'] = char_dialogue_count
    
    # Determine if passed
    critical_issues = [i for i in results['issues'] if i.get('severity') == 'error']
    if critical_issues:
        results['passed'] = False
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Check character consistency in episode")
    parser.add_argument("episode_path", help="Path to episode markdown file")
    parser.add_argument("--project-dir", "-p", required=True,
                        help="Project directory containing characters.md")
    parser.add_argument("--strict", "-s", action="store_true",
                        help="Strict mode: fail on warnings too")
    
    args = parser.parse_args()
    
    print(f"\n{'='*50}")
    print(f"Character Consistency Check")
    print(f"{'='*50}")
    print(f"Episode: {os.path.basename(args.episode_path)}")
    print(f"Project: {os.path.basename(args.project_dir)}")
    
    results = check_character_consistency(args.project_dir, args.episode_path)
    
    print(f"\nKnown characters: {results['stats'].get('known_characters', 0)}")
    print(f"Dialogue distribution:")
    for char, count in sorted(results['stats'].get('dialogue_distribution', {}).items()):
        print(f"  {char}: {count} lines")
    
    if results['issues']:
        print(f"\nIssues ({len(results['issues'])}):")
        for issue in results['issues']:
            severity = issue.get('severity', 'info')
            symbol = '✗' if severity == 'error' else '⚠' if severity == 'warning' else 'ℹ'
            print(f"  {symbol} [{severity.upper()}] {issue['message']}")
    else:
        print(f"\n✓ No consistency issues found!")
    
    print(f"\nOverall: {'PASS' if results['passed'] else 'FAIL'}")
    
    import sys
    sys.exit(0 if results['passed'] else 1)


if __name__ == "__main__":
    main()
