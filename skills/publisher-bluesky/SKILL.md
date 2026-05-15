# Skill: Publisher — Bluesky

Post the article thread to Bluesky. Runs after publisher:post confirms the article is live.

## Pipeline I/O

- **Called by**: pipeline (step: publisher:bluesky)
- **Input**: `{run_dir}/draft-v2.md` + `{run_dir}/image.json` + `{run_dir}/published.json`
- **Output**: `{run_dir}/bluesky.json`: `{ "status": "ok", "uris": [...] }`
- **Pass score**: 1.0 on success, 0.0 on hard failure (wrong credentials, API down)

## Prerequisites

Check `{run_dir}/published.json` — if `status != "ok"` or `url` is missing, stop and call pipeline_complete with score 0.0 and reason "article not published yet".

Credentials needed:
- `BSKY_HANDLE` — Bluesky handle (e.g. `nostrapatria.bsky.social`)
- `BSKY_APP_PASSWORD` — Bluesky app password

If either is missing, call pipeline_complete with score 0.0 and reason "missing Bluesky credentials".

---

## Step 1 — Parse the thread

Read `{run_dir}/draft-v2.md`. Extract the `<!-- bluesky_thread -->` block:

```python
import re

def parse_bluesky_thread(md_content: str) -> list[str]:
    m = re.search(r'<!-- bluesky_thread\n(.+?)-->', md_content, re.DOTALL)
    if not m:
        return []
    block = m.group(1)
    posts = re.split(r'post\d+: \|\n', block)[1:]  # skip empty first split
    return [p.strip() for p in posts if p.strip()]
```

If the result is empty, call pipeline_complete with score 0.0 and reason "no bluesky_thread block in draft-v2.md".

---

## Step 2 — Get image path

Read `{run_dir}/image.json`:
- `status == "ok"` → use the `path` field as `image_path`
- Any other status, or file missing → set `image_path = None`

---

## Step 3 — Post the thread

```python
import os, re
from atproto import Client, models

client = Client()
client.login(os.environ["BSKY_HANDLE"], os.environ["BSKY_APP_PASSWORD"])

def make_facets(text: str) -> list:
    """Detect URLs in text and return Bluesky link facets (byte-accurate)."""
    facets = []
    for match in re.finditer(r'https?://[^\s]+', text):
        url = match.group(0)
        start_byte = len(text[:match.start()].encode('utf-8'))
        end_byte   = len(text[:match.end()].encode('utf-8'))
        facets.append(
            models.AppBskyRichtextFacet.Main(
                features=[models.AppBskyRichtextFacet.Link(uri=url)],
                index=models.AppBskyRichtextFacet.ByteSlice(
                    byte_start=start_byte,
                    byte_end=end_byte
                )
            )
        )
    return facets

def post_thread(posts: list[str], image_path: str | None = None) -> list[str]:
    uris = []
    parent = None
    root = None

    for i, text in enumerate(posts):
        embed = None
        facets = make_facets(text) or None

        # Attach header image to the first post only
        if i == 0 and image_path:
            try:
                with open(image_path, "rb") as f:
                    img_data = f.read()
                blob = client.upload_blob(img_data)
                embed = models.AppBskyEmbedImages.Main(
                    images=[models.AppBskyEmbedImages.Image(
                        alt="Article header image",
                        image=blob.blob
                    )]
                )
            except Exception:
                embed = None  # image failed — still post text

        if parent is None:
            response = client.send_post(text=text, embed=embed, facets=facets)
            root = {"uri": response.uri, "cid": response.cid}
            parent = root
        else:
            response = client.send_post(
                text=text,
                reply_to={"root": root, "parent": parent},
                facets=facets
            )
            parent = {"uri": response.uri, "cid": response.cid}
        uris.append(response.uri)

    return uris
```

Call `post_thread(posts, image_path=image_path)`.

---

## Step 4 — Write bluesky.json

On success:
```json
{ "status": "ok", "uris": ["at://...", "at://...", ...] }
```

On failure:
```json
{ "status": "failed", "reason": "..." }
```

---

## Step 5 — Update memory

After a successful post, append to `memory/LIBRARY.md`:
```
- [{article title}]({url}) — Bluesky: {first_uri}
```

---

## Step 6 — Report and stop

Report: `Publisher Bluesky done — {n} posts in thread, first URI: {uris[0]}`

Do not start any other step.
