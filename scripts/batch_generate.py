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
import uuid
import hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ─── Configuration ───────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_OUTPUT = os.path.expanduser("~/comic-projects")
DEFAULT_EPISODES = 5

# ─── Cross-platform config discovery ─────────────────────────────────────────
# Priority:
#  1. HERMES_CONFIG env var
#  2. CWD-relative ./config.yaml
#  3. Skill-relative ./config.yaml
#  4. User config dirs (Linux/macOS/Windows)
#  5. Fallback to defaults (no key -> prompt user)

HERMES_CONFIG_CANDIDATES = []

# 1. Env var
_env = os.environ.get("HERMES_CONFIG", "").strip()
if _env:
    HERMES_CONFIG_CANDIDATES.append(Path(_env))

# 2. CWD
HERMES_CONFIG_CANDIDATES.append(Path("config.yaml"))

# 3. Skill dir
HERMES_CONFIG_CANDIDATES.append(SKILL_DIR / "config.yaml")

# 4. Platform-specific
if sys.platform == "win32":
    HERMES_CONFIG_CANDIDATES.append(Path(os.environ.get("LOCALAPPDATA", "")) / "hermes" / "config.yaml")
    HERMES_CONFIG_CANDIDATES.append(Path.home() / ".hermes" / "config.yaml")
else:
    HERMES_CONFIG_CANDIDATES.append(Path.home() / ".hermes" / "config.yaml")
    HERMES_CONFIG_CANDIDATES.append(Path.home() / ".config" / "hermes" / "config.yaml")
    HERMES_CONFIG_CANDIDATES.append(Path("/etc/hermes/config.yaml"))

# Deduplicate while preserving order
_seen = set()
HERMES_CONFIG_CANDIDATES = [p for p in HERMES_CONFIG_CANDIDATES
                            if not (str(p) in _seen or _seen.add(str(p)))]

# Baidu hot topics
BAIDU_URL = "https://top.baidu.com/board?tab=realtime"

# Topics excluded from batch generation
EXCLUDED_KEYWORDS = [
    "疫情", "死亡", "杀害", "爆炸", "袭击", "地震", "洪水", "火灾",
    "自杀", "暴力", "恐怖", "战争", "时政", "政治", "敏感", "独裁",
    "毒品", "赌博", "诈骗", "邪教", "色情", "裸露",
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

        # Strategy 1: JSON data in script tags (current Baidu format)
        pattern = re.compile(r'"word":"([^"]{4,50})"')
        matches = pattern.findall(html)

        # Strategy 2: HTML title tags
        if not matches:
            pattern2 = re.compile(r'<h2[^>]*>([^<]{4,50})</h2>')
            matches = pattern2.findall(html)

        # Strategy 3: aria-label or title attributes
        if not matches:
            pattern3 = re.compile(r'title="([^"]{4,50})"')
            matches = pattern3.findall(html)

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
    """
    Read Hermes config to get LLM API settings.
    Cross-platform: searches multiple config locations.
    Falls back to env vars if config not found.
    """
    config_path = None
    for candidate in HERMES_CONFIG_CANDIDATES:
        if candidate.exists():
            config_path = candidate
            break

    if not config_path:
        # Fallback to environment
        return {
            "base_url": os.environ.get("HERMES_BASE_URL", "https://cli-api.aweqy.top/v1").rstrip("/"),
            "api_key": os.environ.get("HERMES_API_KEY", ""),
            "default_model": os.environ.get("HERMES_MODEL", "step-router-v1"),
        }

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()

        config = {}
        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Handle YAML key: value (simple cases)
            if ":" in line:
                key, _, val = line.partition(":")
                key = key.strip()
                val = val.strip()
                # Remove quotes
                if (val.startswith('"') and val.endswith('"')) or \
                   (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                config[key] = val

        return config
    except Exception as e:
        print(f"[WARN] Failed to parse Hermes config at {config_path}: {e}")
        return {}


def call_llm(base_url: str, api_key: str, model: str, prompt: str,
             max_tokens: int = 8000, retries: int = 3, backoff: float = 2.0) -> str:
    """
    Call LLM API with retry logic.
    Retries on network errors, 5xx, and 429 (rate limit).
    """
    url = f"{base_url.rstrip('/')}/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.8,
    }).encode("utf-8")

    last_error = ""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=payload, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            })

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

            # Retry on 429 (rate limit) and 5xx (server errors)
            if e.code in (429, 500, 502, 503, 504):
                wait = backoff * (2 ** attempt) + random.uniform(0, 1)
                print(f"\n[RETRY {attempt+1}/{retries}] HTTP {e.code}, waiting {wait:.1f}s...")
                time.sleep(wait)
                last_error = f"HTTP {e.code}: {body[:200]}"
                continue

            # Non-retryable error
            print(f"\n[LLM HTTP {e.code}] {body[:200]}")
            return ""

        except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
            wait = backoff * (2 ** attempt) + random.uniform(0, 1)
            print(f"\n[RETRY {attempt+1}/{retries}] Network error: {e}, waiting {wait:.1f}s...")
            time.sleep(wait)
            last_error = str(e)
            continue

        except Exception as e:
            print(f"\n[LLM Error] {e}")
            return ""

    print(f"\n[LLM FAILED] Max retries exceeded. Last error: {last_error}")
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


# ─── Episode Generation with Context Management ──────────────────────────────

def generate_outline(topic: str, project_name: str, mode: str,
                     episodes: int, art_style: str) -> str:
    """Generate story outline only."""
    config = get_hermes_api_config()
    base_url = config.get("base_url", "https://cli-api.aweqy.top/v1").rstrip("/")
    api_key = config.get("api_key", "")
    model = config.get("default_model", "step-router-v1")

    if not api_key:
        print("[ERROR] No API key found. Set HERMES_API_KEY env var or configure Hermes.")
        return ""

    mode_desc = {
        "A": "对话多，镜头少（传统漫画风，每集30-40场景，每场景1-2个镜头+3-8段对话）",
        "B": "一个对话对应一个镜头（平衡模式，每集50-60场景）",
        "C": "一段对话多个镜头（电影短剧风，每集150-250场景，画面细节丰富）",
    }

    outline_prompt = (
        "你是专业的漫画编剧。为主题「{topic}」创作漫画故事大纲。\n\n"
        "要求：\n"
        "- 分镜密度模式：{mode_desc}\n"
        "- 计划集数：{episodes}集\n"
        "- 2-3个主要角色（姓名、性格、外貌、背景）\n"
        "- 每集梗概（100-200字）\n"
        "- 至少2个伏笔（埋在某集，后续回收）\n"
        "- 风格：{art_style}\n\n"
        "输出Markdown：\n"
        "# {project_name}\n\n"
        "## 故事大纲\n"
        "### 核心设定\n[背景、冲突]\n\n"
        "### 主要角色\n[档案]\n\n"
        "### 分集规划\n"
        "- 第1集：[标题] - [梗概]\n"
        "- ...\n\n"
        "### 伏笔设计\n"
        "- [描述]（第X集埋下，第Y集回收）\n"
    ).format(
        topic=topic,
        mode_desc=mode_desc.get(mode, mode_desc["B"]),
        episodes=episodes,
        art_style=art_style or "现代都市，写实风格",
        project_name=project_name,
    )

    outline = call_llm(base_url, api_key, model, outline_prompt, max_tokens=4000)
    return outline or ""


def generate_episode(ep_num: int, outline: str, mode: str, project_name: str) -> str:
    """
    Generate a single episode using the full outline.
    Outline is NOT truncated here; passed in full to preserve context.
    """
    config = get_hermes_api_config()
    base_url = config.get("base_url", "https://cli-api.aweqy.top/v1").rstrip("/")
    api_key = config.get("api_key", "")
    model = config.get("default_model", "step-router-v1")

    mode_desc = {
        "A": "对话多，镜头少（传统漫画风，每集30-40场景）",
        "B": "一个对话对应一个镜头（平衡模式，每集50-60场景）",
        "C": "一段对话多个镜头（电影短剧风，每集150-250场景）",
    }

    ep_prompt = (
        "你是漫画编剧。根据大纲撰写第{ep_num}集分镜脚本。\n\n"
        "【完整大纲】\n{outline}\n\n"
        "【要求】\n"
        "- 分镜密度：{mode_desc}\n"
        "- 每个场景：镜头类型、画面描述、对话/旁白、AI提示词（正向+反向）\n"
        "- 对话自然，画面具象化（颜色、光线、动作、表情）\n"
        "- AI提示词格式：```masterpiece...``` 和 ```worst quality...```\n\n"
        "【输出】\n"
        "# 第{ep_num}集：[标题]\n\n"
        "**故事梗概**：[本集内容]\n"
        "**分镜模式**：{mode}\n"
        "**预计场景数**：X个\n\n"
        "---\n\n"
        "## Scene 1\n"
        "**镜头**：[类型]\n"
        "**画面**：[描述]\n"
        "**对话**：\n"
        "- [角色]：[台词]\n"
        "**AI 提示词**：\n"
        "正向：\n```\nmasterpiece, best quality, [画面], [镜头], [风格], cinematic lighting\n```\n"
        "反向：\n```\nworst quality, low quality, blurry, deformed, bad anatomy, extra limbs\n```\n\n"
        "---\n\n"
        "*本集完*\n\n"
        "**生成统计**：\n"
        "- 总场景数：X\n"
        "- 总对话数：X\n"
        "- 验证状态：待验证\n"
    ).format(ep_num=ep_num, outline=outline, mode_desc=mode_desc.get(mode, mode_desc["B"]), mode=mode)

    ep_content = call_llm(base_url, api_key, model, ep_prompt, max_tokens=20000)
    return ep_content or ""


def generate_outline_and_episodes(topic: str, project_name: str, mode: str,
                                   episodes: int, art_style: str,
                                   output_dir: str) -> bool:
    """Generate story outline and episodes using LLM with full context."""
    print("  Generating outline...", end=" ", flush=True)
    outline = generate_outline(topic, project_name, mode, episodes, art_style)
    if not outline:
        print("FAILED")
        return False
    print("OK ({} chars)".format(len(outline)))

    project_dir = os.path.join(output_dir, "projects", project_name)
    outline_path = os.path.join(project_dir, "outline.md")
    with open(outline_path, "w", encoding="utf-8") as f:
        f.write(outline)

    for ep_num in range(1, episodes + 1):
        print("  Episode {}/{}...".format(ep_num, episodes), end=" ", flush=True)

        # Rate limiting: small delay between episodes to avoid hitting rate limits
        if ep_num > 1:
            time.sleep(random.uniform(1.5, 3.0))

        ep_content = generate_episode(ep_num, outline, mode, project_name)
        if not ep_content:
            print("FAILED")
            return False

        # Extract title
        title_match = re.search(r"第\d+集[：:](.+)", ep_content)
        ep_title = title_match.group(1).strip() if title_match else "第{}集".format(ep_num)
        ep_title = re.sub(r'[\\/:*?"<>|]', "", ep_title).strip() or "第{}集".format(ep_num)

        ep_filename = "ep{:03d}_{}.md".format(ep_num, ep_title[:30])
        ep_path = os.path.join(project_dir, "episodes", ep_filename)

        with open(ep_path, "w", encoding="utf-8") as f:
            f.write(ep_content)
        print("OK ({} chars)".format(len(ep_content)))

    return True


# ─── Validation ──────────────────────────────────────────────────────────────

def run_validation(project_dir: str, episodes: int, mode: str) -> bool:
    """Run validation scripts. Returns True if all passed, False if warnings."""
    validate_script = SCRIPT_DIR / "validate_episode.py"
    consistency_script = SCRIPT_DIR / "consistency_check.py"
    update_script = SCRIPT_DIR / "update_project.py"

    all_ok = True
    episodes_dir = os.path.join(project_dir, "episodes")

    if not os.path.isdir(episodes_dir):
        return False

    for ep_num in range(1, episodes + 1):
        ep_files = [f for f in os.listdir(episodes_dir)
                    if f.startswith("ep{:03d}_".format(ep_num)) and f.endswith(".md")]
        if not ep_files:
            continue
        ep_path = os.path.join(episodes_dir, ep_files[0])

        # Validate
        try:
            r = subprocess.run(
                [sys.executable, str(validate_script), ep_path,
                 "--project-dir", project_dir],
                capture_output=True, text=True, timeout=60
            )
            if r.returncode != 0:
                print("  [WARN] validate ep{}: {}".format(ep_num, r.stderr[:200]))
                all_ok = False
        except subprocess.TimeoutExpired:
            print("  [WARN] validate ep{}: timeout".format(ep_num))
            all_ok = False
        except Exception as e:
            print("  [WARN] validate ep{}: {}".format(ep_num, str(e)[:100]))
            all_ok = False

        # Consistency check
        try:
            r = subprocess.run(
                [sys.executable, str(consistency_script), ep_path,
                 "--project-dir", project_dir],
                capture_output=True, text=True, timeout=60
            )
            if r.returncode != 0:
                print("  [WARN] consistency ep{}: {}".format(ep_num, r.stderr[:200]))
        except Exception as e:
            print("  [WARN] consistency ep{}: {}".format(ep_num, str(e)[:100]))

        # Update project index
        try:
            r = subprocess.run(
                [sys.executable, str(update_script), ep_path,
                 "--project-dir", project_dir,
                 "--episode-num", str(ep_num)],
                capture_output=True, text=True, timeout=60
            )
            if r.returncode != 0:
                print("  [WARN] update ep{}: {}".format(ep_num, r.stderr[:200]))
        except Exception as e:
            print("  [WARN] update ep{}: {}".format(ep_num, str(e)[:100]))

    return all_ok


# ─── Batch Controller ────────────────────────────────────────────────────────

def load_checkpoint(output_dir: str) -> set:
    """Load set of completed project names from checkpoint file."""
    checkpoint_path = os.path.join(output_dir, ".batch_checkpoint.json")
    if os.path.exists(checkpoint_path):
        try:
            with open(checkpoint_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data.get("completed", []))
        except Exception:
            pass
    return set()


def save_checkpoint(output_dir: str, completed: set):
    """Save checkpoint of completed projects."""
    checkpoint_path = os.path.join(output_dir, ".batch_checkpoint.json")
    try:
        with open(checkpoint_path, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now(timezone(timedelta(hours=8))).isoformat(),
                "completed": sorted(list(completed)),
            }, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("[WARN] Failed to save checkpoint: {}".format(e))


def estimate_cost(mode: str, episodes: int, stories: int) -> dict:
    """Estimate token usage and time for the batch."""
    # Rough estimates per episode (input + output tokens)
    tokens_per_episode = {
        "A": 4000,   # shorter episodes
        "B": 8000,   # medium
        "C": 20000,  # long episodes
    }

    ep_tokens = tokens_per_episode.get(mode, 8000)
    outline_tokens = 4000

    total_llm_calls = stories * (1 + episodes)  # 1 outline + N episodes
    total_input_tokens = stories * (outline_tokens + episodes * 2000)  # outline + context
    total_output_tokens = stories * (outline_tokens + episodes * ep_tokens)

    # Time estimate: ~15-30s per LLM call
    time_per_call = 20 if mode == "A" else 35 if mode == "C" else 25
    total_seconds = total_llm_calls * time_per_call

    return {
        "llm_calls": total_llm_calls,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "total_tokens": total_input_tokens + total_output_tokens,
        "estimated_seconds": total_seconds,
        "estimated_minutes": total_seconds / 60,
    }


def run_batch(count: int, mode: str, episodes: int, output_dir: str,
              art_style: str = "", auto: bool = False):
    """Run batch generation of N independent comic projects."""

    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Load checkpoint (resume support)
    completed = load_checkpoint(output_dir)
    if completed:
        print("Resuming: {} projects already completed".format(len(completed)))

    # Show cost estimate
    estimate = estimate_cost(mode, episodes, count)
    print("\n" + "=" * 60)
    print("  Comic Script Generator - Batch Mode")
    print("=" * 60)
    print("  Stories to generate : {}".format(count))
    print("  Density mode        : {}".format(mode))
    print("  Episodes per story  : {}".format(episodes))
    print("  Art style           : {}".format(art_style or "(default)"))
    print("  Output directory    : {}".format(output_dir))
    print("  Auto mode           : {}".format("ON" if auto else "OFF"))
    print()
    print("  [Estimate]")
    print("    LLM calls         : {}".format(estimate["llm_calls"]))
    print("    Output tokens     : ~{:,}".format(estimate["output_tokens"]))
    print("    Estimated time    : {:.1f} minutes".format(estimate["estimated_minutes"]))
    print("=" * 60)

    if not auto:
        try:
            confirm = input("\nProceed? [Y/n] ").strip().lower()
            if confirm == "n":
                print("Aborted by user.")
                return
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.")
            return

    # Fetch hot topics once
    print("\n[1/4] Fetching hot topics...")
    topics = fetch_baidu_hotspots()
    if not topics:
        print("  Baidu failed, using fallback topics...")
        topics = fallback_hot_topics()

    suitable = filter_suitable_topics(topics)
    print("  {} suitable topics from {} total".format(len(suitable), len(topics)))

    if len(suitable) == 0:
        print("[ERROR] No suitable topics. Aborting.")
        return

    if len(suitable) < count:
        print("[WARN] Only {} suitable topics for {} stories. Topics will repeat.".format(
            len(suitable), count))

    random.seed()
    random.shuffle(suitable)

    results = []
    start_time = time.time()
    topic_index = 0

    for i in range(count):
        # Checkpoint: skip completed
        timestamp_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
        candidate_name = "batch_{}_{:03d}".format(timestamp_suffix, i + 1)

        if candidate_name in completed:
            print("\n[{}/{}] Skipping {} (already completed)".format(i + 1, count, candidate_name))
            results.append({
                "name": candidate_name,
                "topic": "(checkpoint)",
                "status": "SKIPPED",
            })
            continue

        # Generate unique project name with UUID to avoid collisions
        uid = uuid.uuid4().hex[:8]
        project_name = "batch_{}_{:03d}_{}".format(timestamp_suffix, i + 1, uid)
        topic = suitable[topic_index % len(suitable)]
        topic_index += 1

        print("\n{}".format("-" * 60))
        print("[{}/{}] Project: {}".format(i + 1, count, project_name))
        print("  Topic: {}".format(topic))

        # Initialize
        print("  [2/4] Initializing project...")
        project_dir = init_project(project_name, output_dir, mode, episodes, art_style)
        if not project_dir:
            results.append({"name": project_name, "topic": topic, "status": "FAILED", "reason": "init error"})
            continue

        # Generate
        print("  [3/4] Generating {} episodes...".format(episodes))
        gen_start = time.time()
        success = generate_outline_and_episodes(
            topic, project_name, mode, episodes, art_style, output_dir
        )
        gen_time = time.time() - gen_start

        if not success:
            results.append({"name": project_name, "topic": topic, "status": "FAILED", "reason": "generation error"})
            continue

        # Validate
        print("  [4/4] Validating episodes...")
        validation_ok = run_validation(project_dir, episodes, mode)

        status = "OK" if validation_ok else "WARN"
        results.append({
            "name": project_name,
            "topic": topic,
            "status": status,
            "episodes": episodes,
            "time": "{:.0f}s".format(gen_time),
        })

        # Mark as completed
        completed.add(project_name)
        save_checkpoint(output_dir, completed)

        print("  Done! ({:.0f}s) [{}]".format(gen_time, status))

        # Rate limiting between stories
        if not auto and i < count - 1:
            print("\n  Project {} complete. Press Enter to continue...".format(i + 1))
            try:
                input()
            except (EOFError, KeyboardInterrupt):
                print("\n  Batch interrupted. Progress saved.")
                break
        elif auto and i < count - 1:
            delay = random.uniform(2.0, 5.0)
            print("  Cooling down {:.1f}s before next story...".format(delay))
            time.sleep(delay)

    # Final summary
    total_time = time.time() - start_time
    print("\n{}".format("=" * 60))
    print("  BATCH GENERATION COMPLETE")
    print("=" * 60)
    print("  Total time   : {:.0f}s ({:.1f}min)".format(total_time, total_time / 60))
    print("  Successful   : {}".format(sum(1 for r in results if r["status"] == "OK")))
    print("  Warnings     : {}".format(sum(1 for r in results if r["status"] == "WARN")))
    print("  Failed       : {}".format(sum(1 for r in results if r["status"] == "FAILED")))
    print("  Skipped      : {}".format(sum(1 for r in results if r["status"] == "SKIPPED")))
    print()
    for r in results:
        icon = "O" if r["status"] == "OK" else "!" if r["status"] == "WARN" else "X" if r["status"] == "FAILED" else "-"
        print("  [{}] {}".format(icon, r["name"]))
        print("    Topic  : {}".format(r["topic"]))
        print("    Status : {}".format(r["status"]))
        if "time" in r:
            print("    Time   : {}".format(r["time"]))
    print("=" * 60)

    # Save report
    report_path = os.path.join(output_dir, "batch_report_{}.json".format(
        datetime.now().strftime("%Y%m%d_%H%M%S")))
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now(timezone(timedelta(hours=8))).isoformat(),
                "mode": mode,
                "episodes_per_story": episodes,
                "total_time": total_time,
                "total_tokens_estimate": estimate["total_tokens"],
                "results": results,
            }, f, indent=2, ensure_ascii=False)
        print("\n  Report saved: {}".format(report_path))
    except Exception as e:
        print("[WARN] Failed to save report: {}".format(e))


def fallback_hot_topics() -> list:
    """
    Fallback: try LLM first, then hardcoded safe topics.
    Combines multiple strategies to avoid exhaustion.
    """
    config = get_hermes_api_config()
    base_url = config.get("base_url", "https://cli-api.aweqy.top/v1").rstrip("/")
    api_key = config.get("api_key", "")
    model = config.get("default_model", "step-router-v1")

    if api_key:
        prompt = (
            "列出20个当前适合改编成漫画的热点话题（中国互联网热点）。\n"
            "要求：有故事性、情感共鸣或娱乐性；排除纯时政、灾难、暴力、敏感政治内容。\n"
            "格式：每行一个，编号1-20。"
        )
        result = call_llm(base_url, api_key, model, prompt, max_tokens=2000, retries=2)
        if result:
            lines = [l.strip() for l in result.split("\n") if l.strip() and len(l.strip()) >= 4]
            cleaned = []
            for line in lines:
                line = re.sub(r'^\d+[.、）)]\s*', '', line)
                cleaned.append(line)
            if len(cleaned) >= 10:
                return cleaned[:20]

    # Hardcoded fallback (safe, diverse topics)
    return [
        "上班族的周末治愈日常", "校园里的神秘转学生", "都市传说之便利店夜班",
        "猫咪的奇幻冒险", "快递员的暖心故事", "老巷里的手艺人",
        "网红餐厅的真实味道", "面试的意外转折", "合租生活的趣事",
        "高铁上的偶遇", "深夜食堂的故事", "健身房的搞笑日常",
        "外卖小哥的善意", "小区里的流浪猫", "图书馆的邂逅",
        "老同学的聚会", "新同事的误会", "雨中的一把伞",
        "老街的变迁", "手工蛋糕的温暖",
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
            "  python batch_generate.py -n 2 -m A -o ./my-comics\n"
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
