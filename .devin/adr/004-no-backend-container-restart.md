---
trigger: model_decision
description: ADR 004 — API container hot-reloads, worker container does not
---

# ADR 004: API Hot-Reloads, Worker Does Not — Restart Accordingly

**Status:** Accepted
**Date:** 2026-07-18

## Context

The `api` container runs `fastapi dev main.py`, which hot-reloads on file changes. The `worker`
container runs `celery -A main worker --loglevel=info`, with **no** `--reload` equivalent —
Celery does not pick up changed task code in a running worker process.

## Decision

- **Never restart the `api` container** for a plain code change — `fastapi dev` handles it.
- **Do expect to restart the `worker` container** after changing anything under `apps/worker/`
  (tasks, config, trading logic, LLM adapters) for the change to actually run.

## Why

1. `fastapi dev` watches files and reloads automatically — restarting the `api` container is
   redundant and, if it has active WebSocket/long-running connections in the future, disruptive.
2. Celery workers load task code once at process start. A code change without a worker restart
   silently keeps running the **old** code — this is a common source of "I fixed the bug but it's
   still happening" confusion in this project.

## Practical Guidance

- After editing `apps/api/**`: no action needed, just wait for the reload.
- After editing `apps/worker/**`: restart the `worker` container, or re-run
  `scripts/manage_services.sh` (which rebuilds + restarts it) — confirm with the user before
  running either automatically mid-task, per `rules/always-on/safety.md`.

## Forbidden Without Explicit Instruction

- `docker compose down`
- `docker compose up --build` (full rebuild of all services)
