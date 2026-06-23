import argparse
#!/usr/bin/env python3
"""
Comic Script Generator - Episode Validation Script
Validates episode files for quality and consistency.
"""

import os
import re
import json
import sys


def count_scenes(episode_path: str) -> int:
    """Count the number of Scene headers in an episode file."""
    with open(episode_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return len(re.findall(r'^## Scene \d+', content, re.MULTILINE))


def extract_dialogues(episode_path: str) -> list:
    """Extract all dialogue lines from an episode."""
    with open(episode_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    dialogues = []
    for line in content.split('\n'):
        if line.strip().startswith('-') and '：' in line:
            dialogues.append(line.strip())
    return dialogues


def check_ai_prompts(episode_path: str) -> tuple:
    """Check if each scene has an AI prompt section.
    
    Returns:
        (has_prompts, missing_scene_numbers)
    """
    with open(episode_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split at Scene headers; first element is title/header, skip it
    scenes = re.split(r'^## Scene \d+', content, flags=re.MULTILINE)
    scenes = [s for s in scenes if s.strip()]
    # Skip index 0 (it's the title/header before the first Scene)
    scene_blocks = scenes[1:] if len(scenes) > 1 else scenes
    
    missing = []
    for i, scene in enumerate(scene_blocks, 1):
        if '**AI 提示词**' not in scene and 'AI 提示词' not in scene:
            missing.append(i)
    
    return len(missing) == 0, missing


def check_foreshadowing_consistency(project_dir: str, episode_num: int) -> list:
    """Check if foreshadowing entries are properly tracked."""
    fs_path = os.path.join(project_dir, "foreshadowing.md")
    if not os.path.exists(fs_path):
        return []
    
    with open(fs_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    # Check for unchecked items that mention this episode
    unchecked = re.findall(r'- \[ \] .*?（第(\d+)集埋下）', content)
    for match in re.finditer(r'- \[ \] (.+?)（第(\d+)集埋下）', content):
        desc = match.group(1)
        buried_ep = int(match.group(2))
        if buried_ep <= episode_num and buried_ep < episode_num - 2:
            issues.append(f"Long-unrecovered foreshadowing: {desc} (buried ep{buried_ep:03d})")
    
    return issues


def validate_episode(episode_path: str, project_dir: str, expected_mode: str,
                     min_scenes: int, max_scenes: int) -> dict:
    """Run all validation checks on an episode file."""
    
    results = {
        "file": os.path.basename(episode_path),
        "passed": True,
        "issues": [],
        "stats": {}
    }
    
    if not os.path.exists(episode_path):
        results["passed"] = False
        results["issues"].append("File does not exist")
        return results
    
    # Scene count check
    scene_count = count_scenes(episode_path)
    results["stats"]["scenes"] = scene_count
    
    if scene_count < min_scenes:
        results["passed"] = False
        results["issues"].append(f"Too few scenes: {scene_count} (expected >= {min_scenes})")
    elif scene_count > max_scenes:
        results["issues"].append(f"More scenes than expected: {scene_count} (expected <= {max_scenes})")
    
    # AI prompts check
    has_prompts, missing = check_ai_prompts(episode_path)
    if not has_prompts:
        results["passed"] = False
        results["issues"].append(f"Missing AI prompts in scenes: {missing}")
    results["stats"]["ai_prompts"] = has_prompts
    
    # Dialogue extraction
    dialogues = extract_dialogues(episode_path)
    results["stats"]["dialogues"] = len(dialogues)
    
    # Foreshadowing consistency
    episode_num = int(re.search(r'ep(\d+)', os.path.basename(episode_path)).group(1))
    fs_issues = check_foreshadowing_consistency(project_dir, episode_num)
    if fs_issues:
        results["issues"].extend(fs_issues)
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Validate comic script episode")
    parser.add_argument("episode_path", help="Path to episode markdown file")
    parser.add_argument("--project-dir", "-p", required=True,
                        help="Project directory containing config.json and foreshadowing.md")
    parser.add_argument("--mode", "-m", choices=["A", "B", "C"], default="B",
                        help="Density mode for scene count validation")
    parser.add_argument("--strict", "-s", action="store_true",
                        help="Strict mode: fail on warnings too")
    
    args = parser.parse_args()
    
    # Load project config
    config_path = os.path.join(args.project_dir, "config.json")
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        mode = config.get("density_mode", args.mode)
    else:
        mode = args.mode
    
    # Set scene count ranges based on mode
    mode_ranges = {
        "A": (25, 45),
        "B": (40, 70),
        "C": (140, 260)
    }
    min_scenes, max_scenes = mode_ranges.get(mode, (40, 70))
    
    results = validate_episode(
        args.episode_path,
        args.project_dir,
        mode,
        min_scenes,
        max_scenes
    )
    
    # Print results
    print(f"\n{'='*50}")
    print(f"Validation: {results['file']}")
    print(f"{'='*50}")
    print(f"Mode: {mode} (expected {min_scenes}-{max_scenes} scenes)")
    print(f"Scenes: {results['stats'].get('scenes', 'N/A')}")
    print(f"Dialogues: {results['stats'].get('dialogues', 'N/A')}")
    print(f"AI Prompts: {'✓' if results['stats'].get('ai_prompts') else '✗'}")
    
    if results["issues"]:
        print(f"\nIssues ({len(results['issues'])}):")
        for issue in results["issues"]:
            print(f"  ✗ {issue}")
    else:
        print(f"\n✓ All checks passed!")
    
    print(f"\nOverall: {'PASS' if results['passed'] else 'FAIL'}")
    
    sys.exit(0 if results["passed"] else 1)


if __name__ == "__main__":
    main()
