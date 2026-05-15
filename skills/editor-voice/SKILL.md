# Skill: Editor — Voice

Apply the Patria voice. Turns the structurally correct draft into a publishable article with the right register, rhythm, and analytical posture.

## Anti-loop rule

**Read once, write once.**
1. Read `{run_dir}/draft-v2-structure.md` — exactly once.
2. Apply voice edits in memory.
3. Write the full result to `{run_dir}/draft-v2.md` with `write_file` in a single call.
4. Call `python3 /workspace/tools/pipeline_complete.py editor-voice {run_dir}/draft-v2.md`.

**Do NOT call read_file more than once. Write the entire draft in one write_file call — do not append incrementally.**

## Pipeline I/O

- **Called by**: pipeline skill (step: editor-voice)
- **Input**: `{run_dir}/draft-v2-structure.md`
- **Output**: `{run_dir}/draft-v2.md`
- **Pass score**: ≥ 0.7 (voice rules applied, no padding, word count 700–1100)
- **Trigger**: `draft-v2-structure.md` exists

## Goal

This is the final editorial pass before quality control. The structure is already correct — now make it read like Patria. Apply voice rules sentence by sentence where needed. Do not restructure, do not add new facts.

## Retry mode

Before starting, check if `{run_dir}/referee-critique.md` exists.

**If referee-critique.md exists** — this is a referee-directed retry. The normal process still applies, but with these additions:

1. Read `{run_dir}/referee-critique.md` **first**.
2. The critique contains exact quoted sentences under `## Voice fixes` that must change. Each entry gives you: the original sentence, what is wrong, and in many cases the exact rewrite.
3. For each quoted passage in the critique:
   - Locate the exact sentence in draft-v2-structure.md.
   - Apply the fix exactly as specified. If a rewrite is suggested, use it (you may improve phrasing but must keep the substance).
   - If no rewrite is suggested, apply the relevant voice rule yourself.
4. After completing all critique items, continue with the normal voice pass below for any remaining issues.
5. Report: `Editor Voice done (RETRY — {n} critique items addressed) — draft-v2.md, {word count} words.`

Do not skip critique items. Addressing 2 of 5 flagged sentences and ignoring 3 will not raise the score.

## Tools

- `read_file` — read draft-v2-structure.md and referee-critique.md if present
- `write_file` — write draft-v2.md

## Patria voice rules

Apply these actively — find violations and fix them:

**Active voice**: "The Council rejected the proposal" not "The proposal was rejected by the Council."

**Specificity**: Every general statement should have a name, number, or date attached. "Senior officials" → name them if they appear in the research. "A significant increase" → replace with the actual figure.

**No marketing language**: Remove: landmark, game-changer, unprecedented, historic, pivotal, crucial, vital, key, groundbreaking. Replace with the plain description of what actually happened.

**No dramatic framing**: These phrases signal a journalistic sensationalism that violates the Astra Europa register. Find and rewrite:
- "signals the end of the [era/order/system]" → describe what specifically changed or is under pressure
- "survival" as a geopolitical frame → "competitiveness" or "strategic autonomy"
- "The [X] Imperative" in titles or headers → "The Case for [X]" or a plain description
- "seismic", "surge" (as political metaphor), "historic turning point", "transforms X forever"
- Opening sentences that announce a sweeping verdict → rewrite as a specific named fact or event

**Astra Europa register**: After fixing individual words, check the overall register. Each section should read as: diagnose the structural problem → explain why the current approach falls short → state what the federal/integrated alternative would do differently. Not breathless. Not urgent. Reasoned.

**No padding**: Remove: "it is important to note", "needless to say", "at the end of the day", "in order to", "the fact that". Rewrite the sentence without the padding.

**Label opinions**: Any analytical claim or Patria position must be framed as such: "Patria's view:", "The data suggests...", "This implies..." — never presented as neutral fact.

**Rhythm**: After a long, clause-heavy sentence, add a short one. Read each paragraph aloud mentally — if it feels monotonous, vary the sentence length.

**European frame**: Challenges are integration problems to solve within the EU framework. Never frame EU failures as evidence the project has failed. "The coordination mechanism has not delivered on its stated objectives" — not "The EU has failed."

**Closing paragraph**: Must end on a forward-looking structural observation, not a warning or a recap. If it ends with doubt or alarm — rewrite it as a concrete question or next step.

## Process

### Step 1 — Read the draft

If `{run_dir}/referee-critique.md` exists: read it first (see Retry mode above).

Read `{run_dir}/draft-v2-structure.md` in full. Note which paragraphs most need voice work. If this is a retry, start with the sections flagged in the critique.

### Step 2 — Edit section by section

Work through the article one H2 section at a time. For each section:
1. Apply voice rules — fix passive constructions, remove padding, add specificity where missing
2. Check rhythm — vary sentence length if monotonous
3. Append the edited section to draft-v2.md

Do not rewrite sections that already follow the voice rules — copy them as-is.

### Step 3 — Final checks

After all sections:
- [ ] Hook names something specific in the first sentence
- [ ] No ❌ marketing language remaining
- [ ] Opinions are labelled
- [ ] Closing paragraph makes a forward structural point
- [ ] Word count 700–1100 (check; trim padding if over)

### Step 4 — Write draft-v2.md

Complete article, voice-edited. Include the frontmatter and bluesky_thread comment unchanged from draft-v2-structure.md.

Report: `Editor Voice done — draft-v2.md, {word count} words.`

Do not start grounder. Do not edit further.
