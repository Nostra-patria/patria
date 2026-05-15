# Skill: Curator — Angle

Select the editorial angle, define key questions, and write the researcher's brief. This is the editorial decision point — it determines what gets written.

## Pipeline I/O

- **Called by**: pipeline (step: curator:angle)
- **Input**: `{run_dir}/curator-ranked.md` (PRE-LOADED ABOVE)
- **Output**: `{run_dir}/curated-sources.md`
- **Pass score**: ≥ 0.7 (angle defined + minimum 3 key questions + minimum 3 primary sources)

## Goal

Using the ranked source list, choose one strong and specific angle that supports the Astra Europa Guiding Star frame. Define 3–5 key questions the article must answer. Write the researcher's brief — `curated-sources.md` is the only input the researcher will receive.

## Tools

- `write_file` — write curated-sources.md

## Anti-loop rule

**Do not call read_file.** The ranked sources are PRE-LOADED above. Use them directly.

## Process

### Step 1 — Select the angle

From the PRE-LOADED ranked sources, identify the top 3–5 sources by score. Select the single strongest angle:
- Has at least 2 Tier-1 sources covering it
- Connects a current development to the Astra Europa Guiding Star frame
- Offers an analytical perspective — not "X happened" but "X matters because Y"
- Can be answered in 700–900 words with the available sources

Do NOT invent an angle the sources cannot support. If sources are weak, choose the best available and flag it.

### Step 2 — Assign sources to primary / secondary

**Primary sources** (top 3–5 by score, directly covering the angle) — researcher reads all of these.

**Secondary sources** (rank 6–10, useful context) — researcher reads if time allows.

### Step 3 — Define key questions

Write 3–5 key questions the article must answer. Good questions are specific:
- ❌ "What is the EU doing about this?"
- ✅ "What specific legislative mechanism did the Commission propose, and which member states opposed it?"

Cover:
1. The immediate development (what happened, who decided what)
2. The institutional or treaty context
3. The member state fault lines
4. The historical precedent (what was tried before)
5. *(optional)* The critical or counter-argument

### Step 4 — Write output

Write `{run_dir}/curated-sources.md`:

```markdown
# Curated Sources — {run_id}

**Star**: {n} — {name}

## Selected angle
{1-paragraph description — specific, analytical, connected to the Astra Europa frame}

## Key questions this article must answer
1. {specific question}
2. {specific question}
3. {specific question}
4. {specific question — optional}
5. {specific question — optional}

## Primary sources
(Sources directly covering the angle — researcher reads all of these)
- {URL} — {why this source, what specific evidence it contains}
- {URL} — {why this source}
- {URL} — {why this source}

## Secondary sources
(Context sources — read if primary sources leave gaps)
- {URL} — {brief note}
- {URL} — {brief note}

## Out of scope
(Sources reviewed but not selected, with reason)
- {URL} — {why excluded}
```

### Step 5 — Complete

Call: `python3 /workspace/tools/pipeline_complete.py curator:angle {run_dir}/curated-sources.md`
