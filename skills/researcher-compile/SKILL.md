# Skill: Researcher — Compile

Merge all four research runs into a single coherent research report. This is the document the writer will use.

## Pipeline I/O

- **Called by**: pipeline (step: researcher:compile)
- **Input**: `{run_dir}/research-q1.md`, `research-q2.md`, `research-q3.md`, `research-q4.md` (PRE-LOADED ABOVE)
- **Output**: `{run_dir}/research-report.md`
- **Pass score**: ≥ 0.6 (merged report with `## RESEARCH-COMPLETE` marker, min 300 words)

## Goal

Synthesise the four research runs into one structured report. Organise by key question, not by source. Remove duplicates. Preserve all specific quotes, statistics, and named facts. End with `## RESEARCH-COMPLETE`.

## Tools

- `write_file` — write research-report.md

## Anti-loop rule

**Do not call read_file.** All four research-q files are PRE-LOADED above. Use them directly.

## Process

### Step 1 — Review all four runs

From the PRE-LOADED research files:
- Note all findings, quotes, and named facts across all four runs
- Identify duplicates (same fact from multiple sources — keep the best citation)
- Note any gaps (questions where the research was inconclusive)

### Step 2 — Write the compiled report

Write `{run_dir}/research-report.md`:

```markdown
# Research Report — {run_id}

**Star**: {n} — {name}
**Angle**: {angle from research-plan.md or curated-sources.md}

## Key questions
{list the key questions from the research plan}

## Evidence

### Q1: {question}
{findings from research-q1.md — specific facts, quotes, named officials}

### Q2: {question}
{findings from research-q2.md}

### Q3: {question}
{findings from research-q3.md}

### Q4: {question or "Secondary context"}
{findings from research-q4.md}

## Key quotes
{Collect all direct quotes from all four runs here for easy writer access}
> "{exact quote}" — {name, title, source URL}

## Gaps and uncertainties
{Note any key questions that could not be answered from available sources}

## RESEARCH-COMPLETE
```

The `## RESEARCH-COMPLETE` marker is mandatory — without it the step will not pass scoring.

### Step 3 — Complete

Call: `python3 /workspace/tools/pipeline_complete.py researcher:compile {run_dir}/research-report.md`
