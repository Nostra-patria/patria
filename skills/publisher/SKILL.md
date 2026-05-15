# Skill: Publisher

Publish a finished article + social posts to the website, Bluesky, and LinkedIn.

## Pipeline I/O

- **Called by**: pipeline skill (step 5)
- **Input**: `{run_dir}/draft-v2.md` + `{run_dir}/image.json`
- **Output**: write `{run_dir}/published.json`: `{ "url": "...", "bluesky_uris": [...] }`
- **Pass score**: 1.0 — git push must succeed and URL must be set

## Prerequisites

**CRITICAL: Check image.json FIRST.**

Before doing anything else, read `{run_dir}/image.json`. If the `status` field is NOT `"ok"`, **STOP and FAIL this step** — do not publish without a valid header image. Write to `published.json`: `{"status": "blocked", "reason": "image not ready", "image": image.json status}` and exit with score 0.

Check credentials before every publish attempt:

| Credential | Env var | Platform |
|---|---|---|
| Bluesky handle | `BSKY_HANDLE` | Bluesky |
| Bluesky app password | `BSKY_APP_PASSWORD` | Bluesky |
| LinkedIn access token | `LINKEDIN_ACCESS_TOKEN` | LinkedIn |
| LinkedIn author URN | `LINKEDIN_AUTHOR_URN` | LinkedIn |
| GitHub token | `GITHUB_TOKEN` | Website |
| GitHub Pages repo | `GITHUB_PAGES_REPO` | Website |

If a credential is missing: log to memory, publish to available platforms only, warn the operator.

---

## 1. Website (GitHub Pages)

**CRITICAL PATH RULE**: Articles must go into `docs/_posts/` — NOT `_posts/`. GitHub Pages serves from the `docs/` folder. Files in root `_posts/` are ignored.

Run these exact `exec` steps. Replace `SLUG` with the full filename slug (e.g. `2026-05-11-my-article`).

**Step 1 — Set up local clone:**
```bash
if [ ! -d /workspace/patria-site ]; then
  git clone https://$GITHUB_TOKEN@github.com/Nostra-patria/patria.git /workspace/patria-site
else
  git -C /workspace/patria-site remote set-url origin https://$GITHUB_TOKEN@github.com/Nostra-patria/patria.git
  git -C /workspace/patria-site pull --rebase origin main
fi
```

**Step 2 — Copy article into `docs/_posts/` (NOT `_posts/`):**
```bash
SLUG=YYYY-MM-DD-your-slug-here
RUN_DIR=/workspace/memory/pipeline/runs/$SLUG
mkdir -p /workspace/patria-site/docs/_posts/
cp $RUN_DIR/draft-v2.md /workspace/patria-site/docs/_posts/$SLUG.md
```

**Step 2b — Copy header image (REQUIRED if illustrator ran):**
```bash
# Image is at: /workspace/memory/media/YYYY-MM/$SLUG-header.png
# It MUST be copied to the repo before committing.
YYYY_MM=$(echo $SLUG | cut -c1-7)
IMG_SRC="/workspace/memory/media/$YYYY_MM/$SLUG-header.png"
IMG_DST="/workspace/patria-site/docs/assets/img/articles/$SLUG-header.png"
if [ -f "$IMG_SRC" ]; then
  mkdir -p /workspace/patria-site/docs/assets/img/articles/
  cp "$IMG_SRC" "$IMG_DST"
  echo "Image copied: $IMG_DST"
else
  echo "WARNING: no header image found at $IMG_SRC — article will publish without image"
fi
```

**Step 2c — Verify correct path and slug consistency:**
```bash
# 1. Article must be in docs/_posts/
if [ ! -f "/workspace/patria-site/docs/_posts/$SLUG.md" ]; then
  echo "FATAL: article is not at docs/_posts/$SLUG.md"
  echo "Check where you copied it. STOP HERE."
  echo "DO NOT change the git add command to match a wrong path."
  echo "DO NOT use _posts/ without docs/. Fix the cp command in Step 2."
  exit 1
fi
echo "OK: article confirmed at docs/_posts/$SLUG.md"

# 2. The image: field in frontmatter must match the actual image filename
FRONTMATTER_IMAGE=$(grep '^image:' /workspace/patria-site/docs/_posts/$SLUG.md | sed 's/.*articles\///' | tr -d "'\" ")
EXPECTED_IMAGE="${SLUG}-header.png"
if [ "$FRONTMATTER_IMAGE" != "$EXPECTED_IMAGE" ]; then
  echo "FATAL: image path mismatch in frontmatter"
  echo "  frontmatter says: $FRONTMATTER_IMAGE"
  echo "  expected:         $EXPECTED_IMAGE"
  echo "Fix the 'image:' field in the article to read:"
  echo "  image: /patria/assets/img/articles/$EXPECTED_IMAGE"
  exit 1
fi
echo "OK: image frontmatter matches slug"
```

If either check fails: fix the problem before continuing. Do **not** proceed to Step 3.

**Step 3 — Commit and push (article + image together):**
```bash
git -C /workspace/patria-site add docs/_posts/$SLUG.md
git -C /workspace/patria-site add docs/assets/img/articles/ 2>/dev/null || true
git -C /workspace/patria-site -c user.name="Patria" -c user.email="agent@patria" commit -m "article: $SLUG"
git -C /workspace/patria-site push origin main
```

After push, the article will be live at:
```
https://nostra-patria.github.io/patria/articles/YYYY/MM/slug/
```

The `image` frontmatter field in the article must point to:
```
/patria/assets/img/articles/YYYY-MM-DD-slug-header.png
```

---

## 2. Bluesky

```python
import os
from atproto import Client

client = Client()
client.login(os.environ["BSKY_HANDLE"], os.environ["BSKY_APP_PASSWORD"])

def post_thread_bluesky(posts: list[str]) -> list[str]:
    uris = []
    parent = None
    root = None

    for text in posts:
        if parent is None:
            response = client.send_post(text=text)
            root = {"uri": response.uri, "cid": response.cid}
            parent = root
        else:
            response = client.send_post(
                text=text,
                reply_to={"root": root, "parent": parent}
            )
            parent = {"uri": response.uri, "cid": response.cid}
        uris.append(response.uri)

    return uris
```

Parse the `bluesky_thread` block from the article's HTML comment at the bottom of the draft file:

```python
import re

def parse_bluesky_thread(md_content: str) -> list[str]:
    m = re.search(r'<!-- bluesky_thread\n(.+?)-->', md_content, re.DOTALL)
    if not m:
        return []
    block = m.group(1)
    posts = re.split(r'post\d+: \|\n', block)[1:]  # skip empty first
    return [p.strip() for p in posts if p.strip()]
```

Then call `post_thread_bluesky(parse_bluesky_thread(article_content))`.

---

## 3. LinkedIn

```python
import os, requests

def post_linkedin(text: str) -> str:
    """Post a text update. Returns post URN."""
    headers = {
        "Authorization": f"Bearer {os.environ['LINKEDIN_ACCESS_TOKEN']}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    payload = {
        "author": os.environ["LINKEDIN_AUTHOR_URN"],
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    response = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers=headers,
        json=payload
    )
    response.raise_for_status()
    return response.headers.get("x-restli-id", "")
```

Post the `linkedin` post from the copywriter output.

---

## Full publish flow

```python
def publish_all(article_slug, article_date, posts, images):
    results = {}

    # 1. Website
    results["website"] = publish_to_github(article_slug, article_date)

    # 2. Bluesky
    if os.environ.get("BSKY_APP_PASSWORD"):
        results["bluesky"] = post_thread_bluesky(posts["bluesky_thread"])

    # 3. LinkedIn
    if os.environ.get("LINKEDIN_ACCESS_TOKEN"):
        results["linkedin"] = post_linkedin(posts["linkedin"])

    return results
```

## After publishing

Update `memory/LIBRARY.md` with the published article URL.
Log the publish event in `memory/MEMORY.md` under `publisher.last_publish`.
