# Skill: Verifier

Independent fact-check of a finished draft. You do NOT use the research report — you verify claims on your own, from scratch. If the writer invented something that was never in the research, you catch it here.

## Anti-loop rule

**Strict execution order. Do not call read_file more than once per file.**
1. Read `{run_dir}/draft-v1.md` — exactly once. Extract all verifiable claims.
2. For each claim (max 8 total `web_fetch` calls): fetch, write batch result immediately with `edit_file`.
3. Write `VERDICT: PASS` or `VERDICT: FAIL` to `{run_dir}/verification-report.md`.
4. Call `python3 /workspace/tools/pipeline_complete.py verifier {run_dir}/verification-report.md`.

**Do NOT re-read draft-v1.md after step 1. Do NOT call web_fetch more than 8 times.**

## Pipeline I/O

- **Called by**: pipeline skill (step: verifier)
- **Input**: `{run_dir}/draft-v1.md`
- **Output**: `{run_dir}/verification-report.md`
- **Pass score**: 0.7 (no ❌ claims allowed; ⚠️ claims tolerated if < 3)
- **On FAIL**: writer is reset to retry — re-runs with verification.md as additional input

---

## Hard constraints

- **DO NOT read `02-research.json`** — you are an independent verifier. Using the research output defeats the purpose.
- **Max 8 `web_fetch` calls** — prioritise the most checkable claims. You cannot check everything; check what matters most.
- **Chunk your work** — verify in batches of 4 claims. Write each batch result to `verification.md` before moving to the next. If you time out, the partial report survives.
- **Stop after 8 fetches**, even if claims remain. Mark remaining claims as `⬜ not checked (limit reached)`.

---

## Step 1 — Extract claims

Read `{run_dir}/draft-v1.md`. Extract every verifiable claim:
- Specific statistics or numbers
- Named people and their titles/roles
- Dates of events
- Quotes (exact or paraphrased)
- Named legislation, treaties, votes, decisions
- Causal claims ("X caused Y", "X led to Z")

Do NOT extract:
- Editorial opinions explicitly labelled as such
- General background statements ("The EU has 27 member states")

Write the claim list immediately to `{run_dir}/verification-report.md`:

```markdown
# Verification Report — {run_id}

## Claims inventory
| # | Claim | Status |
|---|-------|--------|
| 1 | {claim text} | ⬜ pending |
| 2 | {claim text} | ⬜ pending |
...
```

---

## Step 2 — Verify in batches of 4

For each batch of 4 claims:
1. Identify the most authoritative source to check each claim (EU institutions, Reuters, FT, Eurostat, etc.)
2. Call `web_fetch` on that source
3. Mark each claim as:
   - `✅ verified` — source confirms the claim
   - `⚠️ uncertain` — source partially confirms, or wording differs, or source is Tier 3
   - `❌ contradicted` — source contradicts the claim, or claim appears fabricated
   - `⬜ not checked` — limit reached

Update `verification-report.md` after each batch — overwrite the status cells in the table.

---

## Step 3 — Write verdict

After all batches (or after 8 fetches), append to `verification-report.md`:

```markdown
## Verdict

- Verified ✅: {count}
- Uncertain ⚠️: {count}
- Contradicted ❌: {count}
- Not checked ⬜: {count}

**VERDICT: PASS** — No contradicted claims. Draft may proceed.
```

or:

```markdown
**VERDICT: FAIL** — {count} contradicted claim(s) found. Writer must revise.

### Claims requiring correction
| # | Claim | Issue |
|---|-------|-------|
| 3 | "..." | Contradicted by [source]: actual figure is X |
```

---

## Step 4 — Call pipeline_complete

```
exec: python3 /workspace/tools/pipeline_complete.py verifier {run_dir}/verification-report.md
```

Read the output. If "COMPLETE RETRY" or "COMPLETE FAIL" — stop. The pipeline will reset the writer step automatically and re-queue it.

---

## Scoring logic (applied by pipeline_complete.py)

```
❌ count = 0           → score = 1.0
❌ count = 0, ⚠️ ≥ 3  → score = 0.6
❌ count ≥ 1           → score = 0.0
VERDICT not found      → score = 0.0
```

Pass threshold: **0.7**
