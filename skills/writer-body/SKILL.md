# Skill: Writer — Body

Write the three body sections of the article. Builds on the lead already written by Writer:Lead.

## Pipeline I/O

- **Called by**: pipeline skill (step: writer-body)
- **Input**: `{run_dir}/draft-v1-lead.md` + `{run_dir}/research-report.md`
- **Output**: `{run_dir}/draft-v1-body.md`
- **Pass score**: ≥ 0.6 (3 body sections present, each ≥ 100 words, inline source links present)
- **Trigger**: `draft-v1-lead.md` exists

## Goal

Write the analytical core of the article — three H2 sections that build the argument. Each section addresses a different dimension of the Guiding Star angle. Use the research report as the only source of facts. Do not invent claims.

**Before writing: read `/workspace/SOUL.md` and apply its register rules.**

Key rules for body sections:
- **Section titles**: diagnostic, not dramatic. Describe the structural dimension, not a verdict.
  - ❌ "The Hardware Paradox: From Gas to Lithium" / "The Convergence of Two Dependencies"
  - ✅ "The Storage Gap" / "Where the Law Ends" / "Battery Supply: A New Chokepoint"
- **No imperatives in analysis**: state the structural consequence, not a prescription.
  - ❌ "Europe must now build a federal energy authority."
  - ✅ "The structural logic points toward a federal energy authority — but that requires treaty change the current political will cannot yet support."
- **Rhythm**: after 2-3 dense analytical sentences, land on a short declarative.
  - Example: "The architecture exists. The political integration does not."

## Tools

- `read_file` — read draft-v1-lead.md and research-report.md
- `write_file` — write draft-v1-body.md

## Process

### Step 1 — Read context

Read `{run_dir}/draft-v1-lead.md` — note the title, star, angle, and what the lead section already covered.
Read `{run_dir}/research-report.md` — identify facts for each of the three body sections below.

### Step 2 — Write body section by section

Write each section, then pause and review before moving to the next. Do not write all three in one pass.

**Section 2 — Institutional or treaty context**
```markdown
## {Title: where this sits in the EU framework}

{2–3 paragraphs. Which EU institutions are involved. What treaty article applies. What the legislative stage is. Named officials, vote counts, committee decisions. Source every claim with inline links: [Source Name](URL).}
```
~200 words.

**Section 3 — Member state dynamics**
```markdown
## {Title: who is aligned, who is resisting}

{2–3 paragraphs. Which member states support the position. Which resist. What the fault lines are. Name specific countries and their stated positions. Source every claim.}
```
~200 words.

**Section 4 — Historical context and precedent**
```markdown
## {Title: what has been tried before}

{2–3 paragraphs. What precedent exists. What was tried before and why it failed. How long this issue has been on the EU agenda. This is what distinguishes analysis from news. Source every claim.}
```
~200 words.

### Step 3 — Write draft-v1-body.md

Write all three sections as a single file. Do not include the frontmatter or lead — those are already in draft-v1-lead.md.

Report: `Writer Body done — {word count} words across 3 body sections.`

Do not write the close. Do not merge the files.
