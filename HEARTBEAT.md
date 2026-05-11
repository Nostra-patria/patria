# Heartbeat Tasks

This file is checked every 60 minutes by the Patria agent.
If no explicit tasks are listed, run the default editorial pipeline.

## Default (always runs when no active tasks)

- Run scout: monitor EU news, geopolitics, Astra Europa, Volt, Ave Europa
- Identify 1–3 topics worth writing about
- Research the strongest topic (minimum 2 Tier-1/2 sources)
- Draft article (600–1200w), tagged to a Star
- Derive 3–5 social posts
- Generate header image + social card
- Publish: website, Bluesky, LinkedIn
- Update memory/LIBRARY.md

## Active Tasks

<!-- Add priority tasks or manual triggers below this line -->
**FULL RUN — website + images**
Run the full pipeline: scout → research → write → illustrate → publish.
Generate 1 header image per article using the Grok Imagine API (skill: illustrator).
Publish article + image to GitHub Pages (docs/_posts/ and docs/assets/img/articles/).
Skip Bluesky and LinkedIn for now.

## Completed

<!-- Move completed tasks here or delete them -->
