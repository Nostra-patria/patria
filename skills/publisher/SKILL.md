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

**CRITICAL PATH RULE**: Articles must go into `docs/_posts/` — NOT `_posts/`. GitHub Pages serves from the `docs/` folder. Files in root `_posts/` are ignored.

Run these exact `exec` steps. Replace `SLUG` with the full filename slug (e.g. `2026-05-11-my-article`).

**Step 1 — Set up local clone:**
```bash
TOKEN=$(printenv GITHUB_TOKEN)
if [ ! -d /workspace/patria-site ]; then
  git clone https://$TOKEN@github.com/Nostra-patria/patria.git /workspace/patria-site
else
  git -C /workspace/patria-site remote set-url origin https://$TOKEN@github.com/Nostra-patria/patria.git
  git -C /workspace/patria-site pull origin main
fi
```

**Step 2 — Copy article into `docs/_posts/` (NOT `_posts/`):**
```bash
SLUG=YYYY-MM-DD-your-slug-here
mkdir -p /workspace/patria-site/docs/_posts/
cp /workspace/memory/drafts/$SLUG.md /workspace/patria-site/docs/_posts/$SLUG.md
```

**Step 3 — Commit and push:**
```bash
git -C /workspace/patria-site add docs/_posts/$SLUG.md
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
