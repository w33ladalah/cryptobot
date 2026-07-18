---
description: Workflow for improving or enhancing an existing feature
---

# Improve Existing Feature

Use this when enhancing, refactoring, or optimizing an existing feature in `apps/api`,
`apps/worker`, or `apps/webapp`.

## Phase 1 — Analysis

1. **Understand current implementation:** read the existing code, identify files involved
   (models, repositories, routes, tasks, trading logic), check `rules/worker/known-bugs.md` if
   the area is `apps/worker/core/trading/` or `apps/worker/tasks/analyzer.py`.
2. **Identify improvement areas:** performance, code quality, missing risk controls (for trading
   logic), security, missing error handling.
3. **Plan the changes:** scope (api / worker / webapp), impact on existing functionality, testing
   approach.

## Phase 2 — Implementation

1. **API changes (if applicable):** update models/schema/repository/route per
   `rules/backend/conventions.md`; generate migration if models changed.
2. **Worker changes (if applicable):** update tasks/config/LLM adapters/trading logic; remember
   the worker container needs a restart to pick up code changes (no hot-reload).
3. **Webapp changes (if applicable):** currently minimal scaffold — confirm any assumed pattern
   actually exists before using it.

## Phase 3 — Testing

- Manual testing of the improved feature; regression check on existing behavior; edge cases.
- If it touches trade execution, verify DRY_RUN/Sepolia behavior explicitly.

## Phase 4 — Commit

- Descriptive commit message, e.g. `feat(worker): improve <feature>` or `refactor(api): optimize <component>`.

## Checklist

- [ ] Current implementation understood
- [ ] Changes planned and scoped to the right service(s)
- [ ] Migration applied (if model changed)
- [ ] Changes tested manually, including regressions
- [ ] Worker restarted if `apps/worker/**` changed
- [ ] Changes committed with descriptive message

## Important Notes

- **Experimental project:** prefer minimal, focused changes; ask before broad refactors.
- **API hot-reloads, worker does not** — see `adr/004-no-backend-container-restart.md`.
- **Never enable mainnet trading** without explicit instruction.
