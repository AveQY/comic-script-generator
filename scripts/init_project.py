#!/usr/bin/env python3
"""
Comic Script Generator - Project Initialization Script
Creates project skeleton with all required files and directories.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone, timedelta


def create_project(project_name: str, output_dir: str, density_mode: str = "B",
                   total_episodes: int = 6, art_style: str = "", language: str = "zh-CN"):
    """Create a new comic project with full directory structure."""
    
    project_dir = os.path.join(output_dir, "projects", project_name)
    episodes_dir = os.path.join(project_dir, "episodes")
    
    # Create directories
    os.makedirs(episodes_dir, exist_ok=True)
    
    # Create config.json
    config = {
        "project_name": project_name,
        "created_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "updated_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "density_mode": density_mode,
        "art_style": art_style,
        "language": language,
        "total_episodes": total_episodes,
        "current_episode": 0,
        "episodes_planned": total_episodes,
        "status": "planning",
        "source": "outline",
        "characters": [],
        "foreshadowing_active": [],
        "notes": ""
    }
    
    config_path = os.path.join(project_dir, "config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    # Create empty markdown files
    files = {
        "summary.md": f"# {project_name} - 项目摘要

## 第1集：
- **主要情节**：
- **关键转折**：
- **新增角色**：
- **伏笔**：
",
        "characters.md": f"# {project_name} - 角色档案

## 
- **全名**：
- **年龄**：
- **外貌**：
- **性格**：
- **背景**：
- **首次登场**：第1集
- **关键情节**：
",
        "foreshadowing.md": f"# {project_name} - 伏笔追踪

## 未回收
- [ ] 

## 已回收
"
    }
    
    for filename, content in files.items():
        filepath = os.path.join(project_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f"✓ Project created: {project_dir}")
    print(f"  Density mode: {density_mode}")
    print(f"  Total episodes: {total_episodes}")
    print(f"  Art style: {art_style or '(default)'}")
    print(f"  Language: {language}")
    print(f"\n  Files created:")
    print(f"    config.json")
    print(f"    summary.md")
    print(f"    characters.md")
    print(f"    foreshadowing.md")
    print(f"    episodes/ (empty)")
    
    return project_dir


def main():
    parser = argparse.ArgumentParser(description="Initialize a comic script generator project")
    parser.add_argument("project_name", help="Project name (used as directory name)")
    parser.add_argument("--output", "-o", default=os.path.expanduser("~/comic-projects"),
                        help="Output directory (default: ~/comic-projects)")
    parser.add_argument("--mode", "-m", choices=["A", "B", "C"], default="B",
                        help="Density mode: A=dialogue-heavy, B=balanced, C=film-style (default: B)")
    parser.add_argument("--episodes", "-e", type=int, default=6,
                        help="Total episodes planned (default: 6)")
    parser.add_argument("--art-style", "-a", default="",
                        help="Art style description for AI prompts")
    parser.add_argument("--language", "-l", default="zh-CN",
                        help="Script language (default: zh-CN)")
    
    args = parser.parse_args()
    
    project_dir = create_project(
        project_name=args.project_name,
        output_dir=args.output,
        density_mode=args.mode,
        total_episodes=args.episodes,
        art_style=args.art_style,
        language=args.language
    )
    
    print(f"\nNext step: Provide your story outline to start generating episodes.")


if __name__ == "__main__":
    main()
