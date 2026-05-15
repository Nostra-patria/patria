# Skill: Verifier — Run 1 (Claims Inventory)

Extract every verifiable claim from the finished draft and build the claims inventory. This is the input for the three verification batch runs.

## Pipeline I/O

- **Called by**: pipeline (step: verifier:run1)
- **Input**: `{run_dir}/draft-v1.md` + `{run_dir}/curated-sources.md` (PRE-LOADED ABOVE)
- **Output**: `{run_dir}/verification-report.md`
- **Pass score**: ≥ 0.5 (claims inventory table present, min 150 words)

## Goal

Read the draft and produce a complete numbered inventory of every verifiable claim. Do NOT verify anything yet — that is the job of verifier:check1, check2, check3. This step only extracts and lists.

## Tools

- `write_file` — write verification-report.md

## Anti-loop rule

**Do not call read_file.** The draft and curator sources are PRE-LOADED above. Use them directly.

## Process

### Step 1 — Extract claims

From the PRE-LOADED `draft-v1.md`, extract every verifiable claim:

**Include:**
- Specific statistics or numbers
- Named people and their titles/roles
- Dates of events, votes, decisions
- Exact or paraphrased quotes attributed to named people
- Named legislation, treaties, articles, votes
- Causal claims ("X caused Y", "X led to Z")

**Exclude:**
- Editorial opinions explicitly labelled as such ("Patria's view:", "The data suggests...")
- General background statements ("The EU has 27 member states")
- Unattributed analysis

Aim for 8–15 claims total. If more than 15 exist, prioritise the most specific and most checkable.

### Step 2 — Split into batches

Divide the claims into three groups:
- **Batch 1** (claims 1–N/3): institutional/legal claims
- **Batch 2** (claims N/3+1–2N/3): political/factual claims
- **Batch 3** (claims 2N/3+1–end): quote and date claims

### Step 3 — Write output

Write `{run_dir}/verification-report.md`:

```markdown
# Verification Report — {run_id}

## Claims inventory

| # | Claim | Type | Batch | Status |
|---|-------|------|-------|--------|
| 1 | {exact claim text from draft} | legislative | 1 | ⬜ pending |
| 2 | {exact claim text} | statistic | 1 | ⬜ pending |
| 3 | {exact claim text} | quote | 2 | ⬜ pending |
| 4 | {exact claim text} | date | 2 | ⬜ pending |
...

## Batches

- **Batch 1**: claims {list}
- **Batch 2**: claims {list}
- **Batch 3**: claims {list}
```

### Step 4 — Complete

Call: `python3 /workspace/tools/pipeline_complete.py verifier:run1 {run_dir}/verification-report.md`
