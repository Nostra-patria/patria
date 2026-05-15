# Skill: Writer — Merge

Merge all draft parts into the final draft-v1.md using the pipeline_merge tool.

## Pipeline I/O

- **Called by**: pipeline skill (step: writer-merge)
- **Input**: `{run_dir}/draft-v1-lead.md` + `{run_dir}/draft-v1-body.md` + `{run_dir}/draft-v1-close.md` + `{run_dir}/curated-sources.md`
- **Output**: `{run_dir}/draft-v1.md` (merged complete article)
- **Pass score**: ≥ 0.7 (sources block present + total word count 700–1100)
- **Trigger**: `draft-v1-close.md` exists

## Goal

Merge the three draft parts and sources into one complete article file using the deterministic merge tool. Do NOT rewrite, summarise, or paraphrase any content. The tool does the merging — your job is to run it and check the output.

## Tools

- `exec` — run the merge tool
- `read_file` — verify the output after merging

## Process

### Step 1 — Run the merge tool

```bash
python3 /workspace/tools/pipeline_merge.py {run_dir}
```

Example:
```bash
python3 /workspace/tools/pipeline_merge.py memory/pipeline/runs/2026-05-12-federalist-surge-v3
```

The tool concatenates lead + body + close + sources block and writes `draft-v1.md`. It prints the word count.

### Step 2 — Check the output

Read `{run_dir}/draft-v1.md` and verify:
- It starts with `---` (YAML frontmatter from lead)
- It contains body sections (H2 headings)
- It ends with a `## Sources` section
- Word count is in the 700–1100 range (printed by the tool)

If the word count is below 700, the tool will print a WARNING. In that case, identify the thinnest body section in `draft-v1-body.md` and append one additional paragraph to `draft-v1-body.md` with a specific fact from the research. Then re-run the merge tool.

### Step 3 — Stop

Report: `Writer Merge done — draft-v1.md, {word count} words, {source count} sources.`

Do not start verifier. Do not edit the article content.
