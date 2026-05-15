#!/usr/bin/env python3
"""update_star_history.py — append published article to per-star history.

Usage:
    python3 /workspace/tools/update_star_history.py <run_id>

Reads:
  - memory/pipeline/runs/{run_id}/state.json       → star, star_label
  - memory/pipeline/runs/{run_id}/draft-v2.md      → article title (frontmatter)
  - memory/pipeline/runs/{run_id}/curated-sources.md → selected angle (first paragraph after heading)
  - memory/pipeline/runs/{run_id}/published.json   → article URL

Writes (appends):
  - memory/stars/{star_id}/published.md

Exit 0 on success, exit 1 on failure (with reason printed to stderr).
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

WORKSPACE = Path("/workspace")
RUNS_DIR = WORKSPACE / "memory" / "pipeline" / "runs"
STARS_DIR = WORKSPACE / "memory" / "stars"


def extract_title(draft_path: Path) -> str:
    for line in draft_path.read_text(encoding="utf-8").splitlines():
        m = re.match(r'^title:\s*["\']?(.+?)["\']?\s*$', line)
        if m:
            return m.group(1).strip()
    return "(untitled)"


def extract_angle(sources_path: Path) -> str:
    text = sources_path.read_text(encoding="utf-8")
    m = re.search(r"## Selected angle\s*\n(.+?)(\n##|\Z)", text, re.DOTALL)
    if m:
        return m.group(1).strip().split("\n")[0][:200]  # first line, max 200 chars
    return "(angle not found)"


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: update_star_history.py <run_id>", file=sys.stderr)
        sys.exit(1)

    run_id = sys.argv[1]
    run_dir = RUNS_DIR / run_id

    # Load state
    state_path = run_dir / "state.json"
    if not state_path.exists():
        print(f"state.json not found: {state_path}", file=sys.stderr)
        sys.exit(1)
    state = json.loads(state_path.read_text())
    star_id = state.get("star")
    star_label = state.get("star_label", "")
    if star_id is None:
        print("No 'star' field in state.json", file=sys.stderr)
        sys.exit(1)

    # Load published URL
    published_path = run_dir / "published.json"
    if not published_path.exists():
        print(f"published.json not found: {published_path}", file=sys.stderr)
        sys.exit(1)
    published = json.loads(published_path.read_text())
    if published.get("status") != "ok":
        print(f"Article not published (status={published.get('status')})", file=sys.stderr)
        sys.exit(1)
    url = published.get("url", "")

    # Extract title and angle
    draft_path = run_dir / "draft-v2.md"
    sources_path = run_dir / "curated-sources.md"
    title = extract_title(draft_path) if draft_path.exists() else "(untitled)"
    angle = extract_angle(sources_path) if sources_path.exists() else "(angle not found)"

    # Write to star history
    star_dir = STARS_DIR / str(star_id)
    star_dir.mkdir(parents=True, exist_ok=True)
    history_path = star_dir / "published.md"

    entry = (
        f"\n## {date.today().isoformat()} — {run_id}\n"
        f"**Title**: {title}\n"
        f"**Angle**: {angle}\n"
        f"**URL**: {url}\n"
    )

    if not history_path.exists():
        history_path.write_text(
            f"# Published Articles — Star {star_id}: {star_label}\n"
            + entry,
            encoding="utf-8",
        )
    else:
        with history_path.open("a", encoding="utf-8") as f:
            f.write(entry)

    print(f"Star history updated: {history_path}")
    print(f"  Title: {title}")
    print(f"  Angle: {angle[:80]}...")
    print(f"  URL:   {url}")


if __name__ == "__main__":
    main()
