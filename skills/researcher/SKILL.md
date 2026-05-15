# Skill: Researcher — Run 1 (Primary Sources)

Fetch and extract evidence from the primary sources selected by the Curator. Answer the key questions. Write everything to disk after each fetch.

## CRITICAL: curated-sources.md is pre-loaded — do NOT call read_file

The content of `curated-sources.md` is **already provided above** in the `## PRE-LOADED` section of this prompt.

**DO NOT call `read_file` for `curated-sources.md` or any other file. The data is already here. Start directly at Step 1 (web_fetch).**

## Pipeline I/O

- **Called by**: pipeline skill (step: researcher-1)
- **Input**: `{run_dir}/curated-sources.md` (PRE-LOADED ABOVE)
- **Output**: `{run_dir}/research-report.md` (with `## RUN-1-COMPLETE` marker)
- **Pass score**: ≥ 0.6 (min 2 primary sources fetched with real quotes, min 2 key questions answered)

## Steps

1. From the PRE-LOADED `curated-sources.md` above, identify the Star, angle, key questions, and Primary source URLs.
2. Write the report header to `{run_dir}/research-report.md` (use `write_file`).
3. Fetch Primary URL 1 with `web_fetch`, immediately append findings to research-report.md with `edit_file`.
4. Fetch Primary URL 2 with `web_fetch`, immediately append findings to research-report.md with `edit_file`.
5. Fetch Primary URL 3 with `web_fetch`, immediately append findings to research-report.md with `edit_file`.
6. Fetch Primary URL 4 with `web_fetch` (if available), immediately append findings with `edit_file`.
7. Append `## RUN-1-COMPLETE` to research-report.md.
8. Call: `python3 /workspace/tools/pipeline_complete.py researcher-1 {run_dir}/research-report.md`

**Never call read_file. All input data is pre-loaded above. Go directly to step 2.**

## Goal

Answer the key questions from `curated-sources.md` using the primary sources. Extract real quotes, statistics, and named facts. Write after every single fetch — never buffer multiple sources in memory.

## Tools

- `web_fetch` — fetch each primary source URL (max 4 fetches this run)
- `write_file` / `edit_file` — write research-report.md (append after each fetch)

## Critical rule

**Write to disk after every fetch.** Do not fetch source 2 before writing source 1's findings.

## Report format

Write the report header immediately to `{run_dir}/research-report.md`:
```
# Research Report — {run_id}

**Star**: {n} — {name}
**Angle**: {angle from curated-sources.md}

## Key questions
{copy key questions from curated-sources.md}

## Evidence
```

### For each source

```
### Source: {URL}
**Date**: {publication date}
**Tier**: {1 = EU institution / 2 = quality press/think tank / 3 = other}

**Answers question(s)**: {list which key questions}

**Key facts**:
- {fact or quote — verbatim if quote, with attribution}
- {fact or quote}
- {fact or quote}
```

4. Move to the next URL. The fetched page content is now released from memory.

If a URL fails to load: note `(fetch failed — URL unreachable)` and move to the next.

### Step 3 — Write RUN-1-COMPLETE

After all primary sources are processed (or after 4 fetches), append to `research-report.md`:

```
## RUN-1-COMPLETE
Key questions answered: {list which ones have evidence, which are still open}
Remaining for Run 2: institutional context, historical precedent, gaps and caveats
```

### Step 4 — Stop

Report: `Researcher Run 1 done — {x} sources fetched, {y} key questions answered. Run 2 needed for institutional and historical depth.`

Do not start Run 2. Do not start the writer.
