#!/usr/bin/env python3
"""
pipeline_merge.py — Mechanically merge draft parts into draft-v1.md.

Usage:
    python3 /workspace/tools/pipeline_merge.py <run_dir>

Example:
    python3 /workspace/tools/pipeline_merge.py memory/pipeline/runs/2026-05-12-federalist-surge-v3

This tool concatenates:
  1. draft-v1-lead.md  (full content, includes YAML frontmatter)
  2. draft-v1-body.md  (full content, appended after lead)
  3. draft-v1-close.md (full content, appended after body)
  4. Sources block built from curated-sources.md

Output: {run_dir}/draft-v1.md

Word count (excluding frontmatter and bluesky comment block) is printed.
"""
import re
import sys
from pathlib import Path

WORKSPACE = Path("/workspace")


def extract_urls_from_curated(curated: str) -> list[tuple[str, str]]:
    """Return list of (url, description) from Primary and Secondary sources sections."""
    results = []
    in_sources = False
    for line in curated.splitlines():
        if line.startswith("## Primary sources") or line.startswith("## Secondary sources"):
            in_sources = True
            continue
        if line.startswith("## ") and in_sources:
            in_sources = False
            continue
        if in_sources and line.startswith("- http"):
            parts = line[2:].split(" — ", 1)
            url = parts[0].strip()
            desc = parts[1].strip() if len(parts) > 1 else ""
            results.append((url, desc))
    return results


def word_count_body(content: str) -> int:
    """Count words excluding YAML frontmatter and bluesky_thread comment block."""
    # Remove YAML frontmatter
    if content.startswith("---"):
        end = content.find("\n---", 3)
        if end != -1:
            content = content[end + 4:]
    # Remove bluesky_thread HTML comment
    content = re.sub(r'<!--\s*bluesky_thread.*?-->', '', content, flags=re.DOTALL)
    # Remove markdown ## Bluesky Thread section (alternative format)
    content = re.sub(r'## Bluesky Thread.*', '', content, flags=re.DOTALL)
    return len(content.split())


def main():
    if len(sys.argv) < 2:
        print("ERROR: Usage: pipeline_merge.py <run_dir>")
        sys.exit(1)

    run_dir_arg = sys.argv[1]
    # Support both relative (from workspace) and absolute paths
    run_dir = Path(run_dir_arg) if run_dir_arg.startswith("/") else WORKSPACE / run_dir_arg

    lead_file = run_dir / "draft-v1-lead.md"
    body_file = run_dir / "draft-v1-body.md"
    close_file = run_dir / "draft-v1-close.md"
    curated_file = run_dir / "curated-sources.md"
    output_file = run_dir / "draft-v1.md"

    missing = [f for f in [lead_file, body_file, close_file, curated_file] if not f.exists()]
    if missing:
        print(f"ERROR: Missing input files: {[str(f) for f in missing]}")
        sys.exit(1)

    lead = lead_file.read_text().rstrip()
    body = body_file.read_text().rstrip()
    close = close_file.read_text().rstrip()
    curated = curated_file.read_text()

    # Build sources block from curated-sources.md
    urls = extract_urls_from_curated(curated)
    if urls:
        sources_lines = ["", "## Sources", ""]
        for url, desc in urls:
            label = desc.split("—")[0].strip() if desc else url
            # Use description as label if it looks like a title, else use domain
            if len(label) > 80 or not label:
                label = url.split("/")[2]  # domain fallback
            sources_lines.append(f"- [{label}]({url})")
        sources_block = "\n".join(sources_lines)
    else:
        sources_block = "\n## Sources\n\n*No sources listed in curated-sources.md.*"

    # Concatenate
    merged = f"{lead}\n\n{body}\n\n{close}\n{sources_block}\n"
    output_file.write_text(merged)

    wc = word_count_body(merged)
    print(f"MERGE COMPLETE")
    print(f"Output: {output_file}")
    print(f"Word count (body): {wc}")
    print(f"Parts: lead={len(lead.split())}w body={len(body.split())}w close={len(close.split())}w sources={len(sources_block.split())}w")

    if wc < 700:
        print(f"WARNING: Word count {wc} is below target (700-1100). Body sections may be too thin.")
    elif wc > 1100:
        print(f"WARNING: Word count {wc} exceeds target (700-1100). Consider trimming.")
    else:
        print(f"OK: Word count {wc} within target range 700-1100.")


if __name__ == "__main__":
    main()
