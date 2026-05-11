# Skill: Illustrator

Generate a header image for a Patria article using the Grok Imagine API.

## API

Model: `grok-imagine-image-quality` (`grok-imagine-image-pro` retired May 15 2026 — do not use).

Run this via `exec`:

```bash
python3 - << 'EOF'
import os, requests, base64
from pathlib import Path

API_KEY = os.environ.get("GROK_API_KEY", "")
if not API_KEY:
    print("SKIP: GROK_API_KEY not set")
    exit(0)

SLUG = "YYYY-MM-DD-your-slug-here"   # <-- replace
PROMPT = "..."                         # <-- replace with article-specific prompt

out_dir = Path(f"/workspace/memory/media/{SLUG[:7]}")
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / f"{SLUG}-header.png"

response = requests.post(
    "https://api.x.ai/v1/images/generations",
    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    json={
        "model": "grok-imagine-image-quality",
        "prompt": PROMPT,
        "n": 1,
        "aspect_ratio": "16:9",
        "response_format": "b64_json"
    },
    timeout=120
)
response.raise_for_status()
b64 = response.json()["data"][0]["b64_json"]
out_path.write_bytes(base64.b64decode(b64))
print(f"Saved: {out_path}")
EOF
```

## Only generate the header image

One image per article — the `16:9` header. Skip social cards unless Bluesky/LinkedIn are active.

## Prompt construction

Keep prompts **visual, never textual** — do not ask for text or logos in the image.

```
Editorial photograph or graphic illustration: [specific visual scene from the article].
European context. [Mood: dramatic / analytical / hopeful / urgent].
No text. No logos. Cinematic lighting. High detail.
```

**Examples:**

| Article | Prompt |
|---|---|
| EU defence fragmentation | `"Aerial view of EU member state flags arranged as puzzle pieces with gaps between them. European Parliament in background. Dramatic overcast sky. No text."` |
| AI Act enforcement gap | `"Empty courtroom with a glowing AI chip on the judge's bench. European architectural style. Cold blue light. No text."` |
| EU-Mercosur trade deal | `"Container ship passing under a bridge made of EU and Mercosur flags. Golden hour light. Industrial scale. No text."` |

## File naming and storage

```
memory/media/YYYY-MM/YYYY-MM-DD-slug-header.png
```

The publisher will copy this to `patria-site/docs/assets/img/articles/` during the push step.
