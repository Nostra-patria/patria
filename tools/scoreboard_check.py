#!/usr/bin/env python3
"""
scoreboard_check.py — Pick the next Astra Europa Guiding Star to write about.

Logic: find the minimum article count across all 12 Stars.
       Among those tied at the minimum, pick the lowest Star number.

Output (stdout, two lines):
    STAR=<n> NAME="<name>" COUNT=<n>
    ANGLE="<1-sentence editorial frame>"
    THEMES=<comma-separated keywords>

Exit 0 always (no blocking — scout uses the output to set its topic).
"""

import json
import sys
from pathlib import Path

SCOREBOARD = Path("/workspace/memory/scoreboard.json")
ASTRA      = Path("/workspace/memory/astra-stars.json")


def main():
    # Allow caller to override star selection: --star N or read from active run's state.json
    override_star = None
    if "--star" in sys.argv:
        idx = sys.argv.index("--star")
        if idx + 1 < len(sys.argv):
            override_star = sys.argv[idx + 1]
    else:
        # Check if active run has a star set in state.json
        active_file = Path("/workspace/memory/pipeline/active.json")
        if active_file.exists():
            try:
                active = json.loads(active_file.read_text())
                run_id = active.get("run_id") or active.get("active_run")
                if run_id:
                    state_file = Path(f"/workspace/memory/pipeline/runs/{run_id}/state.json")
                    if state_file.exists():
                        st = json.loads(state_file.read_text())
                        if st.get("star"):
                            override_star = str(st["star"])
            except Exception:
                pass

    if not SCOREBOARD.exists():
        print("ERROR: scoreboard.json not found", file=sys.stderr)
        sys.exit(1)

    data = json.loads(SCOREBOARD.read_text(encoding="utf-8"))
    stars = data.get("stars", {})

    if not stars:
        print("ERROR: scoreboard.json has no stars", file=sys.stderr)
        sys.exit(1)

    # Sort by (count ascending, star number ascending) — lowest count wins,
    # lowest number breaks ties.
    ranked = sorted(stars.items(), key=lambda kv: (kv[1]["count"], int(kv[0])))

    if override_star and str(override_star) in stars:
        star_num  = str(override_star)
        star_data = stars[star_num]
        print(f"# Star override: using star {star_num} from state.json", file=sys.stderr)
    else:
        star_num, star_data = ranked[0]
    name  = star_data["name"]
    count = star_data["count"]

    # Load editorial angle + themes from astra-stars.json
    angle  = ""
    themes = ""
    if ASTRA.exists():
        astra = json.loads(ASTRA.read_text(encoding="utf-8"))
        entry  = astra.get(str(star_num), {})
        angle  = entry.get("angle", "")
        themes = ", ".join(entry.get("themes", []))

    print(f'STAR={star_num} NAME="{name}" COUNT={count}')
    if angle:
        print(f'ANGLE="{angle}"')
    if themes:
        print(f'THEMES={themes}')


if __name__ == "__main__":
    main()
