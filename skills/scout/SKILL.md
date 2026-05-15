# Skill: Scout

First scouting pass. Find 5 real sources for the current Astra Europa Guiding Star. No fetching — URLs and summaries only.

## Pipeline I/O

- **Called by**: pipeline skill (step: scout)
- **Input**: `python3 /workspace/tools/scoreboard_check.py` — provides STAR, ANGLE, THEMES
- **Output**: `{run_dir}/scout-notes.md`
- **Pass score**: ≥ 0.5 (at least 3 sources found)

## Goal

Collect 5 real, current URLs on the assigned Astra Europa Guiding Star. You are building a source pool — not writing an article. Do not fetch page content. Do not form opinions. Just find URLs and write one-sentence summaries.

## Tools

- `web_search` — 5 calls maximum
- `write_file` — write scout-notes.md

## Process

### Step 1 — Read the assignment

Run: `python3 /workspace/tools/scoreboard_check.py`

This prints three lines:
```
STAR=<n> NAME="<name>" COUNT=<n>
ANGLE="<editorial frame>"
THEMES=<keyword1>, <keyword2>, ...
```

Note the STAR number, NAME, ANGLE, and THEMES. This is your search brief.

### Step 1b — Check existing articles for this star

Read `memory/stars/{STAR}/published.md` (where `{STAR}` is the number from Step 1).

If the file exists: note every **Angle** listed. Your proposed sources must support an angle that is **structurally different** from all of them. The same topic can recur, but the argument, institutional focus, or policy mechanism must be distinct. Briefly state in your scout notes how your angle differs.

If the file does not exist: this is the first article for this star — no constraint.

### Step 2 — Search (max 5 calls)

Use the THEMES as search queries. Vary each search to cover different facets:
- Search 1: most urgent recent development (e.g. `"<Theme1> EU 2026"`)
- Search 2: institutional angle (Commission, Parliament, Council, treaty)
- Search 3: member state positions or fault lines
- Search 4: critical or opposition perspective
- Search 5: background or historical context

Rules:
- Only keep results from the last 12 months where possible
- Prefer: EU institutions, Politico Europe, EUobserver, Financial Times, The Guardian, ECFR, Reuters
- Avoid: opinion blogs, tabloids, paywalled sources with no preview, duplicate outlets
- Stop at 5 searches — do not go beyond

### Step 3 — Write output

Write `{run_dir}/scout-notes.md`:

```
# Scout Notes — {run_id}

**Star**: {n} — {name}
**Angle**: {ANGLE}
**Themes**: {THEMES}
**Differentiation**: {1 sentence: how this angle differs from previous articles, or "First article for this star"}

## Sources

1. {URL} — {1-sentence summary of what this source covers}
2. {URL} — {1-sentence summary}
3. {URL} — {1-sentence summary}
4. {URL} — {1-sentence summary}
5. {URL} — {1-sentence summary}
```

Write at least 3 sources. If a search returns nothing useful, note `(no useful result)` and move on — do not repeat the same search with minor variation.

### Step 4 — Stop

Report: `Scout done — Star {n}: {name}, {x} sources found.`

Do not read the URLs. Do not fetch. Do not start the next step. The curator takes over.
