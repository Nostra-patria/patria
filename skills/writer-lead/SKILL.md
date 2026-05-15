# Skill: Writer — Lead

Write the opening of the article only: frontmatter + hook + lead section. Do not write body sections or the close.

## Pipeline I/O

- **Called by**: pipeline skill (step: writer-lead)
- **Input**: `{run_dir}/research-report.md` + `{run_dir}/curated-sources.md`
- **Output**: `{run_dir}/draft-v1-lead.md`
- **Pass score**: ≥ 0.6 (frontmatter complete + hook present + lead section ≥ 100 words)
- **Trigger**: `research-report.md` contains `## RUN-2-COMPLETE`

## Goal

Write the opening of the article — frontmatter, hook, and lead section. Get the argument and register right from the first sentence. The body writer builds on this foundation.

## Tools

- `read_file` — read research-report.md and curated-sources.md
- `write_file` — write draft-v1-lead.md

## Patria voice

**Before writing: read `/workspace/SOUL.md` and apply its register rules.**

- English — always
- Specific over general. Name the commissioner, the treaty article, the vote count, the summit date.
- Active sentences. "The Council approved" not "approval was granted."
- No marketing language: not "landmark", "game-changer", "unprecedented", "historic".
- No padding: not "it is important to note", "needless to say", "at the end of the day".
- Analysis is stated as analysis — never as established fact. Do NOT write "Patria's view:". State the inference directly: "The gap persists not because legislation is absent, but because..."
- Short sentence after complexity. Rhythm matters.
- European integration as the frame: challenges are integration problems to solve within the EU, never evidence the project has failed.

**Register: Astra Europa manifesto tone — calm, diagnostic, structurally rigorous.**

The article must read like the Astra Europa manifesto, not like a newspaper headline. Study these contrasts:

| ❌ Sensational (avoid) | ✅ Astra Europa register (use) |
|---|---|
| "signals the end of the intergovernmental era" | "challenges the structural logic of intergovernmental decision-making" |
| "The Federal Imperative" | "The Case for a Federal Approach" |
| "survival in a multipolar world" | "competitiveness in a multipolar world" |
| "A seismic shift in European policy" | "A structural change in how [institution] handles [X]" |
| "Europe stands at a crossroads" | Name the specific decision point instead |

**Titles**: State the argument, not a verdict. "Beyond Externalisation" is good. "The End of the Intergovernmental Era" is not.

**Hook**: Do NOT open with a date. ❌ "On May 13, 2026, X happened." ✅ Lead with the structural condition. The news peg is context, placed in the first section — not the opening line.

## Process

### Step 1 — Read the research

Read `{run_dir}/research-report.md` in full. Identify:
- The single strongest angle (most institutional specificity + historical depth)
- The most striking fact, quote, or statistic — this will anchor the hook
- The Astra Europa Guiding Star and its frame

### Step 2 — Write the frontmatter

```markdown
---
layout: article
title: "{Specific, opinionated headline — max 90 chars. States the argument, not the topic.}"
date: {today YYYY-MM-DD}
star: {n}
star_label: "{Star name}"
slug: {run_id}
summary: "{One sentence. The argument in plain language.}"
image: /patria/assets/img/articles/{run_id}-header.png
---
```

Slug must equal the `{run_id}` exactly. Image path must follow the pattern above exactly.

### Step 3 — Write the hook

```markdown
**{1-2 sentences. The argument stated boldly. Lead with a named fact, date, or official — not a question, not a generalisation. No hedging.}**
```

Check: does the first sentence name something specific? If it starts with "Europe" followed by a general observation — rewrite it.

### Step 4 — Write the lead section

```markdown
## {Section 1 title — describe the immediate development}

{2–3 paragraphs. What happened. Who decided what. Named people, named dates, named institutions. Inline source links for every factual claim: [Source Name](URL).}
```

This section is ~200 words. It sets the scene for the body writer.

### Step 5 — Write draft-v1-lead.md

Write the complete output: frontmatter + hook + lead section. Stop there.

Report: `Writer Lead done — {word count} words, hook and lead section written.`

Do not write body sections. Do not write the close.
