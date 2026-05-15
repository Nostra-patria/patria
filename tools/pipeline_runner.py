#!/usr/bin/env python3
"""
pipeline_runner.py -- Fast state-machine orchestrator for the Patria pipeline.

Exits in <10s. Outputs one of:
  SKILL_PROMPT:\n{skill_text}   -> cron message tells LLM to execute this
  ACTIVE: {step} ...            -> step running, LLM should do nothing
  NO WORK: ...                  -> nothing to do
  INTEGRITY_RESET: ...          -> file missing, reset applied, next tick dispatches
  RUN COMPLETE: {run_id}        -> all steps done

Usage:
    python3 /workspace/tools/pipeline_runner.py
    python3 /workspace/tools/pipeline_runner.py --step researcher-2
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# -- Config -------------------------------------------------------------------
WORKSPACE    = Path("/workspace")
PIPELINE_DIR = WORKSPACE / "memory" / "pipeline"
ACTIVE_FILE  = PIPELINE_DIR / "active.json"

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

STEP_TIMEOUTS = {
    "scout":            300,
    "scout-deepen":     300,
    "curator":          600,
    "researcher-1":     480,
    "researcher-2":     480,
    "writer-lead":      300,
    "writer-body":      360,
    "writer-close":     240,
    "writer-merge":     120,
    "verifier":         300,
    "editor-structure": 360,
    "editor-voice":     360,
    "grounder":         300,
    "referee":          240,
    "librarian":        180,
    "illustrator":      180,
    "publisher":        300,
}

PREREQUISITES = {
    "scout-deepen":     "scout-notes.md",
    "curator":          "scout-notes-deepen.md",
    "researcher-1":     "curated-sources.md",
    "researcher-2":     "research-report.md",
    "writer-lead":      "research-report.md",
    "writer-body":      "draft-v1-lead.md",
    "writer-close":     "draft-v1-body.md",
    "writer-merge":     "draft-v1-close.md",
    "verifier":         "draft-v1.md",
    "editor-structure": "verification-report.md",
    "editor-voice":     "draft-v2-structure.md",
    "grounder":         "draft-v2.md",
    "referee":          "draft-v2.md",
    "librarian":        "referee-verdict.md",
    "illustrator":      "draft-v2.md",
    "publisher":        "image.json",
}

STALE_INVALIDATORS = {
    "editor-structure": "verification-report.md",
    "editor-voice":     "draft-v2-structure.md",
}

# Files to pre-inject into skill prompts so the LLM never calls read_file in a loop.
# Format: {step: [filename, ...]}  — files injected in order into the prompt header.
INJECT_FILES = {
    "researcher-1": ["curated-sources.md"],
    "researcher-2": ["curated-sources.md", "research-report.md"],
    "writer-lead":  ["curated-sources.md", "research-report.md"],
    "writer-body":  ["curated-sources.md", "research-report.md", "draft-v1-lead.md"],
    "writer-close": ["curated-sources.md", "research-report.md", "draft-v1-lead.md", "draft-v1-body.md"],
    "writer-merge": ["draft-v1-lead.md", "draft-v1-body.md", "draft-v1-close.md"],
    "verifier":     ["draft-v1.md", "curated-sources.md"],
    "editor-structure": ["draft-v1.md", "verification-report.md"],
    "editor-voice":     ["draft-v2-structure.md"],
    "grounder":     ["draft-v2.md", "curated-sources.md"],
    "referee":      ["draft-v2.md", "grounding-report.md"],
    "librarian":    ["draft-v2.md", "referee-verdict.md"],
    "illustrator":  ["draft-v2.md", "curated-sources.md"],
    "publisher":    ["draft-v2.md", "image.json"],
}

# -- Helpers ------------------------------------------------------------------

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def die(msg):
    log(f"ABORT: {msg}")
    sys.exit(1)


def read_state(run_id):
    sf = PIPELINE_DIR / "runs" / run_id / "state.json"
    if not sf.exists():
        die(f"state.json not found for run {run_id}")
    return json.loads(sf.read_text())


def write_state(run_id, state):
    sf = PIPELINE_DIR / "runs" / run_id / "state.json"
    sf.write_text(json.dumps(state, indent=2))


def run_gate(step):
    result = subprocess.run(
        ["python3", "/workspace/tools/pipeline_gate.py", step],
        capture_output=True, text=True,
    )
    output = (result.stdout + result.stderr).strip()
    if "GATE OPEN" in output:
        log(f"Gate open for '{step}'")
        return True
    log(f"Gate blocked for '{step}': {output}")
    return False


def parse_urls_from_section(curated_path, section_header):
    """Extract bullet-point URLs from a named section of curated-sources.md."""
    urls = []
    in_section = False
    for line in Path(curated_path).read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            in_section = (section_header.lower() in stripped.lower())
            continue
        if in_section and stripped.startswith("- http"):
            # "- https://url — description" → extract URL part
            url = stripped[2:].split(" — ")[0].strip()
            if url:
                urls.append(url)
    return urls


def build_researcher_prompt(step, run_dir):
    """Build a minimal, direct task prompt for researcher-1 or researcher-2.
    Embeds the URLs directly so the LLM never needs to call read_file.
    """
    curated = run_dir / "curated-sources.md"
    output_file = run_dir / STEP_OUTPUT[step]

    if step == "researcher-1":
        urls = parse_urls_from_section(curated, "Primary sources")
        marker = "## RUN-1-COMPLETE"
        intro = "Fetch the primary sources below and write findings to research-report.md."
        # Also include key questions directly
        key_questions = []
        in_kq = False
        for line in curated.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s.startswith("## Key questions"):
                in_kq = True
                continue
            if in_kq and s.startswith("## "):
                break
            if in_kq and s:
                key_questions.append(s)
        kq_block = "\n".join(key_questions)
        angle = ""
        in_angle = False
        for line in curated.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s.startswith("## Selected angle"):
                in_angle = True
                continue
            if in_angle and s.startswith("## "):
                break
            if in_angle and s:
                angle = s
                break
        header_block = (
            f"Write this header first to {output_file} using write_file:\n"
            f"```\n"
            f"# Research Report — {run_dir.name}\n\n"
            f"**Angle**: {angle}\n\n"
            f"## Key questions\n{kq_block}\n\n"
            f"## Evidence\n"
            f"```\n\n"
        )
    else:  # researcher-2
        urls = parse_urls_from_section(curated, "Secondary sources")
        marker = "## RUN-2-COMPLETE"
        intro = "Fetch the secondary sources below and APPEND findings to research-report.md (do not overwrite researcher-1 output)."
        header_block = ""

    run_dir_str = str(run_dir)
    steps_block = ""
    for i, url in enumerate(urls, 1):
        steps_block += (
            f"Step {i}: web_fetch {url}\n"
            f"  Then: edit_file {output_file} — append section with findings (min 150 words, include quotes/stats)\n\n"
        )
    next_step_num = len(urls) + 1
    steps_block += (
        f"Step {next_step_num}: edit_file {output_file} — append exactly: {marker}\n\n"
        f"Step {next_step_num + 1}: exec python3 /workspace/tools/pipeline_complete.py {step} {output_file}\n"
    )

    return (
        f"# PIPELINE TASK: {step}\n"
        f"Run: {run_dir.name}\n\n"
        f"{intro}\n\n"
        f"⚠️  DO NOT call read_file. All required info is in this prompt. Start with Step 1 NOW.\n\n"
        + (header_block if step == "researcher-1" else "")
        + f"## URLs to fetch\n\n"
        + steps_block
    )


def _load_file(path):
    """Read file content or return placeholder if missing."""
    p = Path(path)
    return p.read_text(encoding="utf-8") if p.exists() else "(file not yet created)"


def build_grounder_prompt(run_dir):
    out = run_dir / "grounding-report.md"
    draft = _load_file(run_dir / "draft-v2.md")
    report = _load_file(run_dir / "research-report.md")
    return (
        f"# PIPELINE TASK: grounder\n"
        f"Run: {run_dir.name}\n\n"
        f"Verify every factual claim in the draft against the research report.\n\n"
        f"⚠️  DO NOT call read_file. Both files are pre-loaded below. Start with Step 1 NOW.\n\n"
        f"## PRE-LOADED: draft-v2.md\n\n```\n{draft}\n```\n\n"
        f"## PRE-LOADED: research-report.md\n\n```\n{report}\n```\n\n"
        f"## Steps\n\n"
        f"Step 1: write_file {out}\n"
        f"  Content: a Markdown table listing every factual claim from draft-v2.md above\n"
        f"  (claims = specific names, dates, numbers, stats, legislation refs, causal assertions)\n"
        f"  Table columns: # | Claim | Grounded?\n"
        f"  Mark each claim: ✅ grounded / ⚠️ inferred / ❌ ungrounded\n\n"
        f"Step 2: edit_file {out} — append one of:\n"
        f"  VERDICT: GROUNDED  (if zero ❌ items)\n"
        f"  VERDICT: FAIL — list each ❌ claim  (if any ❌ items)\n\n"
        f"Step 3: exec python3 /workspace/tools/pipeline_complete.py grounder {out}\n"
    )


def build_referee_prompt(run_dir):
    out = run_dir / "referee-verdict.md"
    draft = _load_file(run_dir / "draft-v2.md")
    verif = _load_file(run_dir / "verification-report.md")
    curated = _load_file(run_dir / "curated-sources.md")
    return (
        f"# PIPELINE TASK: referee\n"
        f"Run: {run_dir.name}\n\n"
        f"Score the draft on 4 criteria and issue a verdict. All files are pre-loaded.\n\n"
        f"⚠️  DO NOT call read_file. Start scoring NOW using the content below.\n\n"
        f"## PRE-LOADED: draft-v2.md\n\n```\n{draft}\n```\n\n"
        f"## PRE-LOADED: verification-report.md\n\n```\n{verif}\n```\n\n"
        f"## PRE-LOADED: curated-sources.md (for Key questions)\n\n```\n{curated}\n```\n\n"
        f"## Scoring\n\n"
        f"**Accuracy (0-40)**: Count ❌ claims from verification-report.md still in draft. 0=40pts, 1 unqualified=20pts, 2=10pts, 3+=0pts\n"
        f"**Structure (0-20)**: Hook=specific fact in first para? Each H2 opens with claim? Close=forward-looking? All 3=20, 2=15, 1=8, 0=0\n"
        f"**Voice (0-25)**: Check these 6 rules:\n"
        f"  1. Passive voice: more than 3 passive constructions? (-5)\n"
        f"  2. Marketing words: landmark/unprecedented/pivotal/crucial/vital/key/groundbreaking present? (-5)\n"
        f"  3. Dramatic framing: any of these present? 'signals the end of', 'survival' as geopolitical frame, 'The X Imperative', 'seismic', 'historic turning point', 'transforms X forever', opening sentence making a sweeping verdict. (-5)\n"
        f"  4. Padding phrases: 'it is important to note', 'needless to say', 'at the end of the day' present? (-5)\n"
        f"  5. Unlabelled opinion: analysis presented as fact without 'Patria\'s view:' or 'The data suggests...'? (-5)\n"
        f"  6. Monotonous rhythm: no short sentences following long ones? (-5)\n"
        f"  Score: 6 rules ok=25, 5=20, 4=15, 3=8, 2=4, 0-1=0\n"
        f"**Completeness (0-15)**: Key questions from curated-sources.md answered? 700-1100 words? All+ok=15, 3+=12, 2=8, 1=4, 0=0\n\n"
        f"TOTAL = sum. APPROVED ≥80 | NEEDS_WORK 65-79 | REJECTED <50\n\n"
        f"## Steps\n\n"
        f"Step 1: Score each criterion (write down scores before summing)\n\n"
        f"Step 2: write_file {out}\n"
        f"  Format:\n"
        f"  ATTEMPT: 1\n"
        f"  VERDICT: APPROVED (or NEEDS_WORK or REJECTED)\n"
        f"  SCORE: {{total}}/100\n"
        f"  ACCURACY: {{a}}/40\n"
        f"  STRUCTURE: {{s}}/20\n"
        f"  VOICE: {{v}}/25\n"
        f"  COMPLETENESS: {{c}}/15\n"
        f"  RETRY_TARGET: N/A (or step name if NEEDS_WORK)\n"
        f"  ## Notes\n"
        f"  {{one paragraph summary}}\n\n"
        f"Step 3: exec python3 /workspace/tools/pipeline_complete.py referee {out}\n"
    )


def build_librarian_prompt(run_dir):
    out = run_dir / "librarian-report.md"
    verdict = _load_file(run_dir / "referee-verdict.md")
    draft = _load_file(run_dir / "draft-v2.md")
    return (
        f"# PIPELINE TASK: librarian\n"
        f"Run: {run_dir.name}\n\n"
        f"Update scoreboard and library after referee approval.\n\n"
        f"⚠️  Files pre-loaded below. Only call read_file for scoreboard.json and LIBRARY.md (once each).\n\n"
        f"## PRE-LOADED: referee-verdict.md\n\n```\n{verdict}\n```\n\n"
        f"## PRE-LOADED: draft-v2.md (frontmatter only needed)\n\n```\n{draft[:800]}\n```\n\n"
        f"## Steps\n\n"
        f"Step 1: read_file /workspace/memory/scoreboard.json — check current star counts\n\n"
        f"Step 2: read_file /workspace/memory/LIBRARY.md — check current library entries\n\n"
        f"Step 3: write_file /workspace/memory/scoreboard.json — increment star count for the star in the draft frontmatter\n\n"
        f"Step 4: write_file /workspace/memory/LIBRARY.md — prepend new row to articles table:\n"
        f"  | {{date}} | [{{title}}](/patria/articles/{{slug}}/) | Star {{n}} — {{star_name}} | {{score}}/100 |\n\n"
        f"Step 5: write_file {out} — write librarian-report.md confirming what was updated\n\n"
        f"Step 6: exec python3 /workspace/tools/pipeline_complete.py librarian {out}\n"
    )


def build_prompt(step, run_dir):
    # Steps that get minimal direct prompts (avoids read_file loops)
    if step in ("researcher-1", "researcher-2"):
        return build_researcher_prompt(step, run_dir)
    if step == "grounder":
        return build_grounder_prompt(run_dir)
    if step == "referee":
        return build_referee_prompt(run_dir)
    if step == "librarian":
        return build_librarian_prompt(run_dir)

    skill_path = WORKSPACE / STEP_SKILL[step]
    if not skill_path.exists():
        die(f"SKILL.md not found: {skill_path}")
    skill_text = skill_path.read_text(encoding="utf-8")
    skill_text = skill_text.replace("{run_dir}", str(run_dir))
    skill_text = skill_text.replace("{RUN_DIR}", str(run_dir))
    output_file = run_dir / STEP_OUTPUT[step]
    header = (
        f"# PIPELINE STEP: {step}\n"
        f"Run directory: {run_dir}\n"
        f"Output file: {output_file}\n"
        f"Complete command: python3 /workspace/tools/pipeline_complete.py {step} {output_file}\n\n"
        f"---\n\n"
    )

    # Inject required file contents so LLM never needs to call read_file in a loop
    injected = ""
    for fname in INJECT_FILES.get(step, []):
        fpath = run_dir / fname
        if fpath.exists():
            content = fpath.read_text(encoding="utf-8")
            injected += f"## PRE-LOADED: {fname}\n\n```\n{content}\n```\n\n"
    if injected:
        header += (
            "## IMPORTANT: All required files are pre-loaded below.\n"
            "## Do NOT call read_file for any of these files — the content is already here.\n"
            "## Go directly to web_fetch (or the first write step) after reading this prompt.\n\n"
            + injected
            + "---\n\n"
        )

    return header + skill_text


# -- Main ---------------------------------------------------------------------

def main():
    force_step = None
    if "--step" in sys.argv:
        idx = sys.argv.index("--step")
        if idx + 1 < len(sys.argv):
            force_step = sys.argv[idx + 1]

    if not ACTIVE_FILE.exists():
        print("NO WORK: active.json does not exist")
        return

    try:
        active = json.loads(ACTIVE_FILE.read_text())
    except Exception as e:
        print(f"NO WORK: could not read active.json: {e}")
        return

    run_id = active.get("run_id")
    if not run_id:
        print("NO WORK: no active run")
        return

    run_dir = PIPELINE_DIR / "runs" / run_id
    if not run_dir.is_dir():
        print(f"NO WORK: run directory not found: {run_dir}")
        return

    state = read_state(run_id)
    steps = state.get("steps", {})

    # 2. Integrity sweep: reset done steps with missing output files
    for s in STEP_ORDER:
        if s == "researcher-2":
            continue  # shares research-report.md with researcher-1
        if steps.get(s, {}).get("status") != "done":
            continue
        out_file = run_dir / STEP_OUTPUT[s]
        if not out_file.exists():
            log(f"INTEGRITY: '{s}' done but '{STEP_OUTPUT[s]}' missing — reset to pending")
            state["steps"][s] = {"status": "pending", "score": None, "attempts": 0}
            idx = STEP_ORDER.index(s)
            for downstream in STEP_ORDER[idx + 1:]:
                if steps.get(downstream, {}).get("status") == "failed":
                    state["steps"][downstream] = {"status": "waiting", "score": None, "attempts": 0}
            write_state(run_id, state)
            print(f"INTEGRITY_RESET: '{s}' reset to pending — dispatching next tick")
            return

    state = read_state(run_id)
    steps = state.get("steps", {})

    # 3. Check for stale in-progress step (timed out)
    for s in STEP_ORDER:
        if steps.get(s, {}).get("status") != "in-progress":
            continue
        started_iso = steps[s].get("started", "")
        if started_iso:
            try:
                started_dt = datetime.fromisoformat(started_iso.replace("Z", "+00:00"))
                elapsed = (datetime.now(timezone.utc) - started_dt).total_seconds()
                timeout = STEP_TIMEOUTS.get(s, 480)
                if elapsed > timeout + 60:
                    attempts = steps[s].get("attempts", 0) + 1
                    new_status = "retry" if attempts < 3 else "failed"
                    log(f"TIMEOUT: '{s}' in-progress {elapsed:.0f}s > {timeout}s — {new_status}")
                    state["steps"][s] = {
                        "status": new_status,
                        "score": None,
                        "attempts": attempts,
                        "reason": f"Timed out after {elapsed:.0f}s",
                    }
                    write_state(run_id, state)
                    steps = state.get("steps", {})
                else:
                    print(f"ACTIVE: '{s}' in-progress ({elapsed:.0f}s / {timeout}s) — skip this tick")
                    return
            except Exception:
                pass

    # 4. Find next actionable step
    ACTIONABLE = {"pending", "waiting", "retry", "referee-retry"}
    next_step = force_step

    if not next_step:
        for s in STEP_ORDER:
            if steps.get(s, {}).get("status") in ACTIONABLE:
                next_step = s
                break

    if not next_step:
        all_done = all(steps.get(s, {}).get("status") == "done" for s in STEP_ORDER)
        if all_done:
            ACTIVE_FILE.write_text(json.dumps({}))
            print(f"RUN COMPLETE: {run_id}")
        else:
            failed = [s for s in STEP_ORDER if steps.get(s, {}).get("status") == "failed"]
            print(f"NO WORK: blocked — failed steps: {failed}")
        return

    log(f"Run: {run_id}  Step: {next_step}")

    # 5. Prerequisite guard
    prereq = PREREQUISITES.get(next_step)
    if prereq:
        prereq_path = run_dir / prereq
        if not prereq_path.exists():
            log(f"BLOCKED: prereq '{prereq}' missing for '{next_step}'")
            state["steps"][next_step] = {
                "status": "waiting",
                "score": None,
                "attempts": steps.get(next_step, {}).get("attempts", 0),
                "reason": f"Prerequisite '{prereq}' missing",
            }
            write_state(run_id, state)
            print(f"NO WORK: prerequisite '{prereq}' missing for '{next_step}'")
            return

    # 6. Stale-output invalidation
    output_path = run_dir / STEP_OUTPUT[next_step]
    inv_file = STALE_INVALIDATORS.get(next_step)
    if inv_file and output_path.exists():
        inv_path = run_dir / inv_file
        if inv_path.exists() and inv_path.stat().st_mtime > output_path.stat().st_mtime:
            log(f"Deleting stale '{output_path.name}' — '{inv_file}' is newer")
            output_path.unlink()

    # 7. Open gate (marks step as in-progress)
    if not run_gate(next_step):
        print(f"NO WORK: gate blocked for '{next_step}'")
        return

    # 8. Output skill prompt for LLM to execute
    prompt = build_prompt(next_step, run_dir)
    log(f"Dispatching '{next_step}' — outputting SKILL_PROMPT")
    print(f"\nSKILL_PROMPT:\n{prompt}")


if __name__ == "__main__":
    main()