# Skill: Publisher — Post

Publish the finished article to the website (GitHub Pages). That is the only job of this step.

## Pipeline I/O

- **Called by**: pipeline (step: publisher:post)
- **Input**: `{run_dir}/draft-v2.md` + `{run_dir}/image-staged.json`
- **Output**: `{run_dir}/published.json` written by the tool — `{ "status": "ok", "url": "..." }`
- **Pass score**: 1.0 — git push must succeed and `url` must be set

## Prerequisites

**Check image.json status first.**

Read `{run_dir}/image.json`. Three cases:
- `status == "ok"` — image ready, proceed normally.
- `status == "skipped"` — no image. Continue publishing but the tool removes the `image:` frontmatter line.
- File missing or `status == "failed"` — treat as `"skipped"`, continue.

---

## 1. Website (GitHub Pages)

Use the permanent tool — do NOT write your own git/Python code:

```
python3 /workspace/tools/publish_post.py <run_id>
```

- Handles git clone/pull, article copy, image copy, frontmatter strip (if no image), commit, push
- Exit 0 = pushed. Writes `published.json` with `status: "ok"` and `url`
- Exit 1 = hard error — tool writes `published.json` with `status: "FAILED"` and the reason
- **NEVER write published.json yourself** — the tool always writes it

---

## After publishing

Run the star history tool:

```
python3 /workspace/tools/update_star_history.py {run_id}
```

This appends the article title, angle, and URL to `memory/stars/{star}/published.md` so future runs on this star know what angles have already been covered.

Report: `Publisher Post done — article live at {url}`

Do not start publisher:bluesky. Do not update memory files.
