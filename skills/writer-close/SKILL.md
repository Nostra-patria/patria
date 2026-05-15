# Skill: Writer — Close

Write the closing section and Bluesky thread. Output goes to draft-v1-close.md. A separate writer-merge step handles the final merge.

## Pipeline I/O

- **Called by**: pipeline skill (step: writer-close)
- **Input**: `{run_dir}/draft-v1-body.md` + `{run_dir}/curated-sources.md`
- **Output**: `{run_dir}/draft-v1-close.md`
- **Pass score**: ≥ 0.6 (implication paragraph present + bluesky thread present)
- **Trigger**: `draft-v1-body.md` exists

## Goal

Write two things only:
1. A closing implication paragraph (~100 words)
2. A Bluesky thread (5 posts)

Do NOT merge files. Do NOT read draft-v1-lead.md. Do NOT do a word count. That is writer-merge's job.

**Before writing: read `/workspace/SOUL.md` and apply its register rules.**

Closing paragraph rules:
- State the structural consequence — not a prescription or imperative.
- ❌ "This is the only way to close the gap..." / "Europe must now..."
- ✅ End with the structural question or choice that follows from the analysis. Leave the reader with something concrete to consider, not a call to action.
- Honest about pace: if a solution requires treaty change or political will that isn't there yet, say so.
- Land on a short declarative. The last sentence should be under 15 words.

## Tools

- `read_file` — read draft-v1-body.md (for context) and curated-sources.md (for article angle)
- `write_file` — write draft-v1-close.md

## Process

### Step 1 — Read context

Read `{run_dir}/draft-v1-body.md` — understand the analytical argument and what has been established.
Read `{run_dir}/curated-sources.md` — note the Selected angle for the Bluesky framing.

### Step 2 — Write the implication paragraph

```markdown
## {Title: what this means going forward}

{1 paragraph, ~100 words. One concrete forward-looking observation. Not a summary. Not "time will tell." A specific structural question or consequence that follows logically from the analysis. Constructive — leave the reader with something to think about, not a warning.}
```

### Step 3 — Write the Bluesky thread

5 posts. Each builds on the previous — hook, evidence, EU context, Patria take, link.

```markdown
<!-- bluesky_thread
post1: |
  {The hook. Lead with the most striking fact from the article. Core argument in 1-2 sharp sentences. Max 280 chars. Active voice. No em-dashes.}
post2: |
  {Evidence post. One concrete data point or quote that proves the argument. What does it mean in practice? Max 280 chars.}
post3: |
  {EU context. Why does this structural tension exist? Name the institution, treaty article, or policy mechanism at the root. Max 280 chars.}
post4: |
  {The Patria take. What would need to change — one specific reform, shift, or decision. Grounded. Not a slogan. Max 280 chars.}
post5: |
  Full article:
  https://nostra-patria.github.io/patria/articles/{run_id}/

  #EUPolitics #{TopicTag1} #{TopicTag2}
-->
```

Rules: posts 1-4 max 280 chars each. `#EUPolitics` always on post5. Two topic-specific tags. No em-dashes anywhere.

### Step 4 — Write draft-v1-close.md

Write `{run_dir}/draft-v1-close.md` containing exactly:
1. The implication paragraph (Step 2)
2. The Bluesky thread comment (Step 3)

### Step 5 — Stop

Report: `Writer Close done — implication paragraph and Bluesky thread written to draft-v1-close.md.`

Do not start writer-merge. Do not read or write any other file.
