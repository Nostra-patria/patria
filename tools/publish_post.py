#!/usr/bin/env python3
"""
Patria publisher — git push step.

Usage:
    python3 /workspace/tools/publish_post.py <run_id>

Does:
  1. Sets authenticated git remote on /workspace/patria-site
  2. Pulls latest
  3. Copies article (draft-v2.md) to docs/_posts/<run_id>.md
  4. If image.json status==ok: verifies image is already in patria-site (generate_image.py copies it)
  5. If image.json status==skipped/missing: strips image: from frontmatter
  6. Commits and pushes
  7. Writes published.json

Exit codes: 0 = pushed ok, 1 = error
"""
import os, sys, json, re, subprocess
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: publish_post.py <run_id>", file=sys.stderr)
    sys.exit(1)

RUN_ID   = sys.argv[1]
RUN_DIR  = Path(f"/workspace/memory/pipeline/runs/{RUN_ID}")
SITE_DIR = Path("/workspace/patria-site")
POSTS_DIR = SITE_DIR / "docs" / "_posts"
IMGS_DIR  = SITE_DIR / "docs" / "assets" / "img" / "articles"
PUBLISHED = RUN_DIR / "published.json"
REPO      = "Nostra-patria/patria"

def fail(msg: str):
    """Write published.json with FAILED status and exit 1."""
    PUBLISHED.write_text(json.dumps({"status": "FAILED", "reason": msg, "url": None, "bluesky_uris": [], "linkedin_urn": None}, indent=2))
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)

# ── credentials ──────────────────────────────────────────────────────────────
tok = os.environ.get("GITHUB_TOKEN", "")
if not tok:
    fail("GITHUB_TOKEN not set")

# ── image status ─────────────────────────────────────────────────────────────
img_json = RUN_DIR / "image.json"
img_status = "missing"
if img_json.exists():
    img_status = json.loads(img_json.read_text()).get("status", "missing")

print(f"Image status: {img_status}")

# ── git remote setup ─────────────────────────────────────────────────────────
remote = f"https://{tok}@github.com/{REPO}.git"

if not (SITE_DIR / ".git").exists():
    print("Cloning patria-site …")
    subprocess.run(["git", "clone", remote, str(SITE_DIR)], check=True)
else:
    subprocess.run(["git", "-C", str(SITE_DIR), "remote", "set-url", "origin", remote], check=True)
    subprocess.run(["git", "-C", str(SITE_DIR), "pull", "--rebase", "origin", "main"], check=True)

# ── copy article ─────────────────────────────────────────────────────────────
draft = RUN_DIR / "draft-v2.md"
if not draft.exists():
    fail(f"draft-v2.md not found at {draft}")

POSTS_DIR.mkdir(parents=True, exist_ok=True)
article_dst = POSTS_DIR / f"{RUN_ID}.md"
content = draft.read_text(encoding="utf-8")

# ── handle image in frontmatter ───────────────────────────────────────────────
if img_status == "ok":
    # generate_image.py already copied it; just verify
    img_file = IMGS_DIR / f"{RUN_ID}-header.png"
    if not img_file.exists():
        # try copying from memory/media
        year_month = RUN_ID[:7]
        src = Path(f"/workspace/memory/media/{year_month}/{RUN_ID}-header.png")
        if src.exists():
            IMGS_DIR.mkdir(parents=True, exist_ok=True)
            img_file.write_bytes(src.read_bytes())
            print(f"Copied image: {img_file}")
        else:
            print("WARNING: image status=ok but file not found — treating as skipped")
            img_status = "missing"

if img_status != "ok":
    # Strip image: line from frontmatter
    content = re.sub(r'^image:.*\n', '', content, flags=re.MULTILINE)
    print("Image line removed from frontmatter (no image available)")

article_dst.write_text(content, encoding="utf-8")
print(f"Article written: {article_dst}")

# ── ensure image: frontmatter is correct ─────────────────────────────────────
if img_status == "ok":
    post_content = article_dst.read_text(encoding="utf-8")
    expected_img_line = f"image: /patria/assets/img/articles/{RUN_ID}-header.png"
    if "image:" not in post_content:
        # Insert after slug: line (or last frontmatter field before closing ---)
        post_content = post_content.replace(
            f"slug: {RUN_ID}",
            f"slug: {RUN_ID}\n{expected_img_line}"
        )
        article_dst.write_text(post_content, encoding="utf-8")
        print(f"Added image frontmatter: {expected_img_line}")

# ── git commit & push ─────────────────────────────────────────────────────────
subprocess.run(["git", "-C", str(SITE_DIR), "add", str(article_dst)], check=True)
if img_status == "ok":
    subprocess.run(["git", "-C", str(SITE_DIR), "add", str(IMGS_DIR)], check=False)

result = subprocess.run(
    ["git", "-C", str(SITE_DIR),
     "-c", "user.name=Patria",
     "-c", "user.email=agent@patria",
     "commit", "-m", f"article: {RUN_ID}"],
    capture_output=True, text=True
)
if result.returncode != 0 and "nothing to commit" in result.stdout + result.stderr:
    print("Nothing new to commit — already up to date")
else:
    result.check_returncode()

subprocess.run(["git", "-C", str(SITE_DIR), "push", "origin", "main"], check=True)

url = f"https://nostra-patria.github.io/patria/articles/{RUN_ID[0:4]}/{RUN_ID[5:7]}/{RUN_ID[8:]}/"
PUBLISHED.write_text(json.dumps({
    "status": "ok",
    "url": url,
    "bluesky_uris": [],
    "linkedin_urn": None
}, indent=2))

print(f"Published: {url}")
