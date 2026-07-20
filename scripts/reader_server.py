#!/usr/bin/env python3
"""
Comic Script Generator — Reader API Server
===========================================
FastAPI + uvicorn based reader server that serves comic/light-novel
projects for the comic-script-generator skill.

Environment variables:
    COMIC_PROJECTS_ROOT   — path to comic projects directory (default: ~/comic-projects/projects)
    COMIC_READER_PORT     — port to listen on (default: 8081)
    COMIC_READER_API_KEY  — optional API key for request authentication

Routes:
    GET  /                          serve reader.html
    GET  /health                    health check
    GET  /projects                  list projects
    GET  /projects/{name}           project detail (config, episodes, docs, images, stats)
    GET  /project/{name}            compatibility alias for /projects/{name}
    GET  /episode?project=&file=    episode markdown content
    GET  /doc?project=&file=        project document content (summary, characters, etc.)
    GET  /file?project=&path=       serve raw file from project
    GET  /thumb?project=&path=&width=&height=&fit=  dynamic thumbnail via Pillow
    GET  /light-novels?project=     list light_novel/ chapters
"""

from __future__ import annotations

import json
import logging
import mimetypes
import os
import re
import sys
import urllib.parse
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("reader_server")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def _get_projects_root() -> Path:
    """Resolve the comic projects root directory."""
    raw = os.environ.get("COMIC_PROJECTS_ROOT", "")
    if raw:
        path = Path(raw).expanduser().resolve()
    else:
        path = Path.home() / "comic-projects" / "projects"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _get_port() -> int:
    raw = os.environ.get("COMIC_READER_PORT", "8081")
    try:
        return int(raw)
    except ValueError:
        return 8081


def _get_api_key() -> Optional[str]:
    key = os.environ.get("COMIC_READER_API_KEY", "")
    return key.strip() or None


PROJECTS_ROOT = _get_projects_root()
PORT = _get_port()
API_KEY = _get_api_key()

logger.info("PROJECTS_ROOT = %s", PROJECTS_ROOT)
logger.info("PORT = %d", PORT)
logger.info("API_KEY set = %s", "yes" if API_KEY else "no")

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Comic Script Generator — Reader API",
    version="1.0.0",
    description="Local reader server for comic/light-novel projects.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Security helpers
# ---------------------------------------------------------------------------

async def verify_api_key(request: Request) -> None:
    """Check API key from query param or X-API-Key header, if configured."""
    if API_KEY is None:
        return  # no key configured — open access

    query_key = request.query_params.get("api_key")
    header_key = request.headers.get("x-api-key", "")

    provided = (query_key or header_key or "").strip()
    if provided != API_KEY:
        logger.warning("Unauthorized access attempt from %s", request.client.host if request.client else "?")
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return


def safe_resolve(project: str, *parts: str) -> Path | None:
    """
    Resolve a path inside a project directory with traversal protection.
    Returns None if the resolved path is outside the project or the project
    name contains suspicious characters.
    """
    # Basic sanitisation: block path separators and parent-dir tricks in project name
    if not project or ".." in project or "/" in project or "\\" in project:
        return None

    project_dir = (PROJECTS_ROOT / project).resolve()

    # Project must exist and be a directory
    if not project_dir.is_dir():
        return None

    # Resolve the full path
    full = project_dir
    for part in parts:
        # Normalise and sanitise each part
        p = Path(part).as_posix()
        if ".." in p:
            return None
        full = (full / p).resolve()

    # Check traversal: the resolved path must still be under project_dir
    try:
        full.relative_to(project_dir)
    except ValueError:
        return None

    return full


def load_json_safe(path: Path) -> dict:
    """Load a JSON file, returning an empty dict on any error."""
    try:
        if path.is_file():
            with open(path, "r", encoding="utf-8") as fh:
                return json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to load JSON %s: %s", path, exc)
    return {}


def read_text_safe(path: Path) -> str | None:
    """Read a text file, returning None on error."""
    try:
        if path.is_file():
            with open(path, "r", encoding="utf-8") as fh:
                return fh.read()
    except (OSError, UnicodeDecodeError) as exc:
        logger.warning("Failed to read %s: %s", path, exc)
    return None


# ---------------------------------------------------------------------------
# Route: GET / — serve reader.html
# ---------------------------------------------------------------------------

@app.get("/")
async def root(request: Request):
    """Serve the reader HTML page."""
    # Try several common locations for reader.html
    candidate_dirs = [
        Path(__file__).resolve().parent.parent,       # skill directory
        Path(__file__).resolve().parent,               # scripts directory
        Path.cwd(),
    ]
    for d in candidate_dirs:
        reader_path = d / "reader.html"
        if reader_path.is_file():
            return HTMLResponse(content=read_text_safe(reader_path) or "<h1>Reader</h1><p>Loading...</p>")

    # If no reader.html found, return a minimal inline page
    inline_html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Comic Reader</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
       background: #f5f5f5; color: #333; }
header { background: linear-gradient(135deg, #ff6b6b, #ee5a24);
         color: #fff; padding: 24px; text-align: center; }
header h1 { font-size: 28px; margin-bottom: 4px; }
header p { opacity: .85; font-size: 14px; }
.container { max-width: 1000px; margin: 0 auto; padding: 24px; }
.project-card { background: #fff; border-radius: 12px; padding: 20px 24px;
                margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,.08);
                cursor: pointer; transition: transform .15s, box-shadow .15s; }
.project-card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,.12); }
.project-card h3 { font-size: 20px; margin-bottom: 6px; }
.project-card .meta { font-size: 13px; color: #888; }
.loading { text-align: center; padding: 60px 20px; color: #999; }
.error { text-align: center; padding: 20px; color: #e74c3c; }
@media (prefers-color-scheme: dark) {
  body { background: #1a1a2e; color: #e0e0e0; }
  .project-card { background: #16213e; }
  .project-card .meta { color: #aaa; }
}
</style>
</head>
<body>
<header>
  <h1>📚 Comic Reader</h1>
  <p>Comic Script Generator — Project Browser</p>
</header>
<div class="container" id="app">
  <div class="loading">Loading projects…</div>
</div>
<script>
const apiKey = new URLSearchParams(location.search).get('api_key') || '';
const api = (url) => {
  const sep = url.includes('?') ? '&' : '?';
  return fetch(url + (apiKey ? sep + 'api_key=' + encodeURIComponent(apiKey) : '')).then(r => {
    if (!r.ok) throw new Error(r.status + ' ' + r.statusText);
    return r.json();
  });
};
function escapeHtml(t) { const d = document.createElement('div'); d.textContent = t; return d.innerHTML; }
async function loadProjects() {
  const app = document.getElementById('app');
  try {
    const data = await api('/projects');
    if (!data.projects || !data.projects.length) {
      app.innerHTML = '<div class="error"><p>No projects found.</p></div>';
      return;
    }
    app.innerHTML = data.projects.map(p => {
      const status = p.config && p.config.content_mode === 'light_novel' ? '📖' : '🖼';
      const epCount = p.stats ? (p.stats.episodes || 0) : 0;
      const imgCount = p.stats ? (p.stats.images || 0) : 0;
      return `<div class="project-card" onclick="location.href='/projects/${encodeURIComponent(p.name)}' + (apiKey ? '?api_key='+encodeURIComponent(apiKey) : '')">
        <h3>${status} ${escapeHtml(p.name)}</h3>
        <div class="meta">${epCount} episodes · ${imgCount} images</div>
      </div>`;
    }).join('');
  } catch (e) {
    app.innerHTML = '<div class="error">Error loading projects: ' + escapeHtml(e.message) + '</div>';
  }
}
loadProjects();
</script>
</body>
</html>"""
    return HTMLResponse(content=inline_html)


# ---------------------------------------------------------------------------
# Route: GET /health
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "projects_root": str(PROJECTS_ROOT),
        "projects_root_exists": PROJECTS_ROOT.is_dir(),
        "port": PORT,
        "auth_enabled": API_KEY is not None,
    }


# ---------------------------------------------------------------------------
# Route: GET /projects
# ---------------------------------------------------------------------------

@app.get("/projects")
async def list_projects(
    request: Request,
    search: Optional[str] = Query(None, description="Filter projects by name (substring match)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    await verify_api_key(request)

    if not PROJECTS_ROOT.is_dir():
        return JSONResponse(content={"projects": [], "count": 0, "page": page, "page_size": page_size, "total_pages": 0})

    # Gather project directories
    all_projects = []
    for entry in sorted(PROJECTS_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        name = entry.name
        # Skip hidden directories
        if name.startswith("."):
            continue
        if search and search.lower() not in name.lower():
            continue
        config = load_json_safe(entry / "config.json")
        stats = _compute_project_stats(entry)
        all_projects.append({
            "name": name,
            "config": config,
            "stats": stats,
        })

    # Pagination
    total = len(all_projects)
    total_pages = max(1, (total + page_size - 1) // page_size)
    start = (page - 1) * page_size
    end = start + page_size
    page_projects = all_projects[start:end]

    return {
        "projects": page_projects,
        "count": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


def _compute_project_stats(project_dir: Path) -> dict:
    """Compute episode count, image count, and light-novel chapter count."""
    episodes = []
    images = []
    novel_chapters = []

    # Episodes (markdown files directly in project or in episodes/)
    for pattern in ["*.md", "episodes/*.md"]:
        for f in project_dir.glob(pattern):
            # Skip metadata files
            name = f.name
            if name in ("summary.md", "characters.md", "foreshadowing.md", "style_guide.md", "config.json"):
                continue
            episodes.append(str(f.relative_to(project_dir)))

    # Images (rendered and raw)
    for d in ["rendered", "render_output", "images"]:
        img_dir = project_dir / d
        if img_dir.is_dir():
            for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp", "*.gif"):
                images.extend([str(p.relative_to(project_dir)) for p in img_dir.rglob(ext)])

    # Light novel chapters
    ln_dir = project_dir / "light_novel"
    if ln_dir.is_dir():
        for f in sorted(ln_dir.glob("ln*.md")):
            novel_chapters.append({
                "file": str(f.relative_to(project_dir)),
                "title": _extract_title(read_text_safe(f) or ""),
                "chars": len(read_text_safe(f) or ""),
            })

    return {
        "episodes": episodes,
        "episode_count": len(episodes),
        "images": images[:200],  # cap to avoid huge payload
        "image_count": len(images),
        "novel_chapters": novel_chapters,
        "novel_chapter_count": len(novel_chapters),
    }


def _extract_title(md: str) -> str:
    """Extract the first H1 title from markdown."""
    m = re.search(r"^#\s+(.+)$", md, re.MULTILINE)
    return m.group(1).strip() if m else ""


# ---------------------------------------------------------------------------
# Route: GET /projects/by-update — list projects sorted by last content mtime
# NOTE: must be registered BEFORE /projects/{name:path} so "by-update" is not
# captured as a project name.
# ---------------------------------------------------------------------------

def _project_last_updated(project_dir: Path) -> float:
    """Return the latest mtime across all content files in a project.

    Scans: *.md (root, episodes/, light_novel/) + images under rendered/,
    render_output/, images/. Falls back to the project directory's own mtime
    if no content files are found.
    """
    latest = 0.0

    # Markdown files (metadata + episodes + light_novel chapters)
    for pattern in ("*.md", "episodes/*.md", "light_novel/*.md"):
        for f in project_dir.glob(pattern):
            try:
                mtime = f.stat().st_mtime
                if mtime > latest:
                    latest = mtime
            except OSError:
                continue

    # Images under known render directories
    for d in ("rendered", "render_output", "images"):
        img_dir = project_dir / d
        if not img_dir.is_dir():
            continue
        for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp", "*.gif"):
            for f in img_dir.rglob(ext):
                try:
                    mtime = f.stat().st_mtime
                    if mtime > latest:
                        latest = mtime
                except OSError:
                    continue

    # Fallback: directory mtime
    if latest == 0.0:
        try:
            latest = project_dir.stat().st_mtime
        except OSError:
            pass

    return latest


@app.get("/projects/by-update")
async def list_projects_by_update(
    request: Request,
    limit: int = Query(50, ge=1, le=200, description="Max projects to return"),
    content_mode: Optional[str] = Query(
        None,
        description="Filter: 'comic' (has rendered images or no light_novel chapters), "
                    "'light_novel' (has light_novel/ chapters), or omit for all",
    ),
):
    """List projects sorted by last content update time (newest first).

    The "last update" is the maximum mtime across all markdown files
    (metadata + episodes + light_novel chapters) and rendered images.
    """
    await verify_api_key(request)

    if not PROJECTS_ROOT.is_dir():
        return {"projects": [], "count": 0}

    import datetime as _dt

    items = []
    for entry in PROJECTS_ROOT.iterdir():
        if not entry.is_dir():
            continue
        name = entry.name
        if name.startswith("."):
            continue

        config = load_json_safe(entry / "config.json")
        stats = _compute_project_stats(entry)

        # Apply content_mode filter
        if content_mode == "light_novel":
            if stats["novel_chapter_count"] == 0:
                continue
        elif content_mode == "comic":
            is_comic = (
                stats["image_count"] > 0
                or (stats["novel_chapter_count"] == 0 and stats["episode_count"] > 0)
                or "comic" in str(config.get("content_mode", "")).lower()
                or "漫画" in str(config.get("category", ""))
            )
            if not is_comic:
                continue

        last_updated = _project_last_updated(entry)
        items.append({
            "name": name,
            "config": config,
            "stats": {
                "episode_count": stats["episode_count"],
                "image_count": stats["image_count"],
                "novel_chapter_count": stats["novel_chapter_count"],
            },
            "last_updated": last_updated,
            "last_updated_iso": (
                _dt.datetime.fromtimestamp(last_updated).isoformat()
                if last_updated > 0 else None
            ),
        })

    # Sort by last_updated desc (newest first)
    items.sort(key=lambda x: x["last_updated"], reverse=True)

    return {
        "projects": items[:limit],
        "count": len(items),
        "limit": limit,
    }


# ---------------------------------------------------------------------------
# Route: GET /projects/{name}  +  /project/{name} (compatibility)
# ---------------------------------------------------------------------------

@app.get("/projects/{name:path}")
async def project_detail(name: str, request: Request):
    await verify_api_key(request)

    resolved = safe_resolve(name)
    if resolved is None:
        raise HTTPException(status_code=404, detail=f"Project '{name}' not found")

    project_dir = resolved

    # Load metadata
    config = load_json_safe(project_dir / "config.json")
    summary = read_text_safe(project_dir / "summary.md") or ""
    characters = read_text_safe(project_dir / "characters.md") or ""
    foreshadowing = read_text_safe(project_dir / "foreshadowing.md") or ""
    style_guide = read_text_safe(project_dir / "style_guide.md") or ""

    stats = _compute_project_stats(project_dir)

    # Episode files list with titles
    episodes = []
    for ep in sorted(project_dir.glob("episodes/*.md")):
        content = read_text_safe(ep)
        title = _extract_title(content or "")
        episodes.append({
            "file": str(ep.relative_to(project_dir)),
            "title": title or ep.stem,
            "chars": len(content or ""),
        })

    # Docs list
    doc_files = []
    for doc_name in ["summary.md", "characters.md", "foreshadowing.md", "style_guide.md"]:
        if (project_dir / doc_name).is_file():
            doc_files.append(doc_name)

    result = {
        "name": name,
        "config": config,
        "stats": stats,
        "episodes": episodes,
        "doc_files": doc_files,
        "summary": summary[:2000],  # truncated for list view
        "characters": characters[:2000],
        "foreshadowing": foreshadowing[:2000],
        "style_guide": style_guide[:2000],
    }
    return result


@app.get("/project/{name:path}")
async def project_detail_alias(name: str, request: Request):
    """Compatibility alias for /projects/{name}."""
    return await project_detail(name, request)


# ---------------------------------------------------------------------------
# Route: GET /episode?project=&file=
# ---------------------------------------------------------------------------

@app.get("/episode")
async def get_episode(
    request: Request,
    project: str = Query(..., description="Project name"),
    file: str = Query(..., description="Episode file path (relative to project)"),
):
    await verify_api_key(request)

    path = safe_resolve(project, file)
    if path is None:
        raise HTTPException(status_code=404, detail=f"Episode '{file}' not found in project '{project}'")

    content = read_text_safe(path)
    if content is None:
        raise HTTPException(status_code=404, detail="Failed to read episode file")

    return Response(content=content, media_type="text/markdown; charset=utf-8")


# ---------------------------------------------------------------------------
# Route: GET /doc?project=&file=
# ---------------------------------------------------------------------------

@app.get("/doc")
async def get_doc(
    request: Request,
    project: str = Query(..., description="Project name"),
    file: str = Query(..., description="Document file name (e.g. summary.md, characters.md)"),
):
    await verify_api_key(request)

    path = safe_resolve(project, file)
    if path is None:
        raise HTTPException(status_code=404, detail=f"Document '{file}' not found in project '{project}'")

    content = read_text_safe(path)
    if content is None:
        raise HTTPException(status_code=404, detail="Failed to read document file")

    return Response(content=content, media_type="text/markdown; charset=utf-8")


# ---------------------------------------------------------------------------
# Route: GET /file?project=&path=
# ---------------------------------------------------------------------------

@app.get("/file")
async def get_file(
    request: Request,
    project: str = Query(..., description="Project name"),
    path: str = Query(..., description="File path relative to project root"),
):
    await verify_api_key(request)

    resolved = safe_resolve(project, path)
    if resolved is None or not resolved.is_file():
        raise HTTPException(status_code=404, detail=f"File '{path}' not found in project '{project}'")

    # Guess media type
    media_type, _ = mimetypes.guess_type(str(resolved))
    if media_type is None:
        media_type = "application/octet-stream"

    return FileResponse(path=str(resolved), media_type=media_type)


# ---------------------------------------------------------------------------
# Route: GET /thumb?project=&path=&width=&height=&fit=
# ---------------------------------------------------------------------------

@app.get("/thumb")
async def get_thumbnail(
    request: Request,
    project: str = Query(..., description="Project name"),
    path: str = Query(..., description="Image path relative to project root"),
    width: int = Query(300, ge=16, le=4096, description="Target width"),
    height: int = Query(300, ge=16, le=4096, description="Target height"),
    fit: str = Query("cover", regex="^(cover|inside)$", description="Fit mode: cover or inside"),
):
    await verify_api_key(request)

    resolved = safe_resolve(project, path)
    if resolved is None or not resolved.is_file():
        raise HTTPException(status_code=404, detail=f"File '{path}' not found in project '{project}'")

    # Only process image files
    ext = resolved.suffix.lower()
    if ext not in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tiff", ".tif"):
        # Non-image: return as-is
        media_type, _ = mimetypes.guess_type(str(resolved))
        return FileResponse(path=str(resolved), media_type=media_type or "application/octet-stream")

    # Generate thumbnail via Pillow
    try:
        from PIL import Image, ImageOps  # noqa: E402
    except ImportError:
        # Fallback: return original
        logger.warning("Pillow not available, returning original file for thumbnail")
        media_type, _ = mimetypes.guess_type(str(resolved))
        return FileResponse(path=str(resolved), media_type=media_type or "application/octet-stream")

    try:
        img = Image.open(resolved)
        img.load()  # force load to catch corrupt images early
    except Exception as exc:
        logger.error("Failed to open image %s: %s", resolved, exc)
        raise HTTPException(status_code=500, detail=f"Failed to open image: {exc}")

    # Preserve aspect ratio
    img_format = "JPEG"
    if ext == ".png":
        # If image has transparency, keep PNG; otherwise JPEG is fine
        if img.mode in ("RGBA", "LA", "P"):
            img_format = "PNG"
            # Convert palette to RGBA if needed
            if img.mode == "P":
                img = img.convert("RGBA")

    # Convert to RGB for JPEG output if needed
    if img_format == "JPEG" and img.mode != "RGB":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "RGBA":
            bg.paste(img, mask=img.split()[3])
        else:
            bg.paste(img)
        img = bg

    # Resize
    resample_filter = getattr(Image, "LANCZOS", getattr(getattr(Image, "Resampling", None), "LANCZOS", 3))  # 3 = BICUBIC
    size = (width, height)
    if fit == "cover":
        img = ImageOps.fit(img, size, resample_filter, centering=(0.5, 0.5))
    else:
        img.thumbnail(size, resample_filter)

    # Save to bytes
    import io
    buf = io.BytesIO()
    save_kwargs: dict = {"format": img_format}
    if img_format == "JPEG":
        save_kwargs["quality"] = 78  # type: ignore[typeddict-unknown-key]
        save_kwargs["optimize"] = True  # type: ignore[typeddict-unknown-key]
    elif img_format == "PNG":
        save_kwargs["optimize"] = True  # type: ignore[typeddict-unknown-key]

    try:
        img.save(buf, **save_kwargs)
    except Exception as exc:
        logger.error("Failed to save thumbnail for %s: %s", resolved, exc)
        raise HTTPException(status_code=500, detail="Failed to generate thumbnail")

    buf.seek(0)

    media_type = "image/jpeg" if img_format == "JPEG" else "image/png"
    return Response(
        content=buf.read(),
        media_type=media_type,
        headers={
            "Cache-Control": "public, max-age=86400",
            "Content-Disposition": "inline",
        },
    )


# ---------------------------------------------------------------------------
# Route: GET /light-novels?project=
# ---------------------------------------------------------------------------

@app.get("/light-novels")
async def list_light_novels(
    request: Request,
    project: str = Query(..., description="Project name"),
):
    await verify_api_key(request)

    resolved = safe_resolve(project)
    if resolved is None:
        raise HTTPException(status_code=404, detail=f"Project '{project}' not found")

    ln_dir = resolved / "light_novel"
    if not ln_dir.is_dir():
        return {
            "project": project,
            "count": 0,
            "novels": [],
        }

    novels = []
    for f in sorted(ln_dir.glob("ln*.md")):
        content = read_text_safe(f)
        title = _extract_title(content or "")
        novels.append({
            "file": str(f.relative_to(resolved)),
            "title": title or f.stem,
            "chars": len(content or ""),
            "url": f"/file?project={urllib.parse.quote(project)}&path={urllib.parse.quote(str(f.relative_to(resolved)))}",
        })

    return {
        "project": project,
        "count": len(novels),
        "novels": novels,
    }


# ---------------------------------------------------------------------------
# Legacy /reader route (mirrors /)
# ---------------------------------------------------------------------------

@app.get("/reader")
async def reader_page(request: Request):
    """Serve reader.html at /reader as well."""
    return await root(request)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    import uvicorn

    logger.info("Starting Reader API server...")
    logger.info("Projects root: %s", PROJECTS_ROOT)
    logger.info("Listening on port: %d", PORT)
    if API_KEY:
        logger.info("API key authentication is ENABLED")
    else:
        logger.info("API key authentication is DISABLED (open access)")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info",
        access_log=True,
    )


if __name__ == "__main__":
    main()
