# Skill: Researcher — Question Run

Answer one assigned research question by fetching the designated source(s) and writing findings to disk immediately.

## Pipeline I/O

- **Called by**: pipeline (step: researcher:q1 / researcher:q2 / researcher:q3 / researcher:q4)
- **Input**: `{run_dir}/research-plan.md` + `{run_dir}/curated-sources.md` (PRE-LOADED ABOVE)
- **Output**: `{run_dir}/research-q{N}.md` — where N is the run number (1, 2, 3, or 4)
- **Pass score**: ≥ 0.5 (min 100 words, at least one source fetched)

## Goal

Answer the single question assigned to this run in the research plan. Fetch the designated source(s). Extract real quotes, statistics, and named facts. Write everything to your output file immediately — never buffer in memory.

## Tools

- `web_fetch` — fetch the designated source URL(s) (max 2 fetches per run)
- `write_file` / `edit_file` — write and append to the research-q{N}.md file

## Anti-loop rule

**Do not call read_file.** The research plan and curator brief are PRE-LOADED above. Identify your assigned question and source URLs from the PRE-LOADED content. Go directly to Step 1.

**Max 2 `web_fetch` calls per run.** Write after every fetch.

## Process

### Step 1 — Identify your assignment

From the PRE-LOADED `research-plan.md`:
- Find the section for your run number (researcher:q1, :q2, :q3, or :q4)
- Note the assigned question and source URL(s)

### Step 2 — Fetch and write (repeat per source)

1. Fetch the first assigned URL with `web_fetch`
2. Immediately write findings to `{run_dir}/research-q{N}.md` with `write_file`
3. If a second URL is assigned, fetch it and append with `edit_file`

Write after every single fetch. Do not fetch source 2 before writing source 1.

### Output format

```markdown
# Research — Q{N}: {question text}
Run: {run_id}

## Source: {URL}
**Fetched**: {date}

### Key findings
- {specific fact, quote, or statistic}
- {specific fact, quote, or statistic}
- {specific fact, quote, or statistic}

### Quotes
> "{exact quote}" — {name, title, source}

### Answer to question
{2–4 sentences directly answering the assigned question using the evidence above}
```

### Step 3 — Complete

Determine your run number N from the step name (q1=1, q2=2, q3=3, q4=4).

Call: `python3 /workspace/tools/pipeline_complete.py researcher:q{N} {run_dir}/research-q{N}.md`

Replace `{N}` with the actual number — e.g. for step `researcher:q2`:
`python3 /workspace/tools/pipeline_complete.py researcher:q2 {run_dir}/research-q2.md`
