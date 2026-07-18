---
trigger: model_decision
description: ADR 004 — Backend container must never be restarted for code changes
---

# ADR 004: No Backend Container Restart for Code Changes

**Status:** Accepted  
**Date:** 2024

## Context

The backend runs with `uvicorn --reload` which watches for file changes and hot-reloads automatically. Early in development, team members were restarting the Docker container for code changes.

## Decision

**Never restart the backend Docker container** for code changes. uvicorn `--reload` handles all Python file changes automatically.

## Why

1. **Active connections**: Restarting drops all WebSocket connections — this interrupts users receiving real-time generation progress.
2. **In-progress tasks**: Active Celery tasks and Replicate API calls continue running; the container restart causes state loss.
3. **Unnecessary**: `uvicorn --reload` detects file changes within seconds.

## When Container Restart IS Needed

1. New `pip` dependency added (requires container rebuild)
2. Environment variable changes (requires container restart)
3. `main.py` startup code changes (lifespan events)

In all these cases: **ask the user to do it manually** — never trigger automatically.

## Forbidden Commands

- `docker compose restart backend`
- `docker compose up --build backend`
- `docker compose stop backend && docker compose start backend`
