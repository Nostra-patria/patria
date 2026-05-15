# Skill: Pipeline

Orchestrate the Patria editorial pipeline. One step per cron tick. Each step does one job, writes its output, scores itself, and stops. The pipeline reads state, opens the gate, runs the next step, and marks it complete.

---

## Pipeline overview

16 steps, each producing a specific output file:

```
scout              → scout-notes.md
scout-deepen       → scout-notes-deepen.md
curator            → curated-sources.md
researcher-1       → research-report.md  (+ ## RUN-1-COMPLETE marker)
researcher-2       → research-report.md  (+ ## RUN-2-COMPLETE marker, appended)
writer-lead        → draft-v1-lead.md
writer-body        → draft-v1-body.md
writer-close       → draft-v1.md         (complete article, 700–1100w)
verifier           → verification-report.md
editor-structure   → draft-v2-structure.md
editor-voice       → draft-v2.md
grounder           → grounding-report.md
referee            → referee-verdict.md  (+ referee-critique.md if NEEDS_WORK)
librarian          → librarian-report.md
illustrator        → image.json
publisher          → published.json
```

---

## State structure

```
memory/pipeline/
  active.json                          <- { "run_id": "2026-05-12-star1-slug" } or {}
  runs/
    2026-05-12-star1-slug/
      state.json                       <- step statuses and scores
      scout-notes.md
      scout-notes-deepen.md
      curated-sources.md
      research-report.md
      draft-v1-lead.md
      draft-v1-body.md
      draft-v1.md
      verification-report.md
      draft-v2-structure.md
      draft-v2.md
      grounding-report.md
      referee-verdict.md
      referee-critique.md              <- only present if referee returned NEEDS_WORK
      librarian-report.md
      image.json
      published.json
```

**state.json structure:**
```json
{
  "run_id": "2026-05-12-star1-slug",
  "started": "2026-05-12T08:00:00Z",
  "current_step": "researcher-1",
  "steps": {
    "scout":            { "status": "done",    "score": 0.8, "attempts": 1 },
    "scout-deepen":     { "status": "done",    "score": 0.8, "attempts": 1 },
    "curator":          { "status": "done",    "score": 0.75, "attempts": 1 },
    "researcher-1":     { "status": "pending", "score": null, "attempts": 0 },
    "researcher-2":     { "status": "waiting" },
    "writer-lead":      { "status": "waiting" },
    "writer-body":      { "status": "waiting" },
    "writer-close":     { "status": "waiting" },
    "verifier":         { "status": "waiting" },
    "editor-structure": { "status": "waiting" },
    "editor-voice":     { "status": "waiting" },
    "grounder":         { "status": "waiting" },
    "referee":          { "status": "waiting" },
    "librarian":        { "status": "waiting" },
    "illustrator":      { "status": "waiting" },
    "publisher":        { "status": "waiting" }
  }
}
```

## How dispatch works

**You do not need to read state or determine the next step yourself.**

The cron dispatcher (AGENTS.md) already ran `python3 /workspace/tools/pipeline_dispatch.py` before loading this skill. That script read `active.json` and `state.json`, found the next actionable step, opened the gate, and printed:

```
DISPATCH READY
Run: <run_id>
Step: <step>
Skill: skills/<step>/SKILL.md
RunDir: memory/pipeline/runs/<run_id>
Complete: python3 /workspace/tools/pipeline_complete.py <step> <output_file>
```

Use those values. Do not re-read active.json or state.json — the dispatch output is authoritative.

---

## Executing the dispatched step

1. Note the `Step`, `Skill`, `RunDir`, and `Complete` values from the dispatch output
2. Read the skill file at `Skill`
3. Execute the step following that skill's instructions, using `RunDir` as the base path
4. When the skill says its output file is written, run the `Complete` command
5. Read the `Complete` output:
   - `COMPLETE PASS` — step done, stop
   - `COMPLETE RETRY` — step below threshold, stop (next tick re-runs it)
   - `COMPLETE NEEDS_WORK` (referee) — pipeline rewound, stop
   - `COMPLETE FAIL` — step failed permanently, stop
   - `RUN COMPLETE` — all 16 steps done, stop

**After any `Complete` call — STOP. Do not start the next step.**

---

## Step input/output reference

Each step's skill file, inputs, and output (use `RunDir` from the dispatch output as the base path):

### scout
- **Skill**: `skills/scout/SKILL.md`
- **Input**: run `tools/scoreboard_check.py` for star assignment
- **Output**: `{run_dir}/scout-notes.md`

### scout-deepen
- **Skill**: `skills/scout-deepen/SKILL.md`
- **Input**: `{run_dir}/scout-notes.md`
- **Output**: `{run_dir}/scout-notes-deepen.md`

### curator
- **Skill**: `skills/curator/SKILL.md`
- **Input**: `{run_dir}/scout-notes.md` + `{run_dir}/scout-notes-deepen.md`
- **Output**: `{run_dir}/curated-sources.md`

### researcher-1
- **Skill**: `skills/researcher/SKILL.md`
- **Input**: `{run_dir}/curated-sources.md`
- **Output**: `{run_dir}/research-report.md` (with `## RUN-1-COMPLETE`)
- **Trigger check**: RUN-1-COMPLETE not yet in file

### researcher-2
- **Skill**: `skills/researcher-2/SKILL.md`
- **Input**: `{run_dir}/curated-sources.md` + `{run_dir}/research-report.md`
- **Output**: append to `{run_dir}/research-report.md` (adds `## RUN-2-COMPLETE`)
- **Trigger check**: RUN-1-COMPLETE present, RUN-2-COMPLETE absent

### writer-lead
- **Skill**: `skills/writer/SKILL.md`
- **Input**: `{run_dir}/research-report.md` + `{run_dir}/curated-sources.md`
- **Output**: `{run_dir}/draft-v1-lead.md`

### writer-body
- **Skill**: `skills/writer-body/SKILL.md`
- **Input**: `{run_dir}/draft-v1-lead.md` + `{run_dir}/research-report.md`
- **Output**: `{run_dir}/draft-v1-body.md`
- **Retry note**: if `status == "referee-retry"`, re-read `{run_dir}/referee-critique.md` first

### writer-close
- **Skill**: `skills/writer-close/SKILL.md`
- **Input**: `{run_dir}/draft-v1-lead.md` + `{run_dir}/draft-v1-body.md` + `{run_dir}/research-report.md`
- **Output**: `{run_dir}/draft-v1.md` (complete article)
- **Retry note**: if `status == "retry"` (set after verifier/grounder fail), re-read `{run_dir}/verification-report.md` or `{run_dir}/grounding-report.md` first

### verifier
- **Skill**: `skills/verifier/SKILL.md`
- **Input**: `{run_dir}/draft-v1.md` (NO research report -- independent check)
- **Output**: `{run_dir}/verification-report.md`
- **FAIL behaviour**: pipeline_complete resets writer-close to retry, clears verifier + grounder to waiting

### editor-structure
- **Skill**: `skills/editor-structure/SKILL.md`
- **Input**: `{run_dir}/draft-v1.md` + `{run_dir}/verification-report.md`
- **Input (retry)**: also reads `{run_dir}/referee-critique.md` if present
- **Output**: `{run_dir}/draft-v2-structure.md`

### editor-voice
- **Skill**: `skills/editor-voice/SKILL.md`
- **Input**: `{run_dir}/draft-v2-structure.md`
- **Input (retry)**: also reads `{run_dir}/referee-critique.md` if present
- **Output**: `{run_dir}/draft-v2.md`

### grounder
- **Skill**: `skills/grounder/SKILL.md`
- **Input**: `{run_dir}/draft-v2.md` + `{run_dir}/research-report.md`
- **NO web access**
- **Output**: `{run_dir}/grounding-report.md`
- **FAIL behaviour**: pipeline_complete resets writer-close to retry, clears verifier through grounder to waiting

### referee
- **Skill**: `skills/referee/SKILL.md`
- **Input**: `{run_dir}/draft-v2.md` + `{run_dir}/verification-report.md` + `{run_dir}/curated-sources.md`
- **Output**: `{run_dir}/referee-verdict.md` (always) + `{run_dir}/referee-critique.md` (if NEEDS_WORK)
- **NEEDS_WORK behaviour**: pipeline_complete reads `RETRY_TARGET` from verdict, resets that step + steps between it and referee
- **REJECTED / HARD_REJECTED**: run is aborted, active.json cleared

### librarian
- **Skill**: `skills/librarian/SKILL.md`
- **Input**: `{run_dir}/referee-verdict.md` + `memory/scoreboard.json` + `memory/LIBRARY.md`
- **Output**: `{run_dir}/librarian-report.md`, updates scoreboard.json and LIBRARY.md

### illustrator
- **Skill**: `skills/illustrator/SKILL.md`
- **Input**: frontmatter from `{run_dir}/draft-v2.md`
- **Output**: `memory/media/YYYY-MM/{run_id}-header.png` + `{run_dir}/image.json`

### publisher
- **Skill**: `skills/publisher/SKILL.md`
- **Input**: `{run_dir}/draft-v2.md` + `{run_dir}/image.json`
- **Output**: `{run_dir}/published.json` + git push + Bluesky post

---

## Referee retry flow (example)

```
referee scores 72/100 → NEEDS_WORK → RETRY_TARGET: editor-voice
pipeline_complete.py:
  sets editor-voice  → "referee-retry"
  sets grounder      → "waiting"
  sets referee       → stays "in-progress" pending retry
  current_step       → "editor-voice"

next tick: gate opens editor-voice (referee-retry status bypasses linear check)
  editor-voice reads referee-critique.md → applies targeted fixes
  writes new draft-v2.md
  pipeline_complete editor-voice → PASS
  current_step → "grounder"

next tick: grounder → passes → referee attempt 2
  referee scores 83/100 → APPROVED → librarian
```

If referee scores NEEDS_WORK on attempt 2, it writes a second critique and routes again.
After attempt 2, force-verdict mode: score >=65 → APPROVED_WITH_NOTES, <50 → HARD_REJECTED.
