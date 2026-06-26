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

# Art style presets / 艺术风格预设
STYLE_PRESETS = {
    "japanese-modern": {
        "name_zh": "现代日漫风",
        "name_en": "Japanese Modern Manga",
        "positive": "masterpiece, best quality, modern manga style, bold lines, screentone, dynamic angles, sharp details, anime aesthetic",
        "negative": "worst quality, low quality, blurry, deformed, bad anatomy, extra limbs, watermark, text, signature, photorealistic",
        "description": "现代日漫风（少年/Jump 风，浓线条，网点纸，动态视角）"
    },
    "chinese-fine": {
        "name_zh": "国风细笔画",
        "name_en": "Chinese Fine Brush",
        "positive": "masterpiece, best quality, Chinese fine brush painting, ink wash, flowing lines, elegant composition, negative space, traditional aesthetics",
        "negative": "worst quality, low quality, blurry, deformed, bad anatomy, extra limbs, watermark, text, signature, modern digital art",
        "description": "国风细笔画（古风，水墨，留白，优雅构图）"
    },
    "western-comic": {
        "name_zh": "美漫超级英雄风",
        "name_en": "Western Superhero Comic",
        "positive": "masterpiece, best quality, western comic book style, superhero, bold outlines, high contrast, hard shadows, muscular figure, dynamic pose, comic book art",
        "negative": "worst quality, low quality, blurry, deformed, bad anatomy, extra limbs, watermark, text, signature, soft lighting, watercolor",
        "description": "美漫超级英雄风（粗线条，高对比，硬边阴影，动态姿势）"
    },
    "ghibli": {
        "name_zh": "吉卜力手绘水彩",
        "name_en": "Ghibli Hand-drawn Watercolor",
        "positive": "masterpiece, best quality, Ghibli style, hand-drawn watercolor, soft lighting, natural scenery, healing atmosphere, detailed backgrounds, lush nature",
        "negative": "worst quality, low quality, blurry, deformed, bad anatomy, extra limbs, watermark, text, signature, dark, horror, cyberpunk",
        "description": "吉卜力手绘水彩（柔和光线，自然场景，治愈系，细腻背景）"
    },
    "pixel-retro": {
        "name_zh": "像素复古风",
        "name_en": "Pixel Retro",
        "positive": "masterpiece, best quality, pixel art, 8-bit, 16-bit, retro game style, low resolution, pixelated, nostalgic, game sprite, arcade aesthetic",
        "negative": "worst quality, low quality, blurry, deformed, bad anatomy, extra limbs, watermark, text, signature, photorealistic, 3d render, smooth",
        "description": "像素复古风（8-bit，低分辨率，游戏感，怀旧）"
    }
}


def resolve_art_style(art_style: str):
    """Resolve art_style from preset key or custom description.
    Returns (resolved_style, preset_key_or_None)
    """
    if not art_style:
        preset = STYLE_PRESETS["japanese-modern"]
        return preset["positive"], "japanese-modern"
    
    if art_style in STYLE_PRESETS:
        preset = STYLE_PRESETS[art_style]
        return preset["positive"], art_style
    
    return art_style, None


def create_style_guide(project_dir: str, art_style: str):
    """Create style_guide.md in project directory."""
    positive, preset_key = resolve_art_style(art_style)
    
    if preset_key and preset_key in STYLE_PRESETS:
        negative = STYLE_PRESETS[preset_key]["negative"]
        description = STYLE_PRESETS[preset_key]["description"]
    else:
        negative = "worst quality, low quality, blurry, deformed, bad anatomy, extra limbs, watermark, text, signature"
        description = art_style or "japanese-modern"
    
    content = "# 风格指南\n\n## 正向提示词\n" + positive + "\n\n## 反向提示词\n" + negative + "\n\n## 风格说明\n" + description + "\n"
    
    guide_path = os.path.join(project_dir, "style_guide.md")
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return guide_path


def create_project(project_name: str, output_dir: str, density_mode: str = "B",
                   total_episodes: int = 6, art_style: str = "", language: str = "zh-CN",
                   source: str = "local", source_config: dict = None):
    """Create a new comic project with full directory structure."""
    
    project_dir = os.path.join(output_dir, "projects", project_name)
    episodes_dir = os.path.join(project_dir, "episodes")
    
    # Create directories
    os.makedirs(episodes_dir, exist_ok=True)
    
    # Resolve art_style from preset or custom
    resolved_style, preset_key = resolve_art_style(art_style)
    
    # Create config.json
    config = {
        "project_name": project_name,
        "created_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "updated_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "density_mode": density_mode,
        "art_style": resolved_style,
        "art_style_preset": preset_key,
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
    
    # Create style_guide.md
    guide_path = create_style_guide(project_dir, resolved_style)
    
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
    
    preset_display = preset_key if preset_key else "custom"
    print(f"✓ Project created: {project_dir}")
    print(f"  Density mode: {density_mode}")
    print(f"  Total episodes: {total_episodes}")
    print(f"  Art style preset: {preset_display}")
    print(f"  Language: {language}")
    print(f"\n  Files created:")
    print(f"    config.json")
    print(f"    summary.md")
    print(f"    characters.md")
    print(f"    foreshadowing.md")
    print(f"    style_guide.md")
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
    parser.add_argument("--art-style", "-a", default="japanese-modern",
                        help="Art style: preset key (japanese-modern/chinese-fine/western-comic/ghibli/pixel-retro) or custom description")
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
