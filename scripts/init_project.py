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
                   total_episodes: int = 6, art_style: str = "", language: str = "zh-CN",
                   source: str = "local", source_config: dict = None):
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
        "source": source,
        "source_config": source_config or {},
        "characters": [],
        "foreshadowing_active": [],
        "notes": ""
    }
    
    config_path = os.path.join(project_dir, "config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    # Create empty markdown files
    files = {
        "summary.md": "# " + project_name + " - 项目摘要\n",
        "characters.md": "# " + project_name + " - 角色档案\n",
        "foreshadowing.md": "# " + project_name + " - 伏笔追踪\n\n## 未回收\n- [ ] \n\n## 已回收\n"
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
    parser.add_argument("--source", "-s", default="local", choices=["local", "api"],
                        help="Script source: local file or online API")
    parser.add_argument("--api-url", default="",
                        help="API URL (required when source=api)")
    parser.add_argument("--api-key", default="",
                        help="API key (required when source=api)")
    
    args = parser.parse_args()
    
    source_config = {}
    if args.source == "api":
        if not args.api_url or not args.api_key:
            print("Error: --api-url and --api-key are required when --source=api")
            sys.exit(1)
        source_config = {
            "mode": "api",
            "api_url": args.api_url,
            "api_key": args.api_key,
            "method": "POST",
            "params": {},
            "headers": {
                "Authorization": f"Bearer {args.api_key}",
                "Content-Type": "application/json"
            },
            "response_path": "data.content",
            "cache_enabled": True,
            "cache_ttl": 3600
        }

    project_dir = create_project(
        project_name=args.project_name,
        output_dir=args.output,
        density_mode=args.mode,
        total_episodes=args.episodes,
        art_style=args.art_style,
        language=args.language,
        source=args.source,
        source_config=source_config
    )
    
    print(f"\nNext step: Provide your story outline to start generating episodes.")


if __name__ == "__main__":
    main()
