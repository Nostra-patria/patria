# Skill: Publisher

Publish a finished article + social posts to the website, Bluesky, and LinkedIn.

## Prerequisites

Check before every publish attempt:

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

Use Python + subprocess — do NOT use shell scripts. The `GITHUB_TOKEN` is available via `os.environ`.

```python
import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

def publish_website(slug: str) -> str:
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        return "SKIP: GITHUB_TOKEN not set"

    repo_url = f"https://{token}@github.com/Nostra-patria/patria.git"
    repo_dir = Path("/workspace/patria-site")

    # Clone or pull
    if not repo_dir.exists():
        subprocess.run(["git", "clone", repo_url, str(repo_dir)], check=True)
    else:
        subprocess.run(["git", "-C", str(repo_dir), "pull", "origin", "main"], check=True)

    # Copy article
    src = Path(f"/workspace/memory/drafts/{slug}.md")
    dst = repo_dir / "docs" / "_posts" / f"{slug}.md"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

    # Copy images if they exist
    media_dir = Path("/workspace/memory/media")
    img_dst = repo_dir / "docs" / "assets" / "img" / "articles"
    img_dst.mkdir(parents=True, exist_ok=True)
    for ext in ("header.png", "social.png"):
        img_src = next(media_dir.rglob(f"{slug}-{ext}"), None)
        if img_src:
            shutil.copy2(img_src, img_dst / img_src.name)

    # Git commit + push
    env = {**os.environ, "GIT_AUTHOR_NAME": "Patria", "GIT_AUTHOR_EMAIL": "agent@patria"}
    subprocess.run(["git", "-C", str(repo_dir), "add", "-A"], check=True, env=env)
    subprocess.run(["git", "-C", str(repo_dir), "commit", "-m", f"article: {slug}"], check=True, env=env)
    subprocess.run(["git", "-C", str(repo_dir), "push", "origin", "main"], check=True, env=env)

    year, month = slug[:4], slug[5:7]
    url_slug = slug[11:]  # strip YYYY-MM-DD-
    return f"https://nostra-patria.github.io/patria/articles/{year}/{month}/{url_slug}/"
```

Article URL after push (Jekyll builds automatically on GitHub Pages):
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

Post the `bluesky_thread` from the copywriter output.

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
