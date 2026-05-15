# Skill: Grounder

Internal consistency check. You verify that every factual claim in the draft can be traced back to the research report. No web access — this is a pure file comparison. If the writer drifted from the research and introduced facts that were never in `02-research.json`, you catch it here.
## Anti-loop rule

**Strict execution order. No web access. Only 2 read_file calls total.**
1. Read `{run_dir}/draft-v1.md` — exactly once.
2. Read `{run_dir}/research-report.md` — exactly once.
3. Compare claims to research, writing each batch result immediately with `edit_file`.
4. Write `VERDICT: GROUNDED` or `VERDICT: FAIL` to `{run_dir}/grounding-report.md`.
5. Call `python3 /workspace/tools/pipeline_complete.py grounder {run_dir}/grounding-report.md`.

**You have read all files you need after step 2. Do NOT call read_file again.**
## Pipeline I/O

- **Called by**: pipeline skill (step: grounder)
- **Input**: `{run_dir}/draft-v1.md` AND `{run_dir}/research-report.md`
- **Output**: `{run_dir}/grounding-report.md`
- **Pass score**: 1.0 (PASS verdict only — any ungrounded claim is a FAIL)
- **On FAIL**: writer is reset to retry — re-runs with grounding.md as additional input

---

## Hard constraints

- **NO `web_search`** — you are comparing two files. You have no need for the internet.
- **NO `web_fetch`** — same reason.
- **Only tools allowed**: `read_file`, `write_file`, `exec` (for pipeline_complete only)
- **Chunk your work** — check 5 claims per batch. Write each batch result before moving on.

---

## Step 1 — Load both files

Read `{run_dir}/draft-v1.md` and `{run_dir}/research-report.md`.

Extract every factual claim from the draft (same definition as verifier — specific numbers, names, dates, quotes, legislation references, causal claims).

Write immediately to `{run_dir}/grounding-report.md`:

```markdown
# Grounding Report — {run_id}

## Claims inventory
| # | Claim from draft | Grounded? |
|---|-----------------|-----------|
| 1 | {claim} | ⬜ pending |
| 2 | {claim} | ⬜ pending |
...
```

---

## Step 2 — Check each claim against research-report

For each batch of 5 claims, scan `research-report.md` for a matching source, quote, or data point.

Mark each claim:
- `✅ grounded` — the claim can be directly traced to a source entry in research-report.md (matching quote, URL, or data point)
- `⚠️ inferred` — the claim is a reasonable inference from the research, but not stated explicitly
- `❌ ungrounded` — the claim does not appear in the research at all, or contradicts it — this means the writer invented it

Update `grounding-report.md` after each batch.

---

## Step 3 — Write verdict

```markdown
## Verdict

- Grounded ✅: {count}
- Inferred ⚠️: {count}
- Ungrounded ❌: {count}

**VERDICT: PASS** — All claims trace back to the research report.
```

or:

```markdown
**VERDICT: FAIL** — {count} ungrounded claim(s). Writer must revise using only the research report.

### Ungrounded claims (writer must remove or replace these)
| # | Claim | Issue |
|---|-------|-------|
| 4 | "..." | Not found in research. Nearest research finding: "{actual research finding}" |
```

The "nearest research finding" helps the writer find the correct fact to use instead.

---

## Step 4 — Call pipeline_complete

```
exec: python3 /workspace/tools/pipeline_complete.py grounder {run_dir}/grounding-report.md
```

If "COMPLETE RETRY" or "COMPLETE FAIL" — stop immediately. The pipeline will reset the writer and re-queue it.

---

## Scoring logic (applied by pipeline_complete.py)

```
VERDICT: PASS   → score = 1.0
VERDICT: FAIL   → score = 0.0
No verdict line → score = 0.0
```

Pass threshold: **1.0** — no ungrounded claims permitted.
