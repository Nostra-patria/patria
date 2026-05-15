# Skill: Librarian

Update the scoreboard and article library after a referee-approved run. Final bookkeeping before illustration.

## Pipeline I/O

- **Called by**: pipeline skill (step: librarian)
- **Input**: `{run_dir}/referee-verdict.md` + `memory/scoreboard.json` + `memory/LIBRARY.md`
- **Output**: `{run_dir}/librarian-report.md` (confirms what was updated)
- **Pass score**: 1.0 (must complete fully or retry)
- **Trigger**: `referee-verdict.md` exists with `VERDICT: APPROVED` or `VERDICT: APPROVED_WITH_NOTES`

## Tools

- `read_file` — read referee-verdict.md, scoreboard.json, LIBRARY.md, draft-v2.md
- `write_file` — update scoreboard.json, update LIBRARY.md, write librarian-report.md

## Process

### Step 1 — Read inputs

Read `{run_dir}/referee-verdict.md`. The pipeline threshold is 0.65 — a run may reach librarian with any of these verdicts and MUST proceed: APPROVED, APPROVED_WITH_NOTES, NEEDS_WORK (72+/100 passed the threshold).

Only stop if VERDICT is REJECTED or HARD_REJECTED. In that case write:
```
librarian-report.md: "SKIPPED — run verdict is {VERDICT}. No scoreboard update."
```
Then call pipeline_complete.py and exit.

For NEEDS_WORK: the pipeline approved it. Proceed with scoreboard and LIBRARY.md updates as normal.

Read `{run_dir}/draft-v2.md` — extract from frontmatter:
- `title`
- `slug`
- `star` (the Astra Europa star number this article covers)
- `date`
- `description` (summary / deck)

Read `memory/scoreboard.json`.

Read `memory/LIBRARY.md` (the article archive).

### Step 2 — Update scoreboard.json

Increment the count for the star number found in the draft frontmatter:

```json
"stars": {
  "{n}": {
    "name": "...",
    "count": <current_count + 1>
  }
}
```

Write the updated `memory/scoreboard.json` immediately after incrementing.

### Step 3 — Update LIBRARY.md

Append a new entry at the top of the articles list (most recent first):

```markdown
| {date} | [{title}](/patria/articles/{slug}/) | Star {n} — {star_name} | {referee_score}/100 |
```

If the LIBRARY.md does not yet have a table, add one:

```markdown
## Published articles

| Date | Title | Star | Score |
|---|---|---|---|
```

Write the updated `memory/LIBRARY.md` immediately after appending.

### Step 4 — Write librarian-report.md

```markdown
# Librarian Report — {run_id}

Scoreboard updated: Star {n} "{star_name}" → count {old_count} → {new_count}
LIBRARY.md updated: added "{title}" ({date})
slug: {slug}
referee score: {score}/100
```

### Step 5 — Complete

```
exec: python3 /workspace/tools/pipeline_complete.py librarian {run_dir}/librarian-report.md
```

Report: `Librarian done — Star {n} count now {new_count}. Proceeding to illustrator.`

Do not start illustrator. Do not edit any other files.
