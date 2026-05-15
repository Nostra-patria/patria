# Heartbeat Tasks

This file is checked every 60 minutes by the Patria agent.

## Role: start new runs only

**Heartbeat does NOT execute pipeline steps.** Steps are dispatched by the cron job (every 3 minutes).

Read `memory/pipeline/active.json`:

- **If a run is active** (run_id is set): do nothing. The cron dispatcher handles it. Return `skip`.
- **If no active run**: start a new run. Use skill: pipeline to pick a topic (scout step only), create `memory/pipeline/runs/{run-id}/state.json`, set `active.json`, then stop. ONE step only.

Do not continue past scout. Do not run researcher, writer, or any later step. The cron dispatcher takes over after scout.

## Active Tasks

<!-- Add manual overrides below this line. Remove when done. -->

## Completed

<!-- Move completed tasks here or delete them -->
