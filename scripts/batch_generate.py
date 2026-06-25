#!/usr/bin/env python3
"""
Comic Script Generator - Batch Generation Script
Automatically generates multiple independent comic projects from hot topics.
"""

import os
import sys
import json
import time
import random
import argparse
import subprocess
import urllib.request
import urllib.error
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path


# ─── Configuration ───────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_OUTPUT = os.path.expanduser("~/comic-projects")
DEFAULT_EPISODES = 5

# Hermes config location
HERMES_CONFIG = Path.home() / "AppData" / "Local" / "hermes" / "config.yaml"

# Baidu hot topics
BAIDU_URL = "https://top.baidu.com/board?tab=realtime"

# Topics excluded from batch generation
EXCLUDED_KEYWORDS = [
    "疫情", "死亡", "杀害", "爆炸", "袭击", "地震", "洪水", "火灾",
    "自杀", "暴力", "恐怖", "战争", "时政", "政治", "敏感"
]


# ─── Hot Topic Fetching ──────────────────────────────────────────────────────

def fetch_baidu_hotspots() -> list:
    """Fetch hot topics from Baidu real-time board."""
    try:
        req = urllib.request.Request(BAIDU_URL, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "zh-CN,zh;q=0.9",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        topics = []

        # Baidu hot board: extract from JSON data in page
        pattern = re.compile(r'"word":"([^"]{4,50})"')
        matches = pattern.findall(html)

        if not matches:
            # Fallback: extract from h2 tags
            pattern2 = re.compile(r'<h2[^>]*>([^<]{4,50})</h2>')
            matches = pattern2.findall(html)

        # Deduplicate while preserving order
        seen = set()
        for m in matches:
            title = m.strip()
            if title and title not in seen:
                seen.add(title)
                topics.append(title)

        return topics[:50]

    except Exception as e:
        print(f"[WARN] Failed to fetch Baidu hotspots: {e}")
        return []


def filter_suitable_topics(topics: list) -> list:
    """Filter topics suitable for comic creation."""
    suitable = []
    for topic in topics:
        excluded = False
        for kw in EXCLUDED_KEYWORDS:
            if kw in topic:
                excluded = True
                break
        if not excluded and len(topic.strip()) >= 4:
            suitable.append(topic)
    return suitable


# ─── LLM API ─────────────────────────────────────────────────────────────────

def get_hermes_api_config() -> dict:
    """Read Hermes config to get LLM API settings."""
    try:
        with open(HERMES_CONFIG, "r", encoding="utf-8") as f:
            content = f.read()
        config = {}
        for line in content.split("\n"):
            line = line.strip()
            if ":" in line and not line.startswith("#"):
                key, _, val = line.partition(":")
                config[key.strip()] = val.strip().strip('"').strip("'")
        return config
    except Exception:
        return {}


def call_llm(base_url: str, api_key: str, model: str, prompt: str,
             max_tokens: int = 8000) -> str:
    """Call LLM API and return response text."""
    url = f"{base_url.rstrip('/')}/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.8,
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    })

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            choices = data.get("choices", [])
            if choices:
                return choices[0]["message"]["content"]
            return ""
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="ignore")[:500]
        except Exception:
            pass
        print(f"\n[LLM HTTP {e.code}] {body}")
        return ""
    except Exception as e:
        print(f"\n[LLM Error] {e}")
        return ""


# ─── Project Initialization ──────────────────────────────────────────────────

def init_project(project_name: str, output_dir: str, mode: str, episodes: int,
                 art_style: str = "") -> str:
    """Initialize a new project using init_project.py."""
    cmd = [
        sys.executable,
        str(SCRIPT_DIR / "init_project.py"),
        project_name,
        "--output", output_dir,
        "--mode", mode,
        "--episodes", str(episodes),
    ]
    if art_style:
        cmd.extend(["--art-style", art_style])

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[ERROR] init_project failed: {r.stderr[:300]}")
        return ""
    print(r.stdout.strip())
    return os.path.join(output_dir, "projects", project_name)


# ─── Episode Generation ──────────────────────────────────────────────────────

def generate_outline_and_episodes(topic: str, project_name: str, mode: str,
                                   episodes: int, art_style: str,
                                   output_dir: str) -> bool:
    """Generate story outline and episodes using LLM."""
    config = get_hermes_api_config()
    base_url = config.get("base_url", "https://cli-api.aweqy.top/v1").rstrip("/")
    api_key = config.get("api_key", "")
    model = config.get("default_model", "step-router-v1")

    if not api_key:
        print("[ERROR] No API key found in Hermes config")
        return False

    mode_desc = {
        "A": "对话多，镜头少（传统漫画风，每集30-40场景，每场景1-2个镜头+3-8段对话）",
        "B": "一个对话对应一个镜头（平衡模式，每集50-60场景）",
        "C": "一段对话多个镜头（电影短剧风，每集150-250场景，画面细节丰富）",
    }

    # Step 1: Generate outline
    outline_prompt = (
        "你是一个专业的漫画编剧。请为主题「{}」创作一个漫画故事大纲。\n\n"
        "要求：\n"
        "- 分镜密度模式：{}\n"
        "- 计划集数：{}集\n"
        "- 提供2-3个主要角色（姓名、性格、外貌、背景）\n"
        "- 提供每集的故事梗概（100-200字）\n"
        "- 设置至少2个伏笔（埋在某集，后续回收）\n"
        "- 风格：{}\n\n"
        "输出格式（Markdown）：\n"
        "# 项目名称：{}\n\n"
        "## 故事大纲\n\n"
        "### 核心设定\n[故事背景、核心冲突]\n\n"
        "### 主要角色\n[角色档案，含姓名/性格/外貌/背景]\n\n"
        "### 分集规划\n"
        "- 第1集：[标题] - [梗概]\n"
        "- ...（共{}集）\n\n"
        "### 伏笔设计\n- [伏笔1描述]（第X集埋下，第Y集回收）\n"
    ).format(topic, mode_desc.get(mode, mode_desc["B"]), episodes,
             art_style or "现代都市，写实风格", project_name, episodes)

    print(f"  Generating outline...", end=" ", flush=True)
    outline = call_llm(base_url, api_key, model, outline_prompt, max_tokens=4000)
    if not outline:
        print("FAILED")
        return False
    print(f"✓ ({len(outline)} chars)")

    project_dir = os.path.join(output_dir, "projects", project_name)
    outline_path = os.path.join(project_dir, "outline.md")
    with open(outline_path, "w", encoding="utf-8") as f:
        f.write(outline)

    # Step 2: Generate episodes
    for ep_num in range(1, episodes + 1):
        print(f"  Episode {ep_num}/{episodes}...", end=" ", flush=True)

        ep_prompt = (
            "你是漫画编剧。根据以下大纲，撰写第{}集的分镜脚本。\n\n"
            "【大纲】\n{}\n\n"
            "【要求】\n"
            "- 分镜密度模式：{}\n"
            "- 每个场景必须包含：镜头类型、画面描述、对话/旁白\n"
            "- 每个场景必须附带 AI 绘图提示词（正向+反向，适配 Midjourney/SD 格式）\n"
            "- AI提示词格式：正向用 ```markdown ... ``` 包裹，反向同样\n"
            "- 对话自然，符合角色性格\n"
            "- 画面描述具象化（颜色、光线、动作、表情）\n\n"
            "【输出格式】\n"
            "# 第{}集：[标题]\n\n"
            "**故事梗概**：[本集内容]\n"
            "**分镜模式**：{}\n"
            "**预计场景数**：X个\n\n"
            "---\n\n"
            "## Scene 1\n"
            "**镜头**：[远景/中景/特写/俯拍/仰拍/双人中景等]\n"
            "**画面**：[人物表情、动作、环境细节、光线氛围]\n"
            "**对话**：\n"
            "- [角色/旁白]：[台词]\n"
            "**AI 提示词**：\n"
            "正向：\n"
            "```\n"
            "masterpiece, best quality, [画面描述], [镜头角度], [艺术风格], cinematic lighting\n"
            "```\n"
            "反向：\n"
            "```\n"
            "worst quality, low quality, blurry, deformed, bad anatomy, extra limbs\n"
            "```\n\n"
            "---\n\n"
            "*本集完*\n\n"
            "**生成统计**：\n"
            "- 总场景数：X\n"
            "- 总对话数：X\n"
            "- 验证状态：待验证\n"
        ).format(ep_num, outline[:2000], mode_desc.get(mode, mode_desc["B"]),
                 ep_num, mode)

        ep_content = call_llm(base_url, api_key, model, ep_prompt, max_tokens=16000)
        if not ep_content:
            print("FAILED")
            return False

        # Determine episode title
        title_match = re.search(r"第\d+集[：:](.+)", ep_content)
        ep_title = title_match.group(1).strip() if title_match else f"第{ep_num}集"
        ep_title = re.sub(r'[\\/:*?"<>|]', "", ep_title).strip()
        if not ep_title:
            ep_title = f"第{ep_num}集"

        ep_filename = "ep{:03d}_{}.md".format(ep_num, ep_title[:30])
        ep_path = os.path.join(project_dir, "episodes", ep_filename)

        with open(ep_path, "w", encoding="utf-8") as f:
            f.write(ep_content)
        print("✓ ({} chars)".format(len(ep_content)))

    return True


# ─── Validation ──────────────────────────────────────────────────────────────

def run_validation(project_dir: str, episodes: int, mode: str) -> bool:
    """Run validation scripts on generated episodes."""
    validate_script = SCRIPT_DIR / "validate_episode.py"
    consistency_script = SCRIPT_DIR / "consistency_check.py"
    update_script = SCRIPT_DIR / "update_project.py"

    all_ok = True
    episodes_dir = os.path.join(project_dir, "episodes")

    for ep_num in range(1, episodes + 1):
        ep_files = [f for f in os.listdir(episodes_dir)
                    if f.startswith("ep{:03d}_".format(ep_num)) and f.endswith(".md")]
        if not ep_files:
            continue
        ep_path = os.path.join(episodes_dir, ep_files[0])

        # Validate
        r = subprocess.run(
            [sys.executable, str(validate_script), ep_path,
             "--project-dir", project_dir],
            capture_output=True, text=True
        )
        if r.returncode != 0:
            print(f"  [WARN] validate ep{ep_num}: {r.stderr[:200]}")
            all_ok = False

        # Consistency check
        r = subprocess.run(
            [sys.executable, str(consistency_script), ep_path,
             "--project-dir", project_dir],
            capture_output=True, text=True
        )
        if r.returncode != 0:
            print(f"  [WARN] consistency ep{ep_num}: {r.stderr[:200]}")

        # Update project index
        r = subprocess.run(
            [sys.executable, str(update_script), ep_path,
             "--project-dir", project_dir,
             "--episode-num", str(ep_num)],
            capture_output=True, text=True
        )
        if r.returncode != 0:
            print(f"  [WARN] update ep{ep_num}: {r.stderr[:200]}")

    return all_ok


# ─── Batch Controller ────────────────────────────────────────────────────────

def run_batch(count: int, mode: str, episodes: int, output_dir: str,
              art_style: str = "", auto: bool = False):
    """Run batch generation of N independent comic projects."""

    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("  Comic Script Generator - Batch Mode")
    print("=" * 60)
    print("  Stories to generate : {}".format(count))
    print("  Density mode        : {}".format(mode))
    print("  Episodes per story  : {}".format(episodes))
    print("  Art style           : {}".format(art_style or "(default)"))
    print("  Output directory    : {}".format(output_dir))
    print("  Auto mode           : {}".format("ON (no pauses)" if auto else "OFF (confirm between stories)"))
    print("=" * 60)

    # Fetch hot topics once
    print("\n[1/3] Fetching hot topics...")
    topics = fetch_baidu_hotspots()
    if not topics:
        print("  Baidu failed, using fallback topics...")
        topics = fallback_hot_topics()

    suitable = filter_suitable_topics(topics)
    print("  Found {} suitable topics from {} total".format(len(suitable), len(topics)))

    if len(suitable) < count:
        print("[WARN] Only {} suitable topics, but need {}".format(len(suitable), count))
        if len(suitable) == 0:
            print("[ERROR] No suitable topics. Aborting.")
            return

    random.seed()
    random.shuffle(suitable)

    results = []
    start_time = time.time()

    for i in range(count):
        topic = suitable[i % len(suitable)]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = "batch_{}_{:03d}".format(timestamp, i + 1)

        print("\n{}".format("-" * 60))
        print("[{}/{}] Project: {}".format(i + 1, count, project_name))
        print("  Topic: {}".format(topic))

        # Initialize
        print("  [2/3] Initializing project...")
        project_dir = init_project(project_name, output_dir, mode, episodes, art_style)
        if not project_dir:
            results.append({"name": project_name, "topic": topic, "status": "FAILED", "reason": "init error"})
            continue

        # Generate
        print("  [3/3] Generating {} episodes (this takes a few minutes)...".format(episodes))
        gen_start = time.time()
        success = generate_outline_and_episodes(
            topic, project_name, mode, episodes, art_style, output_dir
        )
        gen_time = time.time() - gen_start

        if not success:
            results.append({"name": project_name, "topic": topic, "status": "FAILED", "reason": "generation error"})
            continue

        # Validate
        print("  [4/3] Validating episodes...")
        validation_ok = run_validation(project_dir, episodes, mode)

        status = "OK" if validation_ok else "WARN"
        results.append({
            "name": project_name,
            "topic": topic,
            "status": status,
            "episodes": episodes,
            "time": "{:.0f}s".format(gen_time),
        })

        print("  Done! ({:.0f}s) [{}]".format(gen_time, status))

        # Pause between stories (unless auto mode)
        if not auto and i < count - 1:
            print("\n  Project {} complete. Press Enter to continue...".format(i + 1))
            try:
                input()
            except (EOFError, KeyboardInterrupt):
                print("\n  Batch interrupted by user.")
                break

    # Final summary
    total_time = time.time() - start_time
    print("\n{}".format("=" * 60))
    print("  BATCH GENERATION COMPLETE")
    print("=" * 60)
    print("  Total time   : {:.0f}s ({:.1f}min)".format(total_time, total_time / 60))
    print("  Successful   : {}".format(sum(1 for r in results if r["status"] == "OK")))
    print("  Warnings     : {}".format(sum(1 for r in results if r["status"] == "WARN")))
    print("  Failed       : {}".format(sum(1 for r in results if r["status"] == "FAILED")))
    print()
    for r in results:
        icon = "O" if r["status"] == "OK" else "!" if r["status"] == "WARN" else "X"
        print("  [{}] {}".format(icon, r["name"]))
        print("    Topic  : {}".format(r["topic"]))
        print("    Status : {}".format(r["status"]))
        if "time" in r:
            print("    Time   : {}".format(r["time"]))
    print("=" * 60)

    # Save report
    report_path = os.path.join(output_dir, "batch_report_{}.json".format(
        datetime.now().strftime("%Y%m%d_%H%M%S")))
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now(timezone(timedelta(hours=8))).isoformat(),
            "mode": mode,
            "episodes_per_story": episodes,
            "total_time": total_time,
            "results": results,
        }, f, indent=2, ensure_ascii=False)
    print("\n  Report saved: {}".format(report_path))


def fallback_hot_topics() -> list:
    """Fallback: generate diverse topics via LLM when scraping fails."""
    config = get_hermes_api_config()
    base_url = config.get("base_url", "https://cli-api.aweqy.top/v1").rstrip("/")
    api_key = config.get("api_key", "")
    model = config.get("default_model", "step-router-v1")

    prompt = (
        "列出20个当前适合改编成漫画的热点话题（中国互联网热点）。\n"
        "要求：\n"
        "- 有故事性、情感共鸣或娱乐性\n"
        "- 排除纯时政、灾难、暴力、敏感政治内容\n"
        "- 每条只需给出话题标题\n"
        "- 格式：每行一个，编号1-20\n"
    )

    result = call_llm(base_url, api_key, model, prompt, max_tokens=2000)
    if result:
        lines = [l.strip() for l in result.split("\n") if l.strip() and len(l.strip()) >= 4]
        cleaned = []
        for line in lines:
            line = re.sub(r'^\d+[.、）)]\s*', '', line)
            cleaned.append(line)
        return cleaned[:20]

    return [
        "上班族的周末治愈日常", "校园里的神秘转学生", "都市传说之便利店夜班",
        "猫咪的奇幻冒险", "快递员的暖心故事", "老巷里的手艺人",
        "网红餐厅的真实味道", "面试的意外转折", "合租生活的趣事",
        "高铁上的偶遇", "深夜食堂的故事", "健身房的搞笑日常",
    ]


# ─── CLI Entry Point ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Comic Script Generator - Batch Mode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python batch_generate.py --count 3 --mode B --auto\n"
            "  python batch_generate.py --count 5 --mode C --episodes 4\n"
            "  python batch_generate.py --count 2 --mode A --art-style '宫崎骏风格'\n"
        ),
    )
    parser.add_argument("--count", "-n", type=int, required=True,
                        help="Number of stories to generate")
    parser.add_argument("--mode", "-m", choices=["A", "B", "C"], default="B",
                        help="Density mode (default: B)")
    parser.add_argument("--episodes", "-e", type=int, default=5,
                        help="Episodes per story (default: 5)")
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT,
                        help="Output directory (default: ~/comic-projects)")
    parser.add_argument("--art-style", "-a", default="",
                        help="Art style description for AI prompts")
    parser.add_argument("--auto", action="store_true",
                        help="Auto-continue between stories (no prompts)")

    args = parser.parse_args()

    if args.count < 1:
        print("Error: --count must be >= 1")
        sys.exit(1)

    run_batch(
        count=args.count,
        mode=args.mode,
        episodes=args.episodes,
        output_dir=args.output,
        art_style=args.art_style,
        auto=args.auto,
    )


if __name__ == "__main__":
    main()
