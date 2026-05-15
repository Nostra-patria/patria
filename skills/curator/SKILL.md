# Skill: Curator

Select the editorial angle and define the key questions the article must answer. This step determines what gets written — it is the editorial decision point.

## Pipeline I/O

- **Called by**: pipeline skill (step: curator)
- **Input**: `{run_dir}/scout-notes.md` + `{run_dir}/scout-notes-deepen.md`
- **Output**: `{run_dir}/curated-sources.md`
- **Pass score**: ≥ 0.7 (angle defined + minimum 3 key questions + minimum 3 primary sources)

## Goal

Combine up to 10 unique sources from both scout passes. Choose one strong, specific angle that supports the Astra Europa Guiding Star frame. Define 3–5 key questions the article must answer. The researcher will only work from this output — curated-sources.md is the researcher's brief.

## Tools

- `read_file` — read both scout files
- `write_file` — write curated-sources.md

## Anti-loop rule

**Strict execution order:**
1. Read `{run_dir}/scout-notes.md` — once.
2. Read `{run_dir}/scout-notes-deepen.md` — once.
3. Write `{run_dir}/curated-sources.md` with `write_file`.
4. Call `python3 /workspace/tools/pipeline_complete.py curator {run_dir}/curated-sources.md`.

**Do not call read_file more than twice total. Do not re-read any file.**

## Process

### Step 1 — Read both scout files

Read `{run_dir}/scout-notes.md` — note the Star, angle, and all URLs with summaries.
Read `{run_dir}/scout-notes-deepen.md` — note all NEW URLs (ignore any duplicate URLs already in scout-notes.md).

You now have up to 10 unique sources.

### Step 2 — Evaluate and rank

For each source, assess:
- **Depth**: does it contain specific facts, quotes, data, or named officials?
- **Relevance**: does it directly address the Guiding Star angle?
- **Credibility**: is it a Tier-1 source (EU institution, FT, Politico Europe, EUobserver, ECFR, Reuters)?
- **Balance**: are multiple perspectives represented across the full source pool?

**URL quality rule — MANDATORY**: A source URL is only usable if it points to a specific article, report, press release, or publication page — NOT a homepage root. Reject any URL where the path is empty or just `/` (e.g. `https://volteuropa.org/`, `https://federalists.eu/`). A valid URL has a non-trivial path, e.g. `https://ecfr.eu/article/2026-the-year-we-stop-pretending-its-just-a-phase/`. If a homepage URL is the only source for a movement or organisation, omit it from both Primary and Secondary lists and note it in Out of scope.

Rank all sources. Write the ranking immediately to curated-sources.md (Step 3 below) — do not hold it in memory.

### Step 3 — Choose the angle

Select the single strongest angle from the source pool. A strong angle:
- Has at least 2 Tier-1 sources covering it
- Connects a current development to the Astra Europa Guiding Star frame
- Offers an analytical perspective — not just "X happened" but "X matters because Y"
- Can be answered in 700–900 words with the available sources

Do NOT invent an angle that the sources cannot support. If sources are weak across the board, choose the best available and flag it.

### Step 4 — Define key questions

Write 3–5 key questions the article must answer. These questions drive the researcher. Good questions are specific:
- ❌ "What is the EU doing about this?"
- ✅ "What specific legislative mechanism did the Commission propose, and which member states opposed it?"

Questions should cover:
1. The immediate development (what happened, who decided what)
2. The institutional or treaty context
3. The member state fault lines
4. The historical precedent (what was tried before)
5. *(optional)* The critical or counter-argument

### Step 5 — Write output

Write `{run_dir}/curated-sources.md`:

```
# Curated Sources — {run_id}

**Star**: {n} — {name}

## Selected angle
{1-paragraph description of the chosen angle — specific, analytical, connected to the Astra Europa frame}

## Key questions this article must answer
1. {specific question}
2. {specific question}
3. {specific question}
4. {specific question — optional}
5. {specific question — optional}

## Primary sources
(Sources directly covering the chosen angle — researcher must read these)
- {URL} — {why this source, what specific evidence it contains}
- {URL} — {why this source}
- {URL} — {why this source}

## Secondary sources
(Supporting context, alternative perspectives — researcher should read if time allows)
- {URL} — {what supporting evidence this adds}
- {URL} — {what supporting evidence this adds}

## Out of scope
{What this article will NOT cover, and why — keep the researcher focused}
```

Write the output section by section, appending after each section. Do not buffer the entire file in memory.

### Step 6 — Stop

Report: `Curator done — Star {n}: angle selected, {x} key questions, {y} primary sources, {z} secondary sources.`

Do not start the researcher. Do not fetch any URLs.
