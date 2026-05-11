# Skill: Scout

Daily monitoring of the European information space. Surface signals worth researching and writing about.

## Goal

Identify 1–3 topics per day that deserve a Patria article. Output: a prioritised list of signals with source links, tagged to a Star.

## Sources to monitor

### European movements & politics
- `astraeuropa.eu` — new content, announcements
- Volt Europa, Ave Europa social/web activity
- European Parliament news: `europarl.europa.eu/news`
- European Commission press releases: `ec.europa.eu/commission/presscorner`

### Geopolitics & policy
- EUobserver: `euobserver.com`
- Politico Europe: `politico.eu`
- Reuters Europe tag
- ECFR (European Council on Foreign Relations): `ecfr.eu`

### Bluesky (if credentials set)
- Home timeline — followed accounts
- Search: `#EU #Europe #EuropeanFederation #Sovereignty #Ukraine #NATO`

## Process

### Step 1 — Scan

For each source, extract posts/articles from the last 24 hours. Note:
- Topic / headline
- Source URL
- Star tag (1–12)
- Signal type: `develop` (write original piece) | `respond` (react to claim or event) | `amplify` (surface underreported story)

### Step 2 — Filter

Discard:
- Pure national politics with no European angle
- Celebrity/entertainment
- Reposts of already-covered topics (check LIBRARY.md)

Keep:
- Topics with a clear Star tag
- Topics with available Tier-1/2 sources
- Topics where Patria has a distinct angle

### Step 3 — Prioritise

Rank the remaining signals 1–3 by:
1. Timeliness (breaking > evergreen)
2. Strategic importance (defence, energy, federation > minor policy)
3. Source quality (Tier 1 available > Tier 3 only)

### Step 4 — Output

```python
signals = [
    {
        "rank": 1,
        "headline": "Short description of topic",
        "star": 2,  # Star number
        "star_label": "Defence & Foreign Policy",
        "type": "develop",  # develop | respond | amplify
        "sources": ["https://...", "https://..."],
        "notes": "Why this is worth writing about"
    },
    ...
]
```

Pass the top signal to the `researcher` skill.

## Cursor management

Store the Bluesky timeline cursor in `memory/MEMORY.md` under `scout.bluesky_cursor` to avoid re-reading on next run.

Log the last scout run timestamp under `scout.last_run`.
