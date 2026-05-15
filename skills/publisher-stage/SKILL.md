# Skill: Publisher — Stage

Confirm the header image is in place and write image-staged.json. **Do NOT generate an image** — that was done by the illustrator step.

## Pipeline I/O

- **Called by**: pipeline (step: publisher:stage)
- **Input**: `{run_dir}/image.json` (written by illustrator)
- **Output**: `{run_dir}/image-staged.json`
- **Pass score**: 1.0 — image file must exist at path and be > 50 KB

## Tools

- `exec` — check file existence, copy if needed
- `write_file` — write image-staged.json

## Process

### Step 1 — Read image.json

```
exec: cat {run_dir}/image.json
```

Three cases:
- `status == "ok"` — image exists, proceed to Step 2
- `status == "skipped"` — no API key was available. Write image-staged.json and complete:
  ```json
  { "status": "PENDING_API_KEY", "path": null, "reason": "illustrator skipped — no API key" }
  ```
  Then call `python3 /workspace/tools/pipeline_complete.py publisher:stage {run_dir}/image-staged.json` and exit.
- File missing — treat as skipped.

### Step 2 — Verify image file

The image was already copied to `patria-site` by `generate_image.py`. Verify it exists:

```
exec: ls /workspace/patria-site/docs/assets/img/articles/{run_id}-header.png
```

If the file is missing, copy it from `memory/media`:
```
exec: cp /workspace/memory/media/YYYY-MM/{run_id}-header.png /workspace/patria-site/docs/assets/img/articles/{run_id}-header.png
```
(replace YYYY-MM with the year-month from the run_id date, e.g. `2026-05`)

### Step 3 — Write image-staged.json

```json
{
  "status": "ok",
  "path": "/workspace/patria-site/docs/assets/img/articles/{run_id}-header.png"
}
```

Write with `write_file` to `{run_dir}/image-staged.json`.

### Step 4 — Complete

```
python3 /workspace/tools/pipeline_complete.py publisher:stage {run_dir}/image-staged.json
```
