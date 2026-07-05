#!/usr/bin/env python3
"""
Comic Script Generator - Character Consistency Checker
Validates character descriptions, dialogue names, and style guide usage.
"""

import os
import re
import argparse

SKIP_DIALOGUE_PREFIXES = ('- `', '- 旁白框', '- [', '- 总', '- 验证状态')
SKIP_DIALOGUE_NAMES = {'旁白', '内心', '心理独白', '字幕', '旁白框', '总 Panel 数', '总对话数', '验证状态'}


def extract_dialogue_speaker(line: str):
    """Return speaker name for real dialogue bubble lines, or None for SFX/stats/captions."""
    stripped = line.strip()
    if not stripped.startswith('-'):
        return None
    if stripped.startswith(SKIP_DIALOGUE_PREFIXES):
        return None
    match = re.match(r'^-\s*([^：\n]+)[：]', stripped)
    if not match:
        return None
    name = match.group(1).strip()
    name = re.sub(r'（[^）]*）', '', name).strip()
    name = re.sub(r'\([^)]*\)', '', name).strip()
    if not name or name in SKIP_DIALOGUE_NAMES:
        return None
    return name


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
            match = re.match(r'^- \*\*([^*]+)\*\*[：:]\s*(.+)$', line)
            if match:
                field = match.group(1).strip()
                value = match.group(2).strip()
                if field == '外貌':
                    characters[current_char]['appearance'] = value
                elif field == '性格':
                    characters[current_char]['personality'] = value
                characters[current_char]['profile'] += field + ': ' + value + '\n'
    return characters


def dialogue_distribution(episode_path: str) -> dict:
    with open(episode_path, 'r', encoding='utf-8') as f:
        content = f.read()
    counts = {}
    for line in content.split('\n'):
        speaker = extract_dialogue_speaker(line)
        if speaker:
            counts[speaker] = counts.get(speaker, 0) + 1
    return counts


def check_character_dialogue_style(project_dir: str, episode_path: str) -> list:
    known_names = set(load_project_characters(project_dir).keys())
    counts = dialogue_distribution(episode_path)
    unknown = set(counts) - known_names
    issues = []
    if unknown:
        issues.append({
            'type': 'unknown_character_dialogue',
            'message': '发现未记录的角色: ' + ', '.join(sorted(unknown)),
            'severity': 'warning'
        })
    return issues


def check_appearance_consistency(project_dir: str, episode_path: str) -> list:
    # Placeholder for future semantic checks. Keep non-destructive and deterministic.
    return []


def check_style_consistency(project_dir: str, episodes: list) -> list:
    issues = []
    guide_path = os.path.join(project_dir, 'style_guide.md')
    if not os.path.exists(guide_path):
        issues.append({'type': 'missing_style_guide', 'message': 'style_guide.md not found - run init_project.py', 'severity': 'error'})
        return issues
    with open(guide_path, 'r', encoding='utf-8') as f:
        guide_content = f.read()
    positive_match = re.search(r'## 正向提示词\s*\n(.+?)(?:\n##|$)', guide_content, re.DOTALL)
    negative_match = re.search(r'## 反向提示词\s*\n(.+?)(?:\n##|$)', guide_content, re.DOTALL)
    if not positive_match or not negative_match:
        issues.append({'type': 'invalid_style_guide', 'message': 'style_guide.md format invalid', 'severity': 'error'})
        return issues
    key_terms = [t.strip() for t in positive_match.group(1).split(',')[:3] if t.strip()]
    if not key_terms:
        return issues
    for ep_path in episodes:
        if not os.path.exists(ep_path):
            continue
        with open(ep_path, 'r', encoding='utf-8') as f:
            ep_content = f.read()
        panel_matches = list(re.finditer(r'^### Panel \d+', ep_content, flags=re.MULTILINE))
        missing = []
        for idx, match in enumerate(panel_matches):
            start = match.end()
            end = panel_matches[idx + 1].start() if idx + 1 < len(panel_matches) else len(ep_content)
            block = ep_content[start:end]
            if not any(term.lower() in block.lower() for term in key_terms):
                missing.append(idx + 1)
        if missing:
            issues.append({
                'type': 'style_mismatch',
                'message': os.path.basename(ep_path) + ': ' + str(len(missing)) + ' panels missing style keywords',
                'severity': 'warning',
                'details': missing[:5]
            })
    return issues


def check_character_consistency(project_dir: str, episode_path: str) -> dict:
    results = {
        'file': os.path.basename(episode_path),
        'passed': True,
        'issues': [],
        'stats': {}
    }
    if not os.path.exists(episode_path):
        results['passed'] = False
        results['issues'].append('File does not exist')
        return results
    chars = load_project_characters(project_dir)
    results['stats']['known_characters'] = len(chars)
    results['issues'].extend(check_character_dialogue_style(project_dir, episode_path))
    results['issues'].extend(check_appearance_consistency(project_dir, episode_path))
    episodes_dir = os.path.join(project_dir, 'episodes')
    if os.path.exists(episodes_dir):
        all_episodes = sorted(os.path.join(episodes_dir, f) for f in os.listdir(episodes_dir) if f.startswith('ep') and f.endswith('.md'))
        if all_episodes:
            results['issues'].extend(check_style_consistency(project_dir, all_episodes))
    results['stats']['dialogue_distribution'] = dialogue_distribution(episode_path)
    critical = [i for i in results['issues'] if isinstance(i, dict) and i.get('severity') == 'error']
    if critical:
        results['passed'] = False
    return results


def main():
    parser = argparse.ArgumentParser(description='Check character consistency in episode')
    parser.add_argument('episode_path', help='Path to episode markdown file')
    parser.add_argument('--project-dir', '-p', required=True, help='Project directory containing characters.md')
    parser.add_argument('--strict', '-s', action='store_true', help='Strict mode: fail on warnings too')
    args = parser.parse_args()

    results = check_character_consistency(args.project_dir, args.episode_path)
    print('\n' + '=' * 50)
    print('Character Consistency Check')
    print('=' * 50)
    print('Episode:', os.path.basename(args.episode_path))
    print('Project:', os.path.basename(args.project_dir))
    print('\nKnown characters:', results['stats'].get('known_characters', 0))
    dist = results['stats'].get('dialogue_distribution', {})
    if dist:
        print('Dialogue distribution:')
        for char, count in sorted(dist.items()):
            print('  ' + char + ': ' + str(count) + ' lines')
    if results['issues']:
        print('\nIssues:')
        for issue in results['issues']:
            if isinstance(issue, dict):
                print('  [' + issue.get('severity', 'info').upper() + '] ' + issue.get('message', str(issue)))
            else:
                print('  ' + str(issue))
    else:
        print('\n✓ No consistency issues found!')
    print('\nOverall:', 'PASS' if results['passed'] else 'FAIL')
    if not results['passed'] or (args.strict and results['issues']):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
