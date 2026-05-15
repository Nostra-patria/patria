# Skill: Researcher — Run 2 (Secondary Sources + Depth)

Fetch secondary sources and add institutional context, historical precedent, member state positions, and gaps. Append to the existing research report.

## CRITICAL: Files are pre-loaded — do NOT call read_file

The content of `curated-sources.md` and `research-report.md` is **already provided above** in the `## PRE-LOADED` sections of this prompt.

**DO NOT call `read_file` for any file. The data is already here. Start directly at Step 1 (web_fetch).**

## Steps

1. From the PRE-LOADED `curated-sources.md` above, identify the **Secondary sources** URLs.
2. From the PRE-LOADED `research-report.md` above, note what Run 1 covered (to avoid duplication).
3. Fetch Secondary URL 1 with `web_fetch`, immediately append findings to research-report.md with `edit_file`.
4. Fetch Secondary URL 2 with `web_fetch`, immediately append findings to research-report.md with `edit_file`.
5. Fetch Secondary URL 3 with `web_fetch` (if available), immediately append findings with `edit_file`.
6. Append depth sections (Institutional context, Member state positions, Historical precedent) to research-report.md.
7. Append `## RUN-2-COMPLETE` to research-report.md.
8. Call: `python3 /workspace/tools/pipeline_complete.py researcher-2 {run_dir}/research-report.md`

**Never call read_file. All input data is pre-loaded. Go directly to web_fetch.**

## Process

### Step 1 — Read context (TWO reads total, then STOP reading)

Read `{run_dir}/research-report.md` — understand what Run 1 already covered. Note which key questions are still open.

Read `{run_dir}/curated-sources.md` — note the Secondary sources list (these are your targets).

**You have now read all the files you need. Do not call read_file again. Proceed immediately to Step 2.**

### Step 2 — Fetch secondary sources (one at a time, max 3)

**Before fetching**: Check each URL. If a URL has no path beyond a bare domain root (e.g. `https://volteuropa.org/` or `https://federalists.eu/`), do NOT fetch the homepage. Instead, use `web_search` to find a specific article or publication from that organisation relevant to the article angle. Use the search query: `site:{domain} {angle keyword}`. Take the first result URL with a real path and fetch that instead. If no specific article is found via search, then skip and note it. Never read `curated-sources.md` more than once.

For each URL in the Secondary sources list (max 3 fetches):

1. `web_fetch` the URL
2. Extract specifically:
   - Institutional context: which EU body, treaty article, committee, or official is central?
   - Member state positions: who supports, who opposes, what are the fault lines?
   - Historical context: what precedent exists, what was tried before, what failed?
   - Gaps and caveats: what is contested, uncertain, or missing from the evidence?
3. Immediately append to `research-report.md`:

```
### Source: {URL}
**Date**: {publication date}
**Tier**: {1/2/3}

**Section**: {Institutional context | Member state positions | Historical context | Gaps}

**Key facts**:
- {fact, quote, or named position — verbatim quotes with attribution}
- {fact}
```

4. Release the page from memory. Move to next URL.

### Step 3 — Write depth sections

After all secondary fetches, append the following sections to `research-report.md`. Write each section from the extracted facts — do not repeat what Run 1 already wrote:

```
## Institutional context
{Which EU institutions are involved. Treaty articles. Named officials. Committee decisions. Legislative stage.}

## Member state positions
{Who is aligned, who is resistant, what the fault lines are. Name specific countries and their stated positions where possible.}

## Historical context
{What precedent exists. What has been tried before. What failed and why. How long this issue has been on the EU agenda.}

## Gaps and caveats
{What could not be verified. Conflicting sources. Data that is missing or contested. Uncertainty the writer must acknowledge.}

## Sources table
| URL | Date | Tier | Used for |
|-----|------|------|----------|
| {all URLs from Run 1 and Run 2} | ... | ... | ... |
```

### Step 4 — Write RUN-2-COMPLETE

Append to `research-report.md`:

```
## RUN-2-COMPLETE
Research is complete. Writer may proceed.
```

### Step 5 — Stop

Report: `Researcher Run 2 done — institutional context, historical arc, {x} total sources across both runs. Research complete.`

Do not start the writer.
