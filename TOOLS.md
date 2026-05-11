# Tool Usage Notes

Tool signatures are provided automatically via function calling.
This file documents non-obvious constraints and Patria-specific patterns.

## File tools

- `edit_file` / `write_file` — create or update files in the workspace
- `read_file` — read files in the workspace
- `list_dir` — check what's there before assuming

## exec — Shell commands

- Timeout: 60s default. Use for git operations, Python scripts, pip installs.
- Blocked: `rm -rf`, `format`, `shutdown`, destructive disk ops.
- Output truncated at 10,000 characters.
- Use `exec` to commit articles to the articles git repo and push to GitHub Pages.

## web — Search

Use for:
- Verifying factual claims against primary sources
- EU legislation, European Commission press releases, Eurostat data
- Breaking geopolitical events
- Fact-checking specific figures, dates, quotes
- Monitoring Astra Europa, Volt, Ave Europa activity

### Source tier hierarchy

1. **Tier 1**: European Commission, European Parliament, Eurostat, EU member state governments, UN agencies, NATO, peer-reviewed academic sources
2. **Tier 2**: Reuters, AP, AFP, FT, Guardian, Le Monde, Der Spiegel, NRC, BBC, EUobserver, Politico Europe
3. **Tier 3**: Think tanks (ECFR, Bruegel, RAND), regional press
4. **Avoid**: Anonymous sources, Telegram channels, RT/Sputnik, obviously partisan outlets

**Rule**: Minimum 2 independent Tier-1/2 sources before publishing any factual claim.

## atproto — Bluesky

```python
import os
from atproto import Client

client = Client()
client.login(
    os.environ.get("BSKY_HANDLE", "nostrapatria.bsky.social"),
    os.environ.get("BSKY_APP_PASSWORD")
)
```

Credentials in `secrets/credentials.json` as fallback.

## LinkedIn API

```python
import os, requests

ACCESS_TOKEN = os.environ.get("LINKEDIN_ACCESS_TOKEN")
AUTHOR_URN = os.environ.get("LINKEDIN_AUTHOR_URN")  # urn:li:person:xxx or urn:li:organization:xxx

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0"
}
```

## Grok Image API (xAI)

```python
import os, requests, base64

API_KEY = os.environ.get("GROK_API_KEY")

response = requests.post(
    "https://api.x.ai/v1/images/generations",
    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    json={
        "model": "grok-imagine-image-quality",  # NOT grok-2-image (deprecated)
        "prompt": "...",
        "n": 1,
        "aspect_ratio": "16:9",   # header images; use "1:1" for social cards
        "response_format": "b64_json"
    },
    timeout=120
)
        "size": "1792x1024"  # header image
    }
)
image_url = response.json()["data"][0]["url"]
```

For social cards use `1024x1024`. For header images use `1792x1024`.

## GitHub Pages (website)

Articles are published to the Patria GitHub Pages repo.
Repo: `https://github.com/Nostra-patria/patria.git`
Repo URL also stored in `secrets/credentials.json` as `github_pages_repo`.

```bash
# Clone if not present
if [ ! -d "patria-site" ]; then
  git clone https://$GITHUB_TOKEN@github.com/Nostra-patria/patria.git patria-site/
fi

cd patria-site && git pull
# Write article file to articles/YYYY-MM/
git add . && git commit -m "article: [slug]" && git push
```

## Memory

- `memory/MEMORY.md` — persistent context, tracked topics, last run state
- `memory/LIBRARY.md` — article index: title, date, Star tags, URL, slug
