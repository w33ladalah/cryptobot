---
trigger: model_decision
description: ADR 003 — Dual-currency points system (Green + Blue)
---

# ADR 003: Dual-Currency Points System

**Status:** Accepted  
**Date:** 2024

## Context

Aya AI charges users for AI operations. Two distinct value streams exist: AI compute resources and human talent licensing.

## Decision

Implement a **dual-currency system**:

- **Green Points** — AI/compute operations (image generation, video, editing, downloads)
- **Blue Points** — Human talent model licensing (downloaded images that used paid talent models)

## Point Deduction Pattern

```python
# 1. Check balance BEFORE operation (HTTP 402 if insufficient)
await check_user_points_for_service(db, user_id, service_alias)

# 2. Deduct AFTER success
await deduct_points_for_service(db, user_id, service_alias, reference_id=str(item_id))
```

## Consequences

- Service aliases are **canonical** — defined in `ServicePointCost` records and documented in `docs/AYA_POINTS_SYSTEM.md`.
- Never invent a new service alias without adding it to `docs/AYA_POINTS_SYSTEM.md`.
- Blue point deductions for downloads are multiplied by talent count (a download using 3 talent models = 3× blue deduction).
- WebSocket notification (`/api/ws/points/{user_id}`) fires after every deduction to update the frontend balance display.
