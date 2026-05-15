# Skill: Researcher — Plan

Build the research plan from the curator's brief. Define exactly what each research question requires and which sources to use.

## Pipeline I/O

- **Called by**: pipeline (step: researcher:plan)
- **Input**: `{run_dir}/curated-sources.md` (PRE-LOADED ABOVE)
- **Output**: `{run_dir}/research-plan.md`
- **Pass score**: ≥ 0.5 (min 3 questions planned with source assignments, min 80 words)

## Goal

Turn the curator's key questions into a concrete research plan. Assign each question to one of the four research runs (q1–q4). Identify which source URLs are most likely to answer each question. The plan guides the researcher:q1–q4 steps.

## Tools

- `write_file` — write research-plan.md

## Anti-loop rule

**Do not call read_file.** The curator brief is PRE-LOADED above. Use it directly.

## Process

### Step 1 — Read the brief

From the PRE-LOADED `curated-sources.md`:
- Note the Star, angle, and all key questions
- Note which URLs are Primary vs Secondary sources
- Note what evidence each source is expected to contain

### Step 2 — Assign questions to runs

Distribute the key questions across q1–q4 (one question per run). If there are fewer than 4 questions, merge or split as needed:
- q1 — the most important question (institutional/legal mechanism)
- q2 — political fault lines / member state positions
- q3 — historical precedent / context
- q4 — counter-argument or critical perspective (if applicable)

Assign the best matching source URL(s) to each run.

### Step 3 — Write output

Write `{run_dir}/research-plan.md`:

```markdown
# Research Plan — {run_id}

**Star**: {n} — {name}
**Angle**: {angle from curated-sources.md}

## Run assignments

### researcher:q1 — {question}
**Sources**: {URL(s) to fetch}
**Expected evidence**: {what we expect to find}

### researcher:q2 — {question}
**Sources**: {URL(s) to fetch}
**Expected evidence**: {what we expect to find}

### researcher:q3 — {question}
**Sources**: {URL(s) to fetch}
**Expected evidence**: {what we expect to find}

### researcher:q4 — {question or "secondary context"}
**Sources**: {URL(s) to fetch}
**Expected evidence**: {what we expect to find}
```

### Step 4 — Complete

Call: `python3 /workspace/tools/pipeline_complete.py researcher:plan {run_dir}/research-plan.md`
