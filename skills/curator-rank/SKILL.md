# Skill: Curator — Rank

Evaluate and rank all sources from both scout passes. Produce a ranked source list that the angle step will use to select the editorial angle.

## Pipeline I/O

- **Called by**: pipeline (step: curator:rank)
- **Input**: `{run_dir}/scout-notes.md` + `{run_dir}/scout-notes-deepen.md` (PRE-LOADED ABOVE)
- **Output**: `{run_dir}/curator-ranked.md`
- **Pass score**: ≥ 0.5 (ranked list with scoring reasoning, min 80 words)

## Goal

Combine all unique sources from both scout passes. Score and rank each one. Do not select an angle yet — that is the next step (`curator:angle`). This step is pure evaluation.

## Tools

- `write_file` — write curator-ranked.md

## Anti-loop rule

**Do not call read_file.** Both scout files are PRE-LOADED above. Use them directly.

## Process

### Step 1 — Collect all sources

From the PRE-LOADED scout files, extract every source URL with its summary. Deduplicate — if a URL appears in both passes, keep it once.

### Step 2 — Score each source

For each source, assign a score 1–10 based on:

| Criterion | Weight | What to assess |
|---|---|---|
| **Depth** | 40% | Specific facts, quotes, data, named officials vs. generic commentary |
| **Relevance** | 35% | Directly addresses the Astra Europa Guiding Star angle |
| **Credibility** | 25% | Tier-1 = EU institutions, FT, Politico Europe, Reuters, EUobserver, ECFR. Tier-2 = national quality press. Tier-3 = blogs, advocacy. |

**URL quality rule — MANDATORY**: Reject any URL where the path is empty or just `/` (homepage root). A valid URL has a non-trivial path like `/article/2026-the-year-we-stop-pretending-its-just-a-phase/`. Mark rejected URLs as ❌ INVALID.

### Step 3 — Write output

Write `{run_dir}/curator-ranked.md`:

```markdown
# Curator Ranked Sources — {run_id}

**Star**: {n} — {name from scout-notes.md}

## Source rankings

| Rank | Score | URL | Depth | Relevance | Credibility | Notes |
|------|-------|-----|-------|-----------|-------------|-------|
| 1 | 9/10 | https://... | High | High | Tier-1 | Commissioner quoted directly |
| 2 | 7/10 | https://... | Medium | High | Tier-1 | Useful context, no direct quotes |
...

## Rejected sources
| URL | Reason |
|-----|--------|
| https://example.com/ | ❌ INVALID — homepage root |
```

### Step 4 — Complete

Call: `python3 /workspace/tools/pipeline_complete.py curator:rank {run_dir}/curator-ranked.md`
