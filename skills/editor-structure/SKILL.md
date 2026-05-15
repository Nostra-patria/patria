# Skill: Editor — Structure

Fix structure and incorporate verification findings. Produces a clean structural draft the voice editor can work with.

## Anti-loop rule

**Read each file exactly once, then write immediately.**
1. Check if `{run_dir}/referee-critique.md` exists (optional read).
2. Read `{run_dir}/draft-v1.md` — once.
3. Read `{run_dir}/verification-report.md` — once.
4. Write `{run_dir}/draft-v2-structure.md` in full with `write_file`.
5. Call `python3 /workspace/tools/pipeline_complete.py editor-structure {run_dir}/draft-v2-structure.md`.

**Do NOT re-read any file after it has been read. Write the full output in one write_file call.**

## Pipeline I/O

- **Called by**: pipeline skill (step: editor-structure)
- **Input**: `{run_dir}/draft-v1.md` + `{run_dir}/verification-report.md`
- **Output**: `{run_dir}/draft-v2-structure.md`
- **Pass score**: ≥ 0.7 (all ❌ claims resolved, structure issues fixed, word count maintained)
- **Trigger**: `verification-report.md` exists with `VERDICT: PASS` or `VERDICT: FAIL`

## Goal

Apply the verification findings and fix structural problems. Do NOT apply voice yet — that is the next step. This pass is surgical: remove or correct contradicted claims, fix flow, fix structure.

## Retry mode

Before starting, check if `{run_dir}/referee-critique.md` exists.

**If referee-critique.md exists** — this is a referee-directed retry. The normal process still applies, but with these additions:

1. Read `{run_dir}/referee-critique.md` **first**.
2. The critique contains exact quoted sentences that must change. Address every item in `## Accuracy fixes` and `## Structure fixes` sections explicitly.
3. For each quoted passage in the critique:
   - Locate the exact sentence in the draft (or draft-v2-structure.md if this is a second pass).
   - Apply the specific fix described — not a general improvement, the exact fix.
4. After completing all critique items, continue with the normal process below for any remaining issues.
5. Report: `Editor Structure done (RETRY — {n} critique items addressed) — {word count} words.`

Do not skip critique items. If a critique item no longer applies (the sentence was already changed), note it as resolved.

## Tools

- `read_file` — read input files and referee-critique.md if present
- `write_file` — write draft-v2-structure.md

## Process

### Step 1 — Read input files

If `{run_dir}/referee-critique.md` exists: read it first (see Retry mode above).

Read `{run_dir}/draft-v1.md` in full (or `draft-v2-structure.md` if this is a retry starting from a later draft).
Read `{run_dir}/verification-report.md` — note every ❌ contradicted claim and every ⚠️ uncertain claim.

### Step 2 — Apply verification fixes

For every ❌ contradicted claim:
- Remove the claim entirely, OR
- Replace it with the correct fact as found by the verifier (the verification report notes what the source actually says)
- Never leave a contradicted claim in the text

For every ⚠️ uncertain claim:
- Add a qualifier: "according to [source]" or "as reported by [outlet]"
- Do not remove uncertain claims — they are flagged but not wrong

### Step 3 — Fix structural problems

Check and fix in this order:

**Lead / hook**: Does the first sentence name something specific (a person, date, institution, vote count)? If it opens with a generalisation ("Europe has long struggled with...") — rewrite the opening to lead with the most concrete fact from the article.

**Body sections**: Does each H2 section make a claim first, then support it? If a section only summarises without making a point — add a topic sentence that states the analytical claim.

**Closing paragraph**: Does it make a specific forward-looking observation? If it recaps the body — rewrite it as a concrete structural consequence or question.

**Flow**: Are there abrupt transitions between sections? Add one bridging sentence where needed.

### Step 4 — Write draft-v2-structure.md

Write the full revised article. Write section by section, appending after each. Do not rewrite passages that need no changes — copy them as-is.

Report: `Editor Structure done — {x} contradicted claims resolved, {y} structural fixes, {word count} words.`

Do not apply voice. Do not start Editor:Voice.
