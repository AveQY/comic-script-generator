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


# Prose style presets / 文笔风格预设
PROSE_STYLE_PRESETS = {
    "张嘉佳": {
        "name": "张嘉佳",
        "description": "温暖中带涩，意象密集，短句节奏，善于写中年人的柔软与钝感。物象承载情感，冷色调比喻，自嘲式短句。代表作《从你的全世界路过》《云边有个小卖部》。",
        "prompt_suffix": "文笔风格：张嘉佳。用具体的物象承载情感，避免直接抒情；用短句节奏，像有人在你耳边说；保持温暖中带涩的底色；写中年人的柔软与钝感；比喻要新鲜、冷冽、不落俗套；避免朋友圈金句感，要接近纯文学质感。"
    },
    "余华": {
        "name": "余华",
        "description": "冷静克制，白描手法，苦难中见人性。语言极简，情绪收在骨头里。代表作《活着》《许三观卖血记》。",
        "prompt_suffix": "文笔风格：余华。用极简的白描手法，冷静克制地叙述；苦难中见人性，但不煽情；语言要像刀一样锋利又克制；情绪收在骨头里，不直接抒情。"
    },
    "村上春树": {
        "name": "村上春树",
        "description": "疏离感，平行叙事，超现实细节，音乐与美食意象。第一人称内省，孤独但温暖。代表作《挪威的森林》《海边的卡夫卡》。",
        "prompt_suffix": "文笔风格：村上春树。保持适度的疏离感和平行叙事；加入超现实的细节；多用音乐、美食意象；第一人称内省式叙述；孤独但温暖的基调；比喻要独特、不落俗套。"
    },
    "东野圭吾": {
        "name": "东野圭吾",
        "description": "悬疑推理，层层剥茧，人性反转，社会议题。对话推动剧情，节奏紧凑。代表作《白夜行》《解忧杂货店》。",
        "prompt_suffix": "文笔风格：东野圭吾。悬疑推理风格，层层剥茧；对话推动剧情，节奏紧凑；注重人性反转和社会议题；保持紧张感，但留有余温。"
    },
    "汪曾祺": {
        "name": "汪曾祺",
        "description": "淡而有味，市井烟火，草木皆情。语言清新，节奏舒缓，善于写日常中的诗意。代表作《受戒》《大淖记事》。",
        "prompt_suffix": "文笔风格：汪曾祺。淡而有味，市井烟火气；草木皆情，善于写日常中的诗意；语言清新自然，节奏舒缓；避免刻意煽情，让情感自然流露。"
    },
    "严歌苓": {
        "name": "严歌苓",
        "description": "女性视角细腻，历史与个人交织，语言华丽有质感。善于写大时代下的小人物命运。代表作《芳华》《金陵十三钗》。",
        "prompt_suffix": "文笔风格：严歌苓。女性视角细腻敏感；历史与个人命运交织；语言华丽有质感；善于写大时代下的小人物；注意时代细节的准确性。"
    },
    "王小波": {
        "name": "王小波",
        "description": "荒诞幽默，黑色讽刺，性张力，自由精神。语言跳跃，思维发散，反讽与诗意并存。代表作《黄金时代》《沉默的大多数》。",
        "prompt_suffix": "文笔风格：王小波。荒诞幽默，黑色讽刺；语言跳跃，思维发散；反讽与诗意并存；保持自由精神；不回避敏感话题但要用巧思。"
    },
    "亦舒": {
        "name": "亦舒",
        "description": "都市女性，犀利毒舌，简洁冷峻，独立清醒。对话机智，节奏快，善于写职场与情感。代表作《喜宝》《我的前半生》。",
        "prompt_suffix": "文笔风格：亦舒。都市女性视角，犀利毒舌；语言简洁冷峻；人物独立清醒；对话机智；节奏快；善于写职场与情感中的清醒与克制。"
    },
    "江南": {
        "name": "江南",
        "description": "宏大世界观，少年热血，细腻情感，史诗感。语言华丽，描写宏大场景与细腻内心并存。代表作《龙族》《九州缥缈录》。",
        "prompt_suffix": "文笔风格：江南。宏大世界观，少年热血；细腻情感与史诗感并存；语言华丽，描写宏大场景与细腻内心；保持少年感与宿命感。"
    },
    "马伯庸": {
        "name": "马伯庸",
        "description": "历史悬疑，考据详实，脑洞大开，职场权谋。语言幽默，节奏快，善于写小人物的历史现场。代表作《长安十二时辰》《古董局中局》。",
        "prompt_suffix": "文笔风格：马伯庸。历史悬疑，考据详实；脑洞大开，职场权谋；语言幽默，节奏快；善于写小人物的历史现场；细节真实可信。"
    },
    "丁墨": {
        "name": "丁墨",
        "description": "甜宠推理，高智商男主，强女主，悬疑+恋爱双线。语言轻松，节奏明快，善于写高智商博弈与甜蜜互动。代表作《他来了，请闭眼》《美人为馅》。",
        "prompt_suffix": "文笔风格：丁墨。甜宠推理风格，高智商男主+强女主；悬疑与恋爱双线并行；语言轻松，节奏明快；善于写高智商博弈与甜蜜互动。"
    },
    "Priest": {
        "name": "Priest",
        "description": "耽美/奇幻，世界观宏大，人物鲜活，幽默与热血并存。语言老练，节奏掌控力强。代表作《默读》《杀破狼》《镇魂》。",
        "prompt_suffix": "文笔风格：Priest。世界观宏大，人物鲜活；幽默与热血并存；语言老练，节奏掌控力强；善于写群像和复杂关系；保持故事的张力与深度。"
    },
    "沧月": {
        "name": "沧月",
        "description": "奇幻武侠，空灵唯美，悲剧感，江湖与宿命。语言华丽，意境深远，善于写武侠中的爱恨情仇。代表作《镜》《听雪楼》。",
        "prompt_suffix": "文笔风格：沧月。奇幻武侠，空灵唯美；悲剧感，江湖与宿命；语言华丽，意境深远；善于写武侠中的爱恨情仇与家国天下。"
    },
    "笛安": {
        "name": "笛安",
        "description": "青春疼痛，细腻敏感，家族与成长，语言有诗意。善于写青春期的困惑与家庭关系。代表作《西决》《东霓》《南音》。",
        "prompt_suffix": "文笔风格：笛安。青春疼痛，细腻敏感；家族与成长主题；语言有诗意；善于写青春期的困惑与家庭关系；保持真诚与脆弱感。"
    },
    "七堇年": {
        "name": "七堇年",
        "description": "青春文学，私语化，自我探索，语言干净清澈。善于写成长中的孤独与寻找。代表作《被窝是青春的坟墓》《澜本嫁衣》。",
        "prompt_suffix": "文笔风格：七堇年。青春文学，私语化；自我探索，语言干净清澈；善于写成长中的孤独与寻找；保持真诚的青春感，避免矫情。"
    },
    "沈石溪": {
        "name": "沈石溪",
        "description": "动物小说，拟人化，自然观察，生存与情感。语言生动，细节真实，善于写动物世界的人性。代表作《狼王梦》《第七条猎狗》。",
        "prompt_suffix": "文笔风格：沈石溪。动物小说视角，拟人化但不失真实；自然观察，生存与情感；语言生动，细节真实；善于写动物世界的人性光辉。"
    }
}


def resolve_prose_style(prose_style):
    """Resolve prose_style from preset key, list of keys, or custom description.
    Returns (resolved_style, preset_keys_list_or_None)
    """
    if not prose_style:
        return "", []
    
    if isinstance(prose_style, list):
        resolved = []
        for key in prose_style:
            if key in PROSE_STYLE_PRESETS:
                resolved.append(PROSE_STYLE_PRESETS[key]["prompt_suffix"])
            else:
                resolved.append(str(key))
        return "\n\n".join(resolved), prose_style
    
    if isinstance(prose_style, str):
        if prose_style in PROSE_STYLE_PRESETS:
            return PROSE_STYLE_PRESETS[prose_style]["prompt_suffix"], [prose_style]
        return prose_style, [prose_style]
    
    return "", []


def format_prose_style_display(prose_style):
    """Format prose_style for display in config.json."""
    if not prose_style:
        return ""
    if isinstance(prose_style, list):
        return ", ".join(prose_style)
    return str(prose_style)


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
                   prose_style: str = "", source: str = "local", source_config: dict = None):
    """Create a new comic project with full directory structure."""
    
    project_dir = os.path.join(output_dir, "projects", project_name)
    episodes_dir = os.path.join(project_dir, "episodes")
    
    # Create directories
    os.makedirs(episodes_dir, exist_ok=True)
    
    # Resolve art_style from preset or custom
    resolved_style, preset_key = resolve_art_style(art_style)
    
    # Resolve prose_style
    prose_resolved, prose_presets = resolve_prose_style(prose_style)
    
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
        "script_unit": "page_panel",
        "last_panel_count": 0,
        "status": "planning",
        "source": source,
        "source_config": source_config or {},
        "characters": [],
        "foreshadowing_active": [],
        "notes": "",
        "prose_style": format_prose_style_display(prose_style) if prose_style else "",
        "prose_style_presets": prose_presets
    }
    
    config_path = os.path.join(project_dir, "config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    # Create prose_style_guide.md if prose_style is set
    if prose_resolved:
        prose_guide_path = os.path.join(project_dir, "prose_style_guide.md")
        with open(prose_guide_path, 'w', encoding='utf-8') as f:
            f.write(f"# 文笔风格指南\n\n{prose_resolved}\n")
    
    # Create style_guide.md
    guide_path = create_style_guide(project_dir, resolved_style)
    
    # Create empty markdown files
    files = {
        "summary.md": "# " + project_name + " - 项目摘要\n",
        "characters.md": "# " + project_name + " - 角色档案\n",
        "foreshadowing.md": "# " + project_name + " - 伏笔追踪\n\n## 未回收\n\n## 已回收\n"
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
    parser.add_argument("--prose-style", default="",
                        help="Prose writing style: single key (e.g. 张嘉佳) or comma-separated list (e.g. 张嘉佳,余华)")
    
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

    prose_style = args.prose_style
    # Parse comma-separated into list
    if prose_style and "," in prose_style:
        prose_style = [s.strip() for s in prose_style.split(",") if s.strip()]

    project_dir = create_project(
        project_name=args.project_name,
        output_dir=args.output,
        density_mode=args.mode,
        total_episodes=args.episodes,
        art_style=args.art_style,
        prose_style=prose_style,
        language=args.language,
        source=args.source,
        source_config=source_config
    )
    
    print(f"\nNext step: Provide your story outline to start generating episodes.")


if __name__ == "__main__":
    main()
