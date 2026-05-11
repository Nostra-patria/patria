# Skill: Researcher

Build a source-backed evidence base for a topic before writing. Output: a structured research object ready for the writer skill.

## Goal

Minimum 2 independent Tier-1/2 sources that directly support the main argument. No article without this.

## Process

### Step 1 — Define the angle

From the scout signal, extract:
- **Core claim or argument** — what will this article argue?
- **Star tag** — which of the 12 themes does this belong to?
- **Angle type** — original analysis | counter-narrative | deep dive | explainer

### Step 2 — Consult the library

Before searching the web, check `memory/LIBRARY.md` for prior Patria articles on this Star tag.
Pull relevant context. This prevents repetition and adds depth.

### Step 3 — Search for sources

Systematic search order:

1. **Primary sources** — official bodies first:
   - European Commission: `site:ec.europa.eu [topic]`
   - European Parliament: `site:europarl.europa.eu [topic]`
   - Eurostat: `site:ec.europa.eu/eurostat [topic]`
   - EDA (defence): `site:eda.europa.eu [topic]`
   - ECB (fiscal): `site:ecb.europa.eu [topic]`

2. **Wire agencies** — Reuters, AP, AFP for recent events

3. **Quality press** — FT, Guardian, Politico Europe, EUobserver, Der Spiegel

4. **Think tanks** — ECFR, Bruegel, RAND for analysis

### Step 4 — Evaluate each source

- **Tier** (1/2/3)
- **Relevance** — does it directly address the argument?
- **Recency** — flag if >2 years old
- **Independence** — not funded by the actor being discussed

### Step 5 — Output

```python
research = {
    "topic": "Short topic description",
    "star": 5,
    "star_label": "Energy Sovereignty",
    "angle": "Europe's energy dependency on LNG imports is rising, not falling",
    "argument": "Despite the 2022 pivot away from Russian gas, EU LNG imports from the US have created a new dependency. This undermines strategic autonomy.",
    "prior_library_context": [
        "2026-04-12 — Europe's Gas Dependency: The Russian Pivot (Star 5)",
    ],
    "sources": [
        {
            "title": "EU Energy in Figures 2025",
            "url": "https://ec.europa.eu/...",
            "tier": 1,
            "quote": "LNG imports rose 34% year-on-year...",
            "date": "2025-11-01"
        }
    ],
    "confidence": "high"  # high | medium | low
}
```

Pass to `writer` skill.
