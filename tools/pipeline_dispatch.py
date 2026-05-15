#!/usr/bin/env python3
"""
pipeline_dispatch.py — Find and announce the next pipeline step.

Run this at the start of every cron tick. It reads active.json and state.json,
finds the next actionable step, opens the gate, and prints plain-text instructions
for the agent so the agent does NOT have to construct file paths or read state itself.

Output formats:

  DISPATCH READY
  Run: 2026-05-12-federalist-surge-v2
  Step: scout
  Skill: skills/scout/SKILL.md
  RunDir: memory/pipeline/runs/2026-05-12-federalist-surge-v2
  Complete: python3 /workspace/tools/pipeline_complete.py scout memory/pipeline/runs/2026-05-12-federalist-surge-v2/scout-notes.md

  NO WORK
  Reason: no active run (active.json is empty)

  RUN COMPLETE
  Run: 2026-05-12-federalist-surge-v2
"""
import json
import subprocess
import sys
from pathlib import Path

PIPELINE_DIR = Path("/workspace/memory/pipeline")
ACTIVE_FILE = PIPELINE_DIR / "active.json"

STEP_ORDER = [
    "scout", "scout-deepen", "curator",
    "researcher-1", "researcher-2",
    "writer-lead", "writer-body", "writer-close", "writer-merge",
    "verifier", "editor-structure", "editor-voice",
    "grounder", "referee", "librarian",
    "illustrator", "publisher",
]

STEP_OUTPUT = {
    "scout":            "scout-notes.md",
    "scout-deepen":     "scout-notes-deepen.md",
    "curator":          "curated-sources.md",
    "researcher-1":     "research-report.md",
    "researcher-2":     "research-report.md",
    "writer-lead":      "draft-v1-lead.md",
    "writer-body":      "draft-v1-body.md",
    "writer-close":     "draft-v1-close.md",
    "writer-merge":     "draft-v1.md",
    "verifier":         "verification-report.md",
    "editor-structure": "draft-v2-structure.md",
    "editor-voice":     "draft-v2.md",
    "grounder":         "grounding-report.md",
    "referee":          "referee-verdict.md",
    "librarian":        "librarian-report.md",
    "illustrator":      "image.json",
    "publisher":        "published.json",
}

STEP_SKILL = {
    "scout":            "skills/scout/SKILL.md",
    "scout-deepen":     "skills/scout-deepen/SKILL.md",
    "curator":          "skills/curator/SKILL.md",
    "researcher-1":     "skills/researcher/SKILL.md",
    "researcher-2":     "skills/researcher-2/SKILL.md",
    "writer-lead":      "skills/writer/SKILL.md",
    "writer-body":      "skills/writer-body/SKILL.md",
    "writer-close":     "skills/writer-close/SKILL.md",
    "writer-merge":     "skills/writer-merge/SKILL.md",
    "verifier":         "skills/verifier/SKILL.md",
    "editor-structure": "skills/editor-structure/SKILL.md",
    "editor-voice":     "skills/editor-voice/SKILL.md",
    "grounder":         "skills/grounder/SKILL.md",
    "referee":          "skills/referee/SKILL.md",
    "librarian":        "skills/librarian/SKILL.md",
    "illustrator":      "skills/illustrator/SKILL.md",
    "publisher":        "skills/publisher/SKILL.md",
}


def main():
    # 1. Load active run
    if not ACTIVE_FILE.exists():
        print("NO WORK\nReason: active.json does not exist")
        return

    try:
        active = json.loads(ACTIVE_FILE.read_text())
    except (json.JSONDecodeError, OSError) as e:
        print(f"NO WORK\nReason: could not read active.json: {e}")
        return

    run_id = active.get("run_id")
    if not run_id:
        print("NO WORK\nReason: no active run (active.json is empty)")
        return

    # 2. Load state
    state_file = PIPELINE_DIR / "runs" / run_id / "state.json"
    if not state_file.exists():
        print(f"NO WORK\nReason: state.json not found for run {run_id}")
        return

    try:
        state = json.loads(state_file.read_text())
    except (json.JSONDecodeError, OSError) as e:
        print(f"NO WORK\nReason: could not read state.json for run {run_id}: {e}")
        return

    steps = state.get("steps", {})

    # 3. Find next actionable step
    # Statuses that need dispatch: pending, retry, referee-retry
    # Also include in-progress (crash recovery — gate will safely re-open it)
    ACTIONABLE = ("pending", "retry", "referee-retry", "in-progress")

    next_step = None
    for step in STEP_ORDER:
        s = steps.get(step, {})
        if s.get("status") in ACTIONABLE:
            next_step = step
            break

    if not next_step:
        # Check if all done
        all_done = all(steps.get(s, {}).get("status") == "done" for s in STEP_ORDER)
        if all_done:
            ACTIVE_FILE.write_text(json.dumps({}))
            print(f"RUN COMPLETE\nRun: {run_id}")
        else:
            # Run is blocked (failed step, no pending steps)
            failed = [s for s in STEP_ORDER if steps.get(s, {}).get("status") == "failed"]
            ACTIVE_FILE.write_text(json.dumps({}))
            print(
                f"NO WORK\n"
                f"Reason: run {run_id} is blocked — failed steps: {failed}. "
                f"active.json cleared so heartbeat can start a fresh run."
            )
        return

    # 4. Run pipeline_gate.py to validate + mark step as in-progress
    result = subprocess.run(
        ["python3", "/workspace/tools/pipeline_gate.py", next_step],
        capture_output=True,
        text=True,
    )
    gate_output = (result.stdout + result.stderr).strip()

    if "GATE BLOCKED" in gate_output:
        print(f"NO WORK\nReason: gate blocked for step '{next_step}': {gate_output}")
        return

    if "GATE OPEN" not in gate_output:
        print(
            f"NO WORK\n"
            f"Reason: pipeline_gate.py returned unexpected output for '{next_step}':\n{gate_output}"
        )
        return

    # 5. Print dispatch instructions
    run_dir = f"memory/pipeline/runs/{run_id}"
    output_file = f"{run_dir}/{STEP_OUTPUT[next_step]}"
    skill_file = STEP_SKILL[next_step]
    complete_cmd = f"python3 /workspace/tools/pipeline_complete.py {next_step} {output_file}"

    print("DISPATCH READY")
    print(f"Run: {run_id}")
    print(f"Step: {next_step}")
    print(f"Skill: {skill_file}")
    print(f"RunDir: {run_dir}")
    print(f"Complete: {complete_cmd}")


if __name__ == "__main__":
    main()
