#!/usr/bin/env python3
"""
Patria image generator — called by the illustrator pipeline step.

Usage:
    python3 /workspace/tools/generate_image.py <run_id> "<prompt>"

Writes:
    /workspace/memory/pipeline/runs/<run_id>/image.json
    /workspace/memory/media/YYYY-MM/<run_id>-header.png
    /workspace/patria-site/docs/assets/img/articles/<run_id>-header.png

Exit codes: 0 = ok or skipped, 1 = error
"""
import os, sys, requests, base64, json
from pathlib import Path

if len(sys.argv) < 3:
    print("Usage: generate_image.py <run_id> <prompt>", file=sys.stderr)
    sys.exit(1)

RUN_ID = sys.argv[1]
PROMPT = sys.argv[2]

API_KEY = os.environ.get("GROK_API_KEY", "")
RUN_DIR = Path(f"/workspace/memory/pipeline/runs/{RUN_ID}")
image_json_path = RUN_DIR / "image.json"

if not API_KEY:
    print("SKIP: GROK_API_KEY not set")
    image_json_path.write_text(json.dumps({
        "status": "skipped",
        "reason": "GROK_API_KEY not set",
        "path": None
    }, indent=2))
    sys.exit(0)

YEAR_MONTH = RUN_ID[:7]   # e.g. 2026-05
out_dir = Path(f"/workspace/memory/media/{YEAR_MONTH}")
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / f"{RUN_ID}-header.png"

site_img = Path(f"/workspace/patria-site/docs/assets/img/articles/{RUN_ID}-header.png")
site_img.parent.mkdir(parents=True, exist_ok=True)

print(f"Generating image for {RUN_ID} …")
try:
    response = requests.post(
        "https://api.x.ai/v1/images/generations",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "grok-imagine-image-quality",
            "prompt": PROMPT,
            "n": 1,
            "aspect_ratio": "16:9",
            "response_format": "b64_json"
        },
        timeout=180
    )
    response.raise_for_status()
except requests.HTTPError as e:
    print(f"ERROR: Grok API returned {e.response.status_code}: {e.response.text[:200]}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)

img_bytes = base64.b64decode(response.json()["data"][0]["b64_json"])
out_path.write_bytes(img_bytes)
site_img.write_bytes(img_bytes)

image_json_path.write_text(json.dumps({
    "status": "ok",
    "path": str(out_path),
    "size_bytes": len(img_bytes),
    "model": "grok-imagine-image-quality",
    "prompt": PROMPT
}, indent=2))

print(f"OK: {out_path} ({len(img_bytes):,} bytes)")
