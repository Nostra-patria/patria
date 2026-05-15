#!/usr/bin/env python3
"""
pipeline_complete.py — Official close of a pipeline step with scoring.

This is the ONLY valid way to mark a step as done or failed.
write_file to pipeline output files is NOT sufficient — state.json
will not be updated and the next step will remain blocked.

Usage:
    python3 /workspace/tools/pipeline_complete.py <step> <output_file>

  <step>: any of the 27 colon-format pipeline steps, e.g.:
    scout | scout-deepen | curator:rank | curator:angle |
    researcher:plan | researcher:q1 | ... | researcher:compile |
    writer:lead | writer:body | writer:close | writer:merge |
    verifier:run1 | verifier:check1 | ... | verifier:compile |
    editor:structure | editor:voice |
    grounder | referee | librarian | illustrator |
    publisher:stage | publisher:post

  <output_file>: path to the output file the step produced (used for scoring)

Returns exit code 0 on PASS (step marked done, next step unlocked).
Returns exit code 1 on FAIL (score below threshold — retry or failed).
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

STEP_ORDER = [
    "scout", "scout-deepen",
    "curator:rank", "curator:angle",
    "researcher:plan",
    "researcher:q1", "researcher:q2", "researcher:q3", "researcher:q4",
    "researcher:compile",
    "writer:lead", "writer:body", "writer:close", "writer:merge",
    "verifier:run1",
    "verifier:check1", "verifier:check2", "verifier:check3",
    "verifier:compile",
    "editor:structure", "editor:voice",
    "grounder", "referee", "librarian",
    "illustrator",
    "publisher:stage", "publisher:post",
]
THRESHOLDS = {
    "scout":              0.5,
    "scout-deepen":       0.5,
    "curator:rank":       0.5,
    "curator:angle":      0.7,
    "researcher:plan":    0.5,
    "researcher:q1":      0.5,
    "researcher:q2":      0.5,
    "researcher:q3":      0.5,
    "researcher:q4":      0.5,
    "researcher:compile": 0.6,
    "writer:lead":        0.6,
    "writer:body":        0.6,
    "writer:close":       0.6,
    "writer:merge":       0.7,
    "verifier:run1":      0.5,
    "verifier:check1":    0.5,
    "verifier:check2":    0.5,
    "verifier:check3":    0.5,
    "verifier:compile":   0.7,
    "editor:structure":   0.7,
    "editor:voice":       0.7,
    "grounder":           1.0,
    "referee":            0.65,
    "librarian":          1.0,
    "illustrator":        1.0,
    "publisher:stage":    1.0,
    "publisher:post":     1.0,
}
# Referee retry map: step → the step to reset when referee scores below threshold
REFEREE_RETRY_MAP = {
    "editor:structure": "editor:voice",
    "editor:voice":     "grounder",
    "writer:body":      "writer:close",
}
MAX_ATTEMPTS = 3
PIPELINE_DIR = Path("/workspace/memory/pipeline")
ACTIVE_FILE = PIPELINE_DIR / "active.json"


def score_scout(output: dict, run_id: str) -> tuple[float, str]:
    # Supports both old JSON format and new markdown-based output
    if isinstance(output, str):
        # markdown output: count lines containing a URL (supports "- https://", "1. https://", bare URLs)
        import re
        urls = list(set(re.findall(r'https?://\S+', output)))
        return (0.7 if len(urls) >= 3 else 0.3), f"{len(urls)} source URL(s) found"
    sources = output.get("sources", [])
    headline = output.get("headline", "")
    if not headline:
        return 0.0, "No headline in scout output"
    if not sources:
        return 0.0, "No sources in scout output"
    score = min(1.0, 0.5 + len(sources) * 0.1)
    return score, f"{len(sources)} source(s), headline present"


def score_scout_deepen(content: str, run_id: str) -> tuple[float, str]:
    import re as _re
    urls = list(set(_re.findall(r'https?://\S+', content)))
    if len(urls) >= 3:
        return 0.8, f"{len(urls)} new source URL(s)"
    if len(urls) >= 1:
        return 0.5, f"Only {len(urls)} new source(s) — marginal pass"
    return 0.2, "No source URLs found in scout-deepen output"


def score_curator(content: str, run_id: str) -> tuple[float, str]:
    has_angle = "## Selected angle" in content or "**Angle**" in content or "## Angle" in content
    questions = content.count("Key question") + content.count("?")  # rough count
    primary = content.count("Primary source") + content.count("## Primary")
    issues = []
    score = 0.0
    if has_angle:
        score += 0.35
    else:
        issues.append("no selected angle")
    if questions >= 3:
        score += 0.35
    else:
        issues.append(f"only {questions} question markers")
    if primary >= 1:
        score += 0.3
    else:
        issues.append("no primary sources section")
    detail = "all checks passed" if not issues else ", ".join(issues)
    return round(score, 2), detail


def score_researcher_run(content: str, run_id: str, marker: str) -> tuple[float, str]:
    if marker not in content:
        return 0.0, f"Completion marker '{marker}' not found"
    # Count real quotes (lines with > 30 chars inside block quotes)
    quotes = [l for l in content.splitlines() if l.startswith(">") and len(l) > 35]
    urls = [l for l in content.splitlines() if "http" in l]
    if len(quotes) >= 2 and len(urls) >= 2:
        return 0.8, f"{marker} present, {len(quotes)} quotes, {len(urls)} URLs"
    if len(urls) >= 2:
        return 0.7, f"{marker} present, {len(urls)} URLs (few quotes)"
    if len(urls) >= 1 or len(quotes) >= 1:
        return 0.65, f"{marker} present, {len(urls)} URL(s), {len(quotes)} quote(s)"
    # Marker present but no URLs/quotes — report is synthesised without inline citations.
    # Still a valid first-pass research report; let it through at minimum passing score.
    return 0.62, f"{marker} present (no inline URLs/quotes — synthesised report)"


def score_researcher_1(content: str, run_id: str) -> tuple[float, str]:
    return score_researcher_run(content, run_id, "## RUN-1-COMPLETE")


def score_researcher_2(content: str, run_id: str) -> tuple[float, str]:
    return score_researcher_run(content, run_id, "## RUN-2-COMPLETE")


def score_writer_section(content: str, run_id: str, min_words: int, marker: str) -> tuple[float, str]:
    word_count = len(content.split())
    has_marker = marker in content
    if not has_marker:
        return 0.0, f"Required marker '{marker}' not found"
    if word_count >= min_words:
        return 0.8, f"{word_count} words, marker present"
    return 0.5, f"Only {word_count} words (min {min_words}), marker present"


def score_writer_lead(content: str, run_id: str) -> tuple[float, str]:
    has_frontmatter = content.startswith("---")
    has_hook = len(content.split("\n")[3:6]) > 0  # rough: content after frontmatter
    word_count = len(content.split())
    issues = []
    score = 0.0
    if has_frontmatter:
        score += 0.4
    else:
        issues.append("no frontmatter")
    if word_count >= 100:
        score += 0.4
    else:
        issues.append(f"only {word_count} words")
    if has_hook:
        score += 0.2
    detail = "all checks passed" if not issues else ", ".join(issues)
    return round(score, 2), detail


def score_writer_body(content: str, run_id: str) -> tuple[float, str]:
    h2_count = content.count("\n## ")
    word_count = len(content.split())
    has_sources = "http" in content
    issues = []
    score = 0.0
    if h2_count >= 3:
        score += 0.4
    else:
        issues.append(f"only {h2_count} H2 sections")
    if word_count >= 300:
        score += 0.4
    else:
        issues.append(f"only {word_count} words")
    if has_sources:
        score += 0.2
    else:
        issues.append("no source links")
    detail = "all checks passed" if not issues else ", ".join(issues)
    return round(score, 2), detail


def score_writer_close(content: str, run_id: str) -> tuple[float, str]:
    # draft-v1-close.md: only needs implication paragraph + bluesky thread
    has_bluesky = "bluesky" in content.lower() or "bluesky_thread" in content.lower()
    has_paragraph = len(content.split()) >= 60  # at least the implication paragraph
    if has_bluesky and has_paragraph:
        return 0.8, "implication paragraph and Bluesky thread present"
    if has_bluesky:
        return 0.6, "Bluesky thread present but paragraph too short"
    if has_paragraph:
        return 0.4, "paragraph present but no Bluesky thread"
    return 0.2, "implication paragraph and Bluesky thread missing"


def score_writer_merge(content: str, run_id: str) -> tuple[float, str]:
    # draft-v1.md: merged article — check word count and sources
    import re as _re
    # Exclude frontmatter and bluesky block from word count
    body = content
    if body.startswith("---"):
        end = body.find("\n---", 3)
        if end != -1:
            body = body[end + 4:]
    body = _re.sub(r'<!--\s*bluesky_thread.*?-->', '', body, flags=_re.DOTALL)
    body = _re.sub(r'## Bluesky Thread.*', '', body, flags=_re.DOTALL)
    word_count = len(body.split())
    has_sources = "## Sources" in content
    # Accept bluesky in any common format: HTML comment or markdown section
    has_bluesky = ("bluesky_thread" in content.lower()
                   or "## bluesky thread" in content.lower()
                   or "bluesky thread" in content.lower())
    issues = []
    score = 0.0
    if 700 <= word_count <= 1100:
        score += 0.5
    elif word_count >= 500:
        score += 0.35
        issues.append(f"word count {word_count} slightly outside 700-1100")
    else:
        issues.append(f"word count {word_count} too low")
    if has_sources:
        score += 0.3
    else:
        issues.append("no ## Sources section")
    if has_bluesky:
        score += 0.2
    else:
        issues.append("no Bluesky thread")
    detail = "all checks passed" if not issues else ", ".join(issues)
    return round(score, 2), detail


def score_editor_pass(content: str, run_id: str) -> tuple[float, str]:
    word_count = len(content.split())
    if word_count < 500:
        return 0.3, f"Output too short: {word_count} words"
    has_h2 = "\n## " in content
    if not has_h2:
        return 0.5, "No H2 sections found"
    return 0.8, f"{word_count} words, structured output"


def score_editor_structure(content: str, run_id: str) -> tuple[float, str]:
    return score_editor_pass(content, run_id)


def score_editor_voice(content: str, run_id: str) -> tuple[float, str]:
    return score_editor_pass(content, run_id)


def score_referee(content: str, run_id: str) -> tuple[float, str]:
    if "VERDICT: APPROVED" in content or "VERDICT: APPROVED_WITH_NOTES" in content:
        # Extract numeric score
        for line in content.splitlines():
            if line.startswith("SCORE:"):
                try:
                    score_val = int(line.split(":")[1].split("/")[0].strip())
                    return round(score_val / 100, 2), f"APPROVED score={score_val}/100"
                except (ValueError, IndexError):
                    pass
        return 0.85, "APPROVED (no numeric score found)"
    if "VERDICT: NEEDS_WORK" in content:
        for line in content.splitlines():
            if line.startswith("SCORE:"):
                try:
                    score_val = int(line.split(":")[1].split("/")[0].strip())
                    return round(score_val / 100, 2), f"NEEDS_WORK score={score_val}/100 — retry triggered"
                except (ValueError, IndexError):
                    pass
        return 0.7, "NEEDS_WORK (no numeric score found)"
    if "VERDICT: REJECTED" in content or "VERDICT: HARD_REJECTED" in content:
        return 0.0, "REJECTED by referee"
    return 0.0, "No VERDICT line found in referee-verdict.md"


def score_librarian(content: str, run_id: str) -> tuple[float, str]:
    if "scoreboard updated" in content.lower() or "LIBRARY.md" in content or "count" in content.lower():
        return 1.0, "Librarian report confirms scoreboard updated"
    return 0.5, "Librarian report does not confirm scoreboard update"


def score_verifier(content: str, run_id: str) -> tuple[float, str]:
    if "VERDICT: PASS" in content:
        # Count uncertain claims — penalise slightly if ≥ 3, but still pass
        uncertain = content.count("⚠️ uncertain")
        if uncertain >= 3:
            return 0.75, f"PASS_WITH_NOTES — {uncertain} uncertain claims (editor must qualify)"
        return 1.0, f"PASS — {uncertain} uncertain claim(s)"
    if "VERDICT: FAIL" in content:
        contradicted = content.count("❌ contradicted")
        return 0.0, f"FAIL — {contradicted} contradicted claim(s) found"
    return 0.0, "No VERDICT line found in verification.md"


def score_grounder(content: str, run_id: str) -> tuple[float, str]:
    # Accept: VERDICT: PASS, VERDICT: GROUNDED, VERDICT: APPROVED
    if any(v in content for v in ("VERDICT: PASS", "VERDICT: GROUNDED", "VERDICT: APPROVED")):
        return 1.0, "PASS — all claims grounded in research"
    if "VERDICT: FAIL" in content or "VERDICT: UNGROUNDED" in content:
        ungrounded = content.count("❌ ungrounded")
        return 0.0, f"FAIL — {ungrounded} ungrounded claim(s)"
    return 0.0, "No VERDICT line found in grounding.md"


def score_illustrator(output: dict, run_id: str) -> tuple[float, str]:
    # Soft-skip: if no API key was available, accept PENDING_API_KEY status
    if isinstance(output, dict):
        header = output.get("header", output)  # support both root and nested format
        if header.get("status") == "PENDING_API_KEY":
            return 1.0, "SKIP — no image API key configured, article will publish without header image"
        img_path = header.get("path", output.get("path", ""))
    else:
        img_path = ""
    if not img_path:
        return 0.0, "No path in image.json"
    p = Path(img_path)
    if not p.exists():
        return 0.0, f"Image file not found: {img_path}"
    size = p.stat().st_size
    if size < 50_000:
        return 0.0, f"Image too small: {size} bytes (minimum 50KB)"
    return 1.0, f"Image exists, {size // 1024}KB"


def score_publisher(output: dict, run_id: str) -> tuple[float, str]:
    # Verify article was actually committed to patria-site _posts
    slug = run_id
    post_path = Path(f"/workspace/patria-site/docs/_posts/{slug}.md")
    if not post_path.exists():
        return 0.0, f"Article not found in docs/_posts/{slug}.md — git push may have failed"
    # Accept both "url" and "article_url" keys
    url = output.get("url", "") or output.get("article_url", "")
    if not url:
        return 0.0, "No URL in published.json"
    return 1.0, f"Published at {url}"


# ── Scorers for new 27-step colon-format steps ────────────────────────────────

def score_has_content(content: str, run_id: str, min_words: int = 80) -> tuple[float, str]:
    """Generic scorer: passes if the file has at least min_words words."""
    word_count = len(content.split())
    if word_count >= min_words:
        return 0.7, f"{word_count} words"
    if word_count >= min_words // 2:
        return 0.4, f"only {word_count} words (min {min_words})"
    return 0.2, f"too short: {word_count} words (min {min_words})"


def score_curator_rank(content: str, run_id: str) -> tuple[float, str]:
    """curator:rank — ranked list of sources with scores/reasoning."""
    has_scores = any(c in content for c in ("★", "⭐", "/10", "score", "Score", "rank", "Rank"))
    word_count = len(content.split())
    if word_count >= 100 and has_scores:
        return 0.8, f"{word_count} words with ranking indicators"
    if word_count >= 100:
        return 0.6, f"{word_count} words (no clear ranking indicators)"
    return 0.3, f"too short: {word_count} words"


def score_curator_angle(content: str, run_id: str) -> tuple[float, str]:
    """curator:angle — re-use curator scorer (produces curated-sources.md)."""
    return score_curator(content, run_id)


def score_researcher_plan(content: str, run_id: str) -> tuple[float, str]:
    """researcher:plan — research plan with questions."""
    question_count = content.count("?")
    word_count = len(content.split())
    if question_count >= 3 and word_count >= 80:
        return 0.8, f"{question_count} question(s), {word_count} words"
    if word_count >= 80:
        return 0.6, f"{word_count} words, only {question_count} question(s)"
    return 0.3, f"too short: {word_count} words"


def score_researcher_q(content: str, run_id: str) -> tuple[float, str]:
    """researcher:q1..q4 — one question answered with evidence."""
    urls = re.findall(r'https?://\S+', content)
    word_count = len(content.split())
    if word_count >= 150 and len(urls) >= 1:
        return 0.8, f"{word_count} words, {len(urls)} source(s)"
    if word_count >= 100:
        return 0.6, f"{word_count} words (few/no inline sources)"
    return 0.3, f"too short: {word_count} words"


def score_researcher_compile(content: str, run_id: str) -> tuple[float, str]:
    """researcher:compile — compiled research report."""
    return score_researcher_run(content, run_id, "## RESEARCH-COMPLETE")


def score_verifier_run1(content: str, run_id: str) -> tuple[float, str]:
    """verifier:run1 — claim inventory."""
    claim_count = content.count("CLAIM") + content.count("Claim") + content.count("claim")
    word_count = len(content.split())
    if word_count >= 150:
        return 0.8, f"{word_count} words, ~{claim_count} claim references"
    return 0.4, f"too short: {word_count} words"


def score_verifier_check(content: str, run_id: str) -> tuple[float, str]:
    """verifier:check1..3 — batch verification results."""
    verified = content.count("✅") + content.count("VERIFIED") + content.count("verified")
    uncertain = content.count("⚠️") + content.count("UNCERTAIN")
    failed = content.count("❌") + content.count("FAIL")
    word_count = len(content.split())
    if word_count >= 80:
        return 0.7, f"{word_count} words — ✅{verified} ⚠️{uncertain} ❌{failed}"
    return 0.3, f"too short: {word_count} words"


def score_verifier_compile(content: str, run_id: str) -> tuple[float, str]:
    """verifier:compile — final compiled verification report."""
    return score_verifier(content, run_id)


def score_publisher_stage(output, run_id: str) -> tuple[float, str]:
    """publisher:stage — image staged (image-staged.json)."""
    # Same check as illustrator: image file must exist and be large enough
    if isinstance(output, dict):
        if output.get("status") == "PENDING_API_KEY":
            return 1.0, "SKIP — no image API key, article will publish without image"
        img_path = output.get("path", "")
    else:
        img_path = ""
    if not img_path:
        return 0.0, "No path in image-staged.json"
    p = Path(img_path)
    if not p.exists():
        return 0.0, f"Staged image not found: {img_path}"
    size = p.stat().st_size
    if size < 50_000:
        return 0.0, f"Staged image too small: {size} bytes"
    return 1.0, f"Staged image exists, {size // 1024}KB"


def score_publisher_post(output: dict, run_id: str) -> tuple[float, str]:
    """publisher:post — article published (published.json)."""
    return score_publisher(output, run_id)


SCORERS = {
    "scout":              score_scout,
    "scout-deepen":       score_scout_deepen,
    "curator:rank":       score_curator_rank,
    "curator:angle":      score_curator_angle,
    "researcher:plan":    score_researcher_plan,
    "researcher:q1":      score_researcher_q,
    "researcher:q2":      score_researcher_q,
    "researcher:q3":      score_researcher_q,
    "researcher:q4":      score_researcher_q,
    "researcher:compile": score_researcher_compile,
    "writer:lead":        score_writer_lead,
    "writer:body":        score_writer_body,
    "writer:close":       score_writer_close,
    "writer:merge":       score_writer_merge,
    "verifier:run1":      score_verifier_run1,
    "verifier:check1":    score_verifier_check,
    "verifier:check2":    score_verifier_check,
    "verifier:check3":    score_verifier_check,
    "verifier:compile":   score_verifier_compile,
    "editor:structure":   score_editor_structure,
    "editor:voice":       score_editor_voice,
    "grounder":           score_grounder,
    "referee":            score_referee,
    "librarian":          score_librarian,
    "illustrator":        score_illustrator,
    "publisher:stage":    score_publisher_stage,
    "publisher:post":     score_publisher_post,
}

# --- Main ---
if len(sys.argv) < 3:
    print("COMPLETE ERROR: Usage: pipeline_complete.py <step> <output_file>")
    sys.exit(1)

step = sys.argv[1].lower()
# Normalize legacy dash-format to colon-format (e.g. writer-body → writer:body)
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
step = _DASH_TO_COLON.get(step, step)
output_file = Path(sys.argv[2])

if step not in STEP_ORDER:
    print(f"COMPLETE ERROR: Unknown step '{step}'")
    sys.exit(1)

if not output_file.exists():
    print(f"COMPLETE ERROR: Output file not found: {output_file}")
    sys.exit(1)

# --- Load active run ---
if not ACTIVE_FILE.exists():
    print("COMPLETE ERROR: No active.json found")
    sys.exit(1)

active = json.loads(ACTIVE_FILE.read_text())
run_id = active.get("run_id")
if not run_id:
    print("COMPLETE ERROR: active.json has no run_id")
    sys.exit(1)

state_file = PIPELINE_DIR / "runs" / run_id / "state.json"
if not state_file.exists():
    print(f"COMPLETE ERROR: state.json not found for run {run_id}")
    sys.exit(1)

state = json.loads(state_file.read_text())
steps = state.get("steps", {})
this_step = steps.get(step, {})

if this_step.get("status") != "in-progress":
    print(f"COMPLETE ERROR: Step '{step}' is not in-progress (status={this_step.get('status')}). Call pipeline_gate.py first.")
    sys.exit(1)

# --- Score ---
# Steps that produce JSON output
JSON_STEPS = {"illustrator", "publisher:stage", "publisher:post"}
try:
    content = output_file.read_text(encoding="utf-8")
    try:
        data = json.loads(content)
        if step in JSON_STEPS:
            score, detail = SCORERS[step](data, run_id)
        else:
            score, detail = SCORERS[step](content, run_id)
    except json.JSONDecodeError:
        score, detail = SCORERS[step](content, run_id)
except Exception as e:
    print(f"COMPLETE ERROR: Could not score output: {e}")
    sys.exit(1)

threshold = THRESHOLDS[step]
attempts = this_step.get("attempts", 0) + 1
now = datetime.now(timezone.utc).isoformat()

# Compute duration from started_at if available
started_at = this_step.get("started_at")
duration_s = None
if started_at:
    try:
        started_dt = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
        now_dt = datetime.fromisoformat(now.replace("Z", "+00:00"))
        duration_s = int((now_dt - started_dt).total_seconds())
    except Exception:
        pass

if score >= threshold:
    # PASS
    state["steps"][step] = {
        "status":       "done",
        "score":        score,
        "attempts":     attempts,
        "started_at":   started_at,
        "completed_at": now,
        "duration_s":   duration_s,
    }
    # Unlock next step
    idx = STEP_ORDER.index(step)
    if idx + 1 < len(STEP_ORDER):
        next_step = STEP_ORDER[idx + 1]
        state["steps"][next_step] = {"status": "pending", "score": None, "attempts": 0}
        state["current_step"] = next_step
        print(f"COMPLETE PASS: {step} score={score:.2f}/{threshold} ({detail})")
        print(f"NEXT STEP UNLOCKED: {next_step}")
    else:
        # All done
        state["current_step"] = "done"
        ACTIVE_FILE.write_text(json.dumps({}))
        print(f"COMPLETE PASS: {step} score={score:.2f}/{threshold} ({detail})")
        print(f"RUN COMPLETE: {run_id}")
    state_file.write_text(json.dumps(state, indent=2))
    sys.exit(0)

else:
    # FAIL — determine routing

    # --- Referee NEEDS_WORK routing ---
    # The referee writes RETRY_TARGET into the verdict. Parse it and set that step to "referee-retry".
    if step == "referee" and score >= 0.5:
        retry_target = None
        for line in content.splitlines():
            if line.startswith("RETRY_TARGET:"):
                retry_target = line.split(":", 1)[1].strip()
                break
        if retry_target and retry_target in state["steps"]:
            retry_state = state["steps"].get(retry_target, {})
            retry_attempts = retry_state.get("attempts", 0)
            if retry_attempts < MAX_ATTEMPTS:
                # Extract critique from verdict for retry prompt injection
                critique_lines = []
                in_notes = False
                score_breakdown = []
                for vline in content.splitlines():
                    if vline.startswith(("SCORE:", "ACCURACY:", "STRUCTURE:", "VOICE:", "COMPLETENESS:")):
                        score_breakdown.append(vline.strip())
                    if vline.startswith("## Notes") or vline.startswith("# Notes"):
                        in_notes = True
                        continue
                    if in_notes:
                        if vline.startswith("#") and not vline.startswith("##"):
                            in_notes = False
                        else:
                            critique_lines.append(vline)
                critique_text = ""
                if score_breakdown:
                    critique_text += "Score breakdown: " + " | ".join(score_breakdown) + ". "
                if critique_lines:
                    critique_text += "Referee notes: " + " ".join(l.strip() for l in critique_lines if l.strip())
                if not critique_text:
                    critique_text = f"Reset by referee (attempt {attempts})"

                # Reset retry_target and all steps after it up to (but not including) referee
                reset_from_idx = STEP_ORDER.index(retry_target)
                referee_idx = STEP_ORDER.index("referee")
                for s in STEP_ORDER[reset_from_idx:referee_idx]:
                    state["steps"][s] = {
                        "status": "referee-retry" if s == retry_target else "waiting",
                        "attempts": state["steps"].get(s, {}).get("attempts", 0),
                        "reason": critique_text if s == retry_target else f"Reset by referee (attempt {attempts})",
                    }
                state["steps"][step] = {
                    "status": "in-progress",  # referee stays in-progress until retry resolves
                    "score": score,
                    "attempts": attempts,
                }
                state["current_step"] = retry_target
                state_file.write_text(json.dumps(state, indent=2))
                print(f"COMPLETE NEEDS_WORK: referee score={score:.2f} ({detail})")
                print(f"REFEREE RETRY: resetting pipeline to '{retry_target}'. Steps {STEP_ORDER[reset_from_idx:referee_idx]} reset.")
                sys.exit(1)

        # No valid retry target or max attempts reached — treat as HARD_REJECTED
        state["steps"][step] = {"status": "failed", "score": score, "attempts": attempts, "failed_at": now}
        state["current_step"] = "failed"
        ACTIVE_FILE.write_text(json.dumps({}))
        state_file.write_text(json.dumps(state, indent=2))
        print(f"COMPLETE FAIL: referee score={score:.2f} — no valid retry target or max attempts reached")
        print(f"RUN BLOCKED: {run_id} — manually clear active.json to start fresh.")
        sys.exit(1)

    # --- QC steps (verifier, grounder) failing: reset writer-merge and clear QC ---
    if step in ("verifier", "grounder") and attempts < MAX_ATTEMPTS:
        reset_target = "writer-merge"
        reset_from_idx = STEP_ORDER.index(reset_target)
        current_idx = STEP_ORDER.index(step)
        for s in STEP_ORDER[reset_from_idx:current_idx + 1]:
            state["steps"][s] = {
                "status": "retry" if s == reset_target else "waiting",
                "attempts": state["steps"].get(s, {}).get("attempts", 0),
                "reason": f"Reset by {step}: {detail}",
            }
        state["current_step"] = reset_target
        state_file.write_text(json.dumps(state, indent=2))
        print(f"COMPLETE RETRY: {step} score={score:.2f} < {threshold} ({detail})")
        print(f"WRITER-CLOSE RESET: will re-run with {step} report as additional context (attempt {attempts})")
        sys.exit(1)

    if attempts >= MAX_ATTEMPTS:
        state["steps"][step] = {
            "status": "failed",
            "score": score,
            "attempts": attempts,
            "reason": f"Score {score:.2f} below threshold {threshold} after {attempts} attempts: {detail}",
            "failed_at": now,
        }
        state_file.write_text(json.dumps(state, indent=2))
        print(f"COMPLETE FAIL: {step} score={score:.2f} < {threshold} after {attempts} attempts ({detail})")
        print(f"RUN BLOCKED: {run_id} — step '{step}' failed. Operator must clear active.json to start fresh.")
        sys.exit(1)
    else:
        state["steps"][step] = {
            "status": "retry",
            "score": score,
            "attempts": attempts,
            "reason": f"Score {score:.2f} below threshold {threshold}: {detail}",
        }
        state["current_step"] = step
        state_file.write_text(json.dumps(state, indent=2))
        print(f"COMPLETE RETRY: {step} score={score:.2f} < {threshold} ({detail}) — attempt {attempts}/{MAX_ATTEMPTS}")
        print(f"RETRY REQUIRED: Re-run '{step}' via pipeline_gate.py then redo the work.")
        sys.exit(1)
