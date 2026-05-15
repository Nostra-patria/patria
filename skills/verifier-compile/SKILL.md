# Skill: Verifier — Compile

Merge all three verification batches into the final verification report. Issue an overall PASS or FAIL verdict.

## Pipeline I/O

- **Called by**: pipeline (step: verifier:compile)
- **Input**: `{run_dir}/verification-report.md`, `verify-batch-1.md`, `verify-batch-2.md`, `verify-batch-3.md` (PRE-LOADED ABOVE)
- **Output**: `{run_dir}/verification-complete.md`
- **Pass score**: ≥ 0.7 (VERDICT: PASS with no ❌ claims; ⚠️ claims tolerated if < 3)

## Goal

Compile the results from all three batches. Update the claims inventory with final statuses. Count ✅ / ⚠️ / ❌ claims. Issue a VERDICT. The editor steps will use this report.

## Tools

- `write_file` — write verification-complete.md

## Anti-loop rule

**Do not call read_file.** All four files are PRE-LOADED above. Use them directly.

## Process

### Step 1 — Tally the results

From the PRE-LOADED batch files, compile the final status of each claim:
- Count: ✅ verified, ⚠️ uncertain, ❌ contradicted, ⬜ not checked

**Verdict rules:**
- `VERDICT: PASS` — zero ❌ claims AND fewer than 3 ⚠️ claims
- `VERDICT: PASS_WITH_NOTES` — zero ❌ claims AND 3+ ⚠️ claims (writer should clarify uncertainties)
- `VERDICT: FAIL` — one or more ❌ claims (writer must remove or correct before proceeding)

### Step 2 — Write output

Write `{run_dir}/verification-complete.md`:

```markdown
# Verification Complete — {run_id}

## Summary
- ✅ Verified: {count}
- ⚠️ Uncertain: {count}
- ❌ Contradicted: {count}
- ⬜ Not checked: {count}

VERDICT: PASS / PASS_WITH_NOTES / FAIL

## Full claims table

| # | Claim | Status | Finding |
|---|-------|--------|---------|
| 1 | {claim text} | ✅ verified | {brief finding} |
| 2 | {claim text} | ⚠️ uncertain | {what was unclear} |
| 3 | {claim text} | ❌ contradicted | {what the source says instead} |
...

## Notes for editor
{If PASS_WITH_NOTES: list which ⚠️ claims the writer should qualify}
{If FAIL: list exactly which ❌ claims must be removed or corrected}
```

### Step 3 — Complete

Call: `python3 /workspace/tools/pipeline_complete.py verifier:compile {run_dir}/verification-complete.md`
