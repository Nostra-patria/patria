# Skill: Writer

Write a long-form Patria article from a research object.

## Format

```markdown
---
layout: article
title: "Factual, opinionated headline (max 90 chars)"
date: YYYY-MM-DD
star: 5
star_label: "Energy Sovereignty"
slug: europe-lng-dependency-new-trap
summary: "One sentence. The argument in plain language."
image: /patria/assets/img/articles/YYYY-MM-DD-slug-header.png
---

# [Title]

**[Hook — one or two sentences. The argument stated boldly. No hedging.]**

## [Section 1 — The situation]

[2–3 paragraphs: what is happening. Concrete, sourced. Cite inline with markdown links.]

## [Section 2 — Why it matters for Europe]

[2–3 paragraphs: the European angle. Connect to sovereignty, institutions, strategic interests.
This is where the Patria voice is strongest.]

## [Section 3 — The argument / analysis]

[2–3 paragraphs: what Patria thinks. Clearly labelled as analysis.
Use "The data suggests..." not "Everyone knows..."]

## [Section 4 — What should happen (optional)]

[1–2 paragraphs: what a federal, sovereign Europe would do differently.
Forward-looking. Grounded in the research.]

## Sources

- [Source Title](URL) — Tier 1/2/3
- [Source Title](URL) — Tier 1/2/3
```

## Length

600–1200 words. No padding. Every sentence earns its place.

## Voice rules

- English — always
- Short sentences. Active voice.
- "The Commission's data shows..." not "It is widely believed..."
- Label opinions: "Patria's view:" or "This is, at minimum, worth debating."
- Never condescending. Never sloganeering.
- The hook must earn the reader's attention in two sentences.

## File naming

Jekyll requires this exact format for `_posts/`:
```
YYYY-MM-DD-slug.md
```

## Storage

Write to `memory/drafts/YYYY-MM-DD-slug.md` first.
After publish, the publisher copies it to `patria-site/_posts/`.

## Library update

After the article is finalised, add an entry to `memory/LIBRARY.md`:

```
| YYYY-MM-DD | [Title](URL) | Star N — Label | slug |
```

## Quality check

- [ ] Hook states the argument, not the topic
- [ ] All factual claims have inline source links
- [ ] European angle section is present
- [ ] No fabricated quotes or statistics
- [ ] Star tag matches content
- [ ] Slug is URL-safe (lowercase, hyphens only)
