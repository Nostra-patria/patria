# Skill: Referee

Score the finished draft. Approve it, route it back for targeted repair, or reject it after two failed attempts. The referee never loops — it either passes or it routes back with exact, quoted critique that makes the retry substantively different.

## Pipeline I/O

- **Called by**: pipeline skill (step: referee)
- **Input**: `{run_dir}/draft-v2.md` + `{run_dir}/verification-report.md` + `{run_dir}/curated-sources.md`
- **Output**: `{run_dir}/referee-verdict.md` + (if not APPROVED) `{run_dir}/referee-critique.md`
- **Pass**: APPROVED or APPROVED_WITH_NOTES → continue to librarian
- **Fail**: NEEDS_WORK → route back to retry target (max 2 attempts), HARD_REJECTED → abort run

## Attempt tracking

Before scoring: check if `{run_dir}/referee-verdict.md` already exists.
- If it does not exist: this is **Attempt 1**.
- If it exists and contains `ATTEMPT: 1`: this is **Attempt 2**.
- If it exists and contains `ATTEMPT: 2`: this is the **final pass — force verdict** (see § Force verdict below).

## Scoring rubric

Score all four criteria. Write the scores down **before** calculating the total.

---

### 1. Accuracy (0–40 pts)

Read `verification-report.md`. Count ❌ (contradicted) claims still present in `draft-v2.md`.

| Condition | Score |
|---|---|
| Zero ❌ claims present in draft | 40 |
| 1 ❌ claim present but given a qualifier ("reportedly", "according to X") | 30 |
| 1 ❌ claim present, unqualified | 20 |
| 2 ❌ claims present | 10 |
| 3+ ❌ claims or systematic factual distortion | 0 |

To check: for each ❌ item in the verification report, search `draft-v2.md` for the claim text or a paraphrase of it.

---

### 2. Structure (0–20 pts)

Check three structural rules:

**Rule A — Hook**: Does the first paragraph open with a specific fact (a name, date, number, institution, vote count)? A hook that begins with a generalisation ("Europe has long…", "For years…", "The question of…") fails Rule A.

**Rule B — Body**: Does each H2 section state its analytical claim in the first sentence, then support it? A section that opens with context/background before stating a point fails Rule B.

**Rule C — Close**: Does the final paragraph make a forward-looking structural observation (what happens next, what must follow, what the unresolved tension is)? A closing paragraph that recaps the body fails Rule C.

| Rules passed | Score |
|---|---|
| A + B + C | 20 |
| 2 of 3 | 15 |
| 1 of 3 | 8 |
| 0 of 3 | 0 |

---

### 3. Voice (0–25 pts)

Check five voice rules against the actual text of `draft-v2.md`:

**Rule V1 — Active voice**: Count passive constructions ("was decided by", "has been proposed", "are expected to"). More than 3 = violation.

**Rule V2 — No marketing language**: Check for: landmark, game-changer, unprecedented, historic, pivotal, crucial, vital, key, groundbreaking. Any one of these present = violation.

**Rule V3 — No padding**: Check for: "it is important to note", "needless to say", "at the end of the day", "in order to", "the fact that", "it should be mentioned". Any one = violation.

**Rule V4 — Opinions labelled**: Any analytical judgement presented as neutral fact = violation. "Patria's view:", "This suggests…", "The data points to…" = correct labelling.

**Rule V5 — Varied rhythm**: Does any paragraph contain 4+ sentences of similar length? Monotonous rhythm = minor violation.

| Rules passed | Score |
|---|---|
| 5 of 5 | 25 |
| 4 of 5 | 20 |
| 3 of 5 | 15 |
| 2 of 5 | 8 |
| 0–1 of 5 | 0 |

---

### 4. Completeness (0–15 pts)

Read `curated-sources.md`. Find the "Key questions" section — it lists 3–5 questions the article was supposed to answer.

Count how many are answered in `draft-v2.md`. Also check word count.

| Condition | Score |
|---|---|
| All key questions answered + 700–1100 words | 15 |
| 3+ key questions answered + word count ok | 12 |
| 2 key questions answered | 8 |
| 1 key question answered or word count < 600 | 4 |
| Key questions not answered and/or < 500 words | 0 |

---

## Total and verdict tiers

```
TOTAL = accuracy + structure + voice + completeness
```

| Score | Verdict |
|---|---|
| ≥ 80 | **APPROVED** → continue to librarian |
| 65–79 | **NEEDS_WORK** → targeted retry (if attempts < 2) |
| 50–64 | **NEEDS_WORK** → targeted retry (if attempts < 2) |
| < 50 | **REJECTED** → abort run (do not retry) |

---

## Force verdict (Attempt 3 — final pass)

If this is already Attempt 2 and the draft still scores below 80:

- Score ≥ 65: write `VERDICT: APPROVED_WITH_NOTES` — log the remaining issues but pass to librarian anyway.
- Score 50–64: write `VERDICT: APPROVED_WITH_NOTES` — same, but flag prominently.
- Score < 50: write `VERDICT: HARD_REJECTED` — the run has failed. Do not proceed to librarian.

The force verdict ends retrying. No further loops.

---

## Retry target selection (NEEDS_WORK only)

When the verdict is NEEDS_WORK, identify the single step to retry:

1. If accuracy score ≤ 20 → `RETRY_TARGET: editor-structure`
2. Else if voice score ≤ 15 → `RETRY_TARGET: editor-voice`
3. Else if structure score ≤ 8 → `RETRY_TARGET: editor-structure`
4. Else if completeness score ≤ 8 → `RETRY_TARGET: writer-body`
5. Default → `RETRY_TARGET: editor-voice`

---

## Writing referee-critique.md (NEEDS_WORK only)

This file is what makes the retry different. It must contain **quoted text** — not vague feedback.

Write `{run_dir}/referee-critique.md`:

```markdown
# Referee Critique — {run_id} — Attempt {n}

**RETRY_TARGET**: {step}
**Score**: {total}/100 — Accuracy {a}/40 · Structure {s}/20 · Voice {v}/25 · Completeness {c}/15

## Fixes required
```

Then write one section for each criterion that scored below its maximum, **only if it contributed to the failure**:

### Accuracy fixes (if accuracy < 40)
For each ❌ claim still in the draft, copy the exact sentence from the draft, then state what the verifier found:
```
- CLAIM IN DRAFT: "«exact sentence from draft»"
  CORRECT FACT: [what verification-report.md says the source actually states]
  ACTION: Replace or remove this sentence.
```

### Structure fixes (if structure < 20)
For each failed rule, quote the specific text:
```
- HOOK: "«first sentence of the article»"
  PROBLEM: Opens with a generalisation.
  ACTION: Replace with the most specific fact in the article. Candidate: «quote a specific fact from the body».

- SECTION "«H2 heading»": "«opening sentence of that section»"
  PROBLEM: Opens with context, not a claim.
  ACTION: Add topic sentence first: «suggested claim based on the content of that section».

- CLOSE: "«final paragraph, first sentence»"
  PROBLEM: Recaps the body.
  ACTION: Replace with a forward structural point. Candidate: «a forward-looking observation from the research».
```

### Voice fixes (if voice < 25)
Quote each specific violation:
```
- PASSIVE: "«exact passive sentence»"
  REWRITE AS: "«active version — you must provide the active rewrite»"

- MARKETING: "«sentence containing the marketing word»"
  REMOVE: the word «word». Describe what actually happened.

- PADDING: "«sentence containing the padding phrase»"
  DELETE: «padding phrase». Rewrite as: «leaner version».

- UNLABELLED OPINION: "«sentence stated as fact»"
  ADD LABEL: prefix with "Patria's view:" or "The data suggests…"
```

### Completeness fixes (if completeness < 15)
List the specific unanswered questions:
```
- KEY QUESTION NOT ANSWERED: "«exact question from curated-sources.md»"
  ADD: A paragraph addressing this. Relevant source from the research: «URL or source title from research-report.md».

- WORD COUNT: {actual_words}w — target is 700–1100w.
  ADD: Approximately {700 - actual_words}w. Expand the thinnest body section.
```

---

## Writing referee-verdict.md

Always write `{run_dir}/referee-verdict.md`, regardless of verdict:

```markdown
# Referee Verdict — {run_id}

ATTEMPT: {n}
VERDICT: {APPROVED | NEEDS_WORK | REJECTED | APPROVED_WITH_NOTES | HARD_REJECTED}
SCORE: {total}/100
ACCURACY: {a}/40
STRUCTURE: {s}/20
VOICE: {v}/25
COMPLETENESS: {c}/15

RETRY_TARGET: {step | N/A}

## Notes
{one paragraph: what passed, what didn't, what the retry must fix — or "Approved without reservation" if APPROVED}
```

---

## Completion

After writing verdict (and critique if needed):

```
exec: python3 /workspace/tools/pipeline_complete.py referee {run_dir}/referee-verdict.md
```

Report:
- If APPROVED or APPROVED_WITH_NOTES: `Referee done — APPROVED {total}/100. Proceeding to librarian.`
- If NEEDS_WORK: `Referee done — NEEDS_WORK {total}/100. Critique written. Retry target: {step}. Attempt {n}/2.`
- If REJECTED/HARD_REJECTED: `Referee done — REJECTED {total}/100. Run aborted after {n} attempt(s).`

Do not start librarian. Do not start any retry step. The pipeline dispatcher handles routing.
