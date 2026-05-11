# Skill: Illustrator

Generate a header image and social card for a Patria article using the Grok image API.

## API

```python
import os, requests, base64
from pathlib import Path

API_KEY = os.environ.get("GROK_API_KEY")

def generate_image(prompt: str, size: str = "1792x1024") -> bytes:
    response = requests.post(
        "https://api.x.ai/v1/images/generations",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "grok-2-image",
            "prompt": prompt,
            "n": 1,
            "size": size,
            "response_format": "b64_json"
        }
    )
    response.raise_for_status()
    b64 = response.json()["data"][0]["b64_json"]
    return base64.b64decode(b64)
```

## Sizes

- **Header image**: `1792x1024` — wide format, used at top of article on website
- **Social card**: `1024x1024` — square, used on Bluesky and LinkedIn posts

## Prompt construction

Build the prompt from the article metadata. Keep prompts visual, not textual — do not ask for text in the image.

### Header image prompt template
```
A high-quality editorial photograph or graphic illustration representing [topic].
European political context. [Mood: dramatic / hopeful / urgent / analytical].
No text. No logos. Photorealistic or graphic design style.
[Specific visual element from the article, e.g.: "European Parliament building at dusk", "interconnected energy grids across a map of Europe"]
```

### Social card prompt template
```
A bold, graphic visual representing [one-word concept from article].
Minimalist. European aesthetic. Strong contrast. No text. No logos.
Suitable for social media.
```

## Examples

**Article**: "Europe's LNG Trap" (Star 5 — Energy)
- Header: `"Editorial illustration: LNG tanker docked at a European port. Industrial. Slightly ominous. No text."`
- Social: `"Minimalist graphic: chain link connecting a gas flame to a European map. Bold blue and gold palette. No text."`

## File naming

```
YYYY-MM-DD-slug-header.png
YYYY-MM-DD-slug-social.png
```

## Storage

Save to `memory/media/YYYY-MM/`.

When promoted to standalone with a GitHub Pages site, also commit images to `patria-site/images/articles/YYYY-MM/`.

## Output

```python
images = {
    "header": "memory/media/YYYY-MM/YYYY-MM-DD-slug-header.png",
    "social": "memory/media/YYYY-MM/YYYY-MM-DD-slug-social.png"
}
```

Pass to `publisher`.
