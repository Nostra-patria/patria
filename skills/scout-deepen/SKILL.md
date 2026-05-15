# Skill: Scout II (Deepen)

Second scouting pass. Find 5 more sources on the same Guiding Star — from different angles than Scout I. No fetching — URLs and summaries only.

## Pipeline I/O

- **Called by**: pipeline skill (step: scout-deepen)
- **Input**: `{run_dir}/scout-notes.md` — read to know the Star, angle, and which URLs are already found
- **Output**: `{run_dir}/scout-notes-deepen.md`
- **Pass score**: ≥ 0.5 (at least 3 new sources found)

## Goal

Extend the source pool with 5 new, unique URLs that Scout I did not find. Scout I searched for recent developments and institutional angles. Scout II searches deeper: think tanks, academic sources, national government positions, NGOs, and alternative framings of the same Star.

## Tools

- `read_file` — read scout-notes.md
- `web_search` — 5 calls maximum
- `write_file` — write scout-notes-deepen.md

## Process

### Step 1 — Read Scout I output

Read `{run_dir}/scout-notes.md`. Note:
- The Star number, name, and angle
- All URLs already found — do not duplicate these

### Step 2 — Search (max 5 calls)

Search for the same Star theme but from angles Scout I did not cover:
- Search 1: think tank or academic perspective (ECFR, Bruegel, Bertelsmann, LSE, Carnegie Europe)
- Search 2: national government position — pick a large or dissenting member state
- Search 3: civil society or NGO angle (Transparency International, EEB, Amnesty Europe, etc.)
- Search 4: criticism or counter-argument to the Astra Europa position on this Star
- Search 5: historical precedent or long-arc context (what has been tried before, what failed)

Rules:
- Skip any URL already in scout-notes.md
- Prefer sources not already used in Scout I
- Same quality filter: EU institutions, Politico Europe, EUobserver, FT, Guardian, ECFR preferred
- Stop at 5 searches

### Step 3 — Write output

Write `{run_dir}/scout-notes-deepen.md`:

```
# Scout Notes (Deepen) — {run_id}

**Star**: {n} — {name}
**Angle**: {same angle as Scout I}

## New Sources (not in Scout I)

1. {URL} — {1-sentence summary}
2. {URL} — {1-sentence summary}
3. {URL} — {1-sentence summary}
4. {URL} — {1-sentence summary}
5. {URL} — {1-sentence summary}

## Duplicate URLs skipped
{list any URLs found that were already in scout-notes.md — so curator knows}
```

Write at least 3 new sources. If fewer than 3 new sources are found after 5 searches, note that and stop — do not manufacture sources.

### Step 4 — Stop

Report: `Scout II done — Star {n}: {x} new sources found. Curator can now select from {total} combined sources.`

Do not fetch URLs. Do not start the next step.
