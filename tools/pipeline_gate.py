#!/usr/bin/env python3
"""
pipeline_gate.py — Hard gate check before executing a pipeline step.

Usage:
    python3 /workspace/tools/pipeline_gate.py <step>

Returns exit code 0 if the gate is OPEN (allowed to proceed).
Returns exit code 1 if the gate is BLOCKED — agent MUST STOP.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

STEP_ORDER = [
    "scout", "scout-deepen",
    "curator:rank", "curator:angle",
    "researcher:plan", "researcher:q1", "researcher:q2", "researcher:q3", "researcher:q4", "researcher:compile",
    "writer:lead", "writer:body", "writer:close", "writer:merge",
    "verifier:run1", "verifier:check1", "verifier:check2", "verifier:check3", "verifier:compile",
    "editor:structure", "editor:voice",
    "grounder", "referee", "librarian", "illustrator",
    "publisher:stage", "publisher:post",
]
THRESHOLDS = {
    "scout":             0.5,
    "scout-deepen":      0.5,
    "curator:rank":      0.7,
    "curator:angle":     0.7,
    "researcher:plan":   0.6,
    "researcher:q1":     0.6,
    "researcher:q2":     0.6,
    "researcher:q3":     0.6,
    "researcher:q4":     0.6,
    "researcher:compile":0.6,
    "writer:lead":       0.6,
    "writer:body":       0.6,
    "writer:close":      0.6,
    "writer:merge":      0.7,
    "verifier:run1":     0.5,
    "verifier:check1":   0.5,
    "verifier:check2":   0.5,
    "verifier:check3":   0.5,
    "verifier:compile":  0.7,
    "editor:structure":  0.7,
    "editor:voice":      0.7,
    "grounder":          1.0,
    "referee":           0.65,
    "librarian":         1.0,
    "illustrator":       1.0,
    "publisher:stage":   1.0,
    "publisher:post":    1.0,
}
# Normalize legacy dash-format to colon-format
_DASH_TO_COLON = {
    "writer-lead": "writer:lead", "writer-body": "writer:body",
    "writer-close": "writer:close", "writer-merge": "writer:merge",
    "curator-rank": "curator:rank", "curator-angle": "curator:angle",
    "researcher-plan": "researcher:plan", "researcher-compile": "researcher:compile",
    "researcher-q1": "researcher:q1", "researcher-q2": "researcher:q2",
    "researcher-q3": "researcher:q3", "researcher-q4": "researcher:q4",
    "verifier-run1": "verifier:run1", "verifier-check1": "verifier:check1",
    "verifier-check2": "verifier:check2", "verifier-check3": "verifier:check3",
    "verifier-compile": "verifier:compile",
    "editor-structure": "editor:structure", "editor-voice": "editor:voice",
    "publisher-stage": "publisher:stage", "publisher-post": "publisher:post",
}
REFEREE_RETRY_TARGETS = {"editor:structure", "editor:voice", "writer:body", "writer:close"}
MAX_ATTEMPTS = 3
PIPELINE_DIR = Path("/workspace/memory/pipeline")
ACTIVE_FILE = PIPELINE_DIR / "active.json"


def fail(msg: str) -> None:
    print(f"GATE BLOCKED: {msg}", flush=True)
    sys.exit(1)


def ok(run_id: str, step: str, attempts: int) -> None:
    print(f"GATE OPEN: run={run_id} step={step} attempt={attempts + 1}/{MAX_ATTEMPTS}", flush=True)
    sys.exit(0)


if len(sys.argv) < 2:
    fail("No step provided. Usage: pipeline_gate.py <step>")

step = sys.argv[1].lower()
step = _DASH_TO_COLON.get(step, step)
if step not in STEP_ORDER:
    fail(f"Unknown step '{step}'. Must be one of: {', '.join(STEP_ORDER)}")

# --- Read active run ---
if not ACTIVE_FILE.exists():
    if step == "scout":
        # Scout can always start — it creates the run
        print("GATE OPEN: no active run — scout will create one", flush=True)
        sys.exit(0)
    fail("No active.json found. Scout must run first to create a run.")

active = json.loads(ACTIVE_FILE.read_text())
run_id = active.get("run_id")

if not run_id:
    if step == "scout":
        print("GATE OPEN: no active run — scout will create one", flush=True)
        sys.exit(0)
    fail("active.json has no run_id. Scout must run first.")

# --- Read state ---
state_file = PIPELINE_DIR / "runs" / run_id / "state.json"
if not state_file.exists():
    fail(f"state.json not found for run {run_id}. Corrupted pipeline state.")

state = json.loads(state_file.read_text())
steps = state.get("steps", {})

# --- Check this step is not already done ---
this_step_state = steps.get(step, {})
if this_step_state.get("status") == "done":
    fail(f"Step '{step}' is already done (score={this_step_state.get('score')}). Do not re-run a completed step.")

# --- Referee retry: steps that may be re-entered after a NEEDS_WORK verdict ---
# If the step is a known referee retry target and state.json marks it as "referee-retry",
# allow it even if the next-in-line step is not its direct predecessor.
this_status = this_step_state.get("status", "")
if this_status == "referee-retry" and step in REFEREE_RETRY_TARGETS:
    # Gate is open for retry — skip linear predecessor check below
    attempts = this_step_state.get("attempts", 0)
    if attempts >= MAX_ATTEMPTS:
        fail(f"Step '{step}' has reached max attempts ({MAX_ATTEMPTS}) via referee retry. Run is FAILED.")
    now = datetime.now(timezone.utc).isoformat()
    state["steps"][step] = {**this_step_state, "status": "in-progress", "started": now, "attempts": attempts}
    state["current_step"] = step
    state_file.write_text(json.dumps(state, indent=2))
    ok(run_id, step, attempts)
    # ok() calls sys.exit(0) — code below not reached
attempts = this_step_state.get("attempts", 0)
if attempts >= MAX_ATTEMPTS:
    fail(f"Step '{step}' has reached max attempts ({MAX_ATTEMPTS}). Run is FAILED. Clear active.json to start fresh.")

# --- Check previous step is done with passing score ---
if step != "scout":
    prev_step = STEP_ORDER[STEP_ORDER.index(step) - 1]
    prev_state = steps.get(prev_step, {})
    if prev_state.get("status") != "done":
        fail(
            f"Previous step '{prev_step}' is not done "
            f"(status={prev_state.get('status', 'missing')}, "
            f"score={prev_state.get('score')}). "
            f"Complete '{prev_step}' with score >= {THRESHOLDS[prev_step]} before running '{step}'."
        )
    prev_score = prev_state.get("score", 0) or 0
    if prev_score < THRESHOLDS[prev_step]:
        fail(
            f"Previous step '{prev_step}' score {prev_score:.2f} is below threshold "
            f"{THRESHOLDS[prev_step]}. Cannot proceed to '{step}'."
        )

# --- Check no other step is currently in-progress ---
for s in STEP_ORDER:
    if s == step:
        continue
    if steps.get(s, {}).get("status") == "in-progress":
        fail(
            f"Step '{s}' is currently in-progress. "
            f"Only one step may run at a time. "
            f"Complete or cancel '{s}' before starting '{step}'."
        )

# --- Mark step as in-progress atomically ---
now = datetime.now(timezone.utc).isoformat()
state["steps"][step] = {
    **this_step_state,
    "status": "in-progress",
    "started": now,
    "attempts": attempts,
}
state["current_step"] = step
state_file.write_text(json.dumps(state, indent=2))

ok(run_id, step, attempts)
