# Skill: Illustrator

Generate a header image for a Patria article using the Grok Imagine API.

## Pipeline I/O

- **Called by**: pipeline skill (step 4)
- **Input**: read slug and title from `{run_dir}/draft-v2.md` frontmatter
- **Output**: image at `memory/media/YYYY-MM/{run_id}-header.png` + write `{run_dir}/image.json`: `{ "status": "ok", "path": "...", "size_bytes": N }`
- **Pass score**: 1.0 — `image.json` must exist with `status == "ok"` and file must be > 50 KB. Retry up to 3 times.
## API

**ALWAYS use the permanent tool. Do NOT write your own image.json or call write_file for image.json.**

```
python3 /workspace/tools/generate_image.py <run_id> "<prompt>"
```

- The tool handles everything: API call, file write, image.json, patria-site copy
- Exit 0 = success → `image.json` has `status: "ok"` → call `pipeline_complete.py illustrator image.json`
- Exit 1 = hard error → retry up to 3 times
- The tool handles missing API key internally — never skip manually

## Only generate the header image

One image per article — the `16:9` header. Skip social cards unless Bluesky/LinkedIn are active.

## Prompt construction

**BEFORE writing a prompt: read `/workspace/docs/image-style-guide.md`.**

It defines the Patria/Astra Europa visual register — analytical, diagnostic, austere. Use the thematic guidance table (by Star), the anti-pattern table, and the prompt template.

Key rules:
- Show the structural problem, not the political verdict
- No propaganda aesthetics: no triumphant crowds, no glowing EU maps, no sunrise symbolism, no flag-waving
- Lighting: overcast grey or cold blue dawn — not golden hour
- Style: documentary/editorial/architectural — not cinematic action

Template:
```
[Documentary/Editorial/Architectural] [photograph/illustration/aerial view]:
[Specific structural scene — infrastructure, institutional space, or gap].
[What it conveys structurally — not the political conclusion].
[European context marker — architecture or landscape, not flags].
[Lighting: cold blue dawn / overcast grey / institutional diffuse light].
No text. No logos. No flags as protagonists. Analytical, austere.
```

## File naming and storage

```
memory/media/YYYY-MM/YYYY-MM-DD-slug-header.png
```

The publisher will copy this to `patria-site/docs/assets/img/articles/` during the push step.
