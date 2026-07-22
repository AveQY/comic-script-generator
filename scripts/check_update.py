#!/usr/bin/env python3
"""Check GitHub repo for updates and optionally pull them."""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta

try:
    import urllib.request
except ImportError:
    urllib = None

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_FILE = os.path.join(SKILL_DIR, ".update_check_cache.json")
REPO_URL = "https://github.com/AveQY/comic-script-generator"
NETWORK_TIMEOUT = 5


def check_network():
    """Check if GitHub is reachable."""
    if urllib is None:
        return False
    try:
        req = urllib.request.Request(
            "https://github.com",
            headers={"User-Agent": "Hermes-Skill-Update-Checker/1.0"},
        )
        resp = urllib.request.urlopen(req, timeout=NETWORK_TIMEOUT)
        return resp.status == 200
    except Exception:
        return False


def get_remote_commit():
    """Get the latest commit SHA from origin/main."""
    try:
        r = subprocess.run(
            ["git", "ls-remote", "origin", "main"],
            cwd=SKILL_DIR,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if r.returncode == 0:
            # Output format: <sha>\trefs/heads/main
            line = r.stdout.strip().split("\n")[0]
            return line.split("\t")[0] if "\t" in line else None
    except Exception:
        pass
    return None


def get_local_commit():
    """Get current HEAD commit SHA."""
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=SKILL_DIR,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if r.returncode == 0:
            return r.stdout.strip()
    except Exception:
        pass
    return None


def load_cache():
    """Load cached check result."""
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_cache(data):
    """Save check result to cache."""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def check_update():
    """Main update check logic."""
    result = {
        "timestamp": datetime.now().isoformat(),
        "network_available": False,
        "update_available": False,
        "action": "skip",
        "message": "",
    }

    # 1. Check network
    if not check_network():
        result["message"] = "网络不通，跳过更新检查"
        save_cache(result)
        return result

    result["network_available"] = True

    # 2. Get commits
    local = get_local_commit()
    remote = get_remote_commit()

    if not local or not remote:
        result["message"] = "无法获取 commit 信息，跳过更新"
        save_cache(result)
        return result

    # 3. Compare
    if local == remote:
        result["update_available"] = False
        result["action"] = "up_to_date"
        result["message"] = f"已是最新 ({remote[:8]})"
    else:
        result["update_available"] = True
        result["action"] = "update_needed"
        result["message"] = f"发现更新: {remote[:8]} (本地: {local[:8]})"

    save_cache(result)
    return result


if __name__ == "__main__":
    result = check_update()
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0 if result["action"] != "update_needed" else 1)
