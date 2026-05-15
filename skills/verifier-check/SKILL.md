# Skill: Verifier — Check Batch

Verify one batch of claims from the inventory. Fetch the authoritative sources. Update the status of each claim. Write immediately after every fetch.

## Pipeline I/O

- **Called by**: pipeline (step: verifier:check1 / verifier:check2 / verifier:check3)
- **Input**: `{run_dir}/verification-report.md` + `{run_dir}/draft-v1.md` (PRE-LOADED ABOVE)
- **Output**: `{run_dir}/verify-batch-{N}.md` — where N is the batch number (1, 2, or 3)
- **Pass score**: ≥ 0.5 (batch result file present with status markers)

## Goal

Verify the claims assigned to your batch. Fetch the most authoritative source for each claim. Mark each claim as ✅ verified, ⚠️ uncertain, or ❌ contradicted. Write results immediately — never buffer.

## Tools

- `web_fetch` — fetch authoritative sources (max 3 fetches per batch)
- `write_file` / `edit_file` — write and append to verify-batch-{N}.md

## Anti-loop rule

**Do not call read_file.** The inventory and draft are PRE-LOADED above. Identify your batch from the PRE-LOADED `verification-report.md`. Go directly to Step 1.

**Max 3 `web_fetch` calls per batch.** Write after every fetch.

## Process

### Step 1 — Identify your batch

From the PRE-LOADED `verification-report.md`:
- Find the claims assigned to your batch number (1, 2, or 3)
- Note the claim text for each

### Step 2 — Verify each claim

For each claim in your batch:
1. Identify the most authoritative source to check it (EU institutions, Reuters, FT, Eurostat, etc.)
2. Fetch with `web_fetch`
3. Immediately write the result to your batch file
4. Mark the claim:
   - `✅ verified` — source confirms the claim
   - `⚠️ uncertain` — source partially confirms, or wording differs, or source is Tier 3
   - `❌ contradicted` — source contradicts the claim, or claim appears fabricated
   - `⬜ not checked` — fetch limit reached

### Output format

Write `{run_dir}/verify-batch-{N}.md`:

```markdown
# Verification Batch {N} — {run_id}

## Results

### Claim {number}: {claim text}
**Source checked**: {URL}
**Status**: ✅ verified / ⚠️ uncertain / ❌ contradicted
**Finding**: {1-2 sentences — what the source says about this claim}

### Claim {number}: {claim text}
**Source checked**: {URL}
**Status**: {status}
**Finding**: {finding}

...
```

Write after each claim — do not wait until all claims are done.

### Step 3 — Complete

Determine your batch number N from the step name (check1=1, check2=2, check3=3).

Call: `python3 /workspace/tools/pipeline_complete.py verifier:check{N} {run_dir}/verify-batch-{N}.md`

Replace `{N}` with the actual number — e.g. for step `verifier:check2`:
`python3 /workspace/tools/pipeline_complete.py verifier:check2 {run_dir}/verify-batch-2.md`
