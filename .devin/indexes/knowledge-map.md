---
trigger: model_decision
description: Index of all .devin knowledge files — use to find the right file quickly
---

# Knowledge Map

Quick reference to find the right knowledge file.

## Always-On Rules (loaded every context)

| File | Content |
|------|---------|
| `rules/always-on/core-principles.md` | Project overview, monorepo, current focus, non-negotiables |
| `rules/always-on/safety.md` | Money/trading safety, Docker, secrets, DB safety constraints |
| `rules/always-on/architecture-invariants.md` | API/worker/webapp structural contracts |
| `rules/always-on/self-review.md` | Pre-commit checklist |
| `rules/always-on/auto-review.md` | When to run the `/review` workflow |

## Backend Rules (loaded for apps/api/**, apps/worker/**)

| File | Content |
|------|---------|
| `rules/backend/conventions.md` | API models/repos/routes, worker tasks/config/LLM adapters/trading |

## Worker Rules (loaded for apps/worker/**)

| File | Content |
|------|---------|
| `rules/worker/known-bugs.md` | Confirmed bugs blocking the Ethereum execution path |

## Frontend Rules (loaded for apps/webapp/**)

| File | Content |
|------|---------|
| `rules/frontend/conventions.md` | Current (minimal) webapp state, tech stack, when to propose structure |

## Infra Rules

| File | Content |
|------|---------|
| `rules/infra/docker-commands.md` | Allowed/forbidden Docker commands, api vs worker reload behavior |
| `rules/infra/migrations.md` | Alembic migration steps and checklist |

## Security Rules

| File | Content |
|------|---------|
| `rules/security/env-secrets.md` | .env locations, sensitive keys, never commit secrets |

## Architecture

| File | Content |
|------|---------|
| `architecture/overview.md` | System diagram, data flows, domain models, multi-chain design plan |

## ADRs (Architecture Decision Records)

| File | Decision |
|------|---------|
| `adr/004-no-backend-container-restart.md` | API hot-reloads, worker doesn't — restart accordingly |

## Workflows (Manual Multi-Step Processes)

| File | When to Use |
|------|------------|
| `workflows/add-new-feature.md` | Feature touching api/worker/webapp |
| `workflows/add-api-endpoint.md` | New API endpoint only |
| `workflows/database-migration.md` | Alembic migration |
| `workflows/fix-backend-bug.md` | API/worker debugging workflow |
| `workflows/improve-existing-feature.md` | Refactor/enhance existing feature |
| `workflows/should-write-tests.md` | Decide if tests are needed |
| `workflows/should-save-knowledge.md` | Decide knowledge type to save |
| `workflows/save-as-memory.md` | When and how to save memories |
| `workflows/git-commit-all.md` | Commit all changes |
| `workflows/review.md` | Code review workflow |
| `workflows/save-as-rule.md` | Save knowledge as a rule |
| `workflows/save-as-skill.md` | Save knowledge as a skill |
| `workflows/save-as-workflow.md` | Save knowledge as a workflow |
| `workflows/should-document.md` | Decide if documentation is needed |
| `workflows/update-docs.md` | Update project documentation |
| `workflows/start-dev.md` | Start the dev environment |
| `workflows/start-aws-ec2-session.md` | Start an AWS EC2 session |
| `workflows/enhance.md` | General enhancement workflow |

## Skills (Auto-Invoked Code Generation)

| File | When Used |
|------|----------|
| `skills/scaffold-backend-entity/` | Scaffold model + schema + repository + route in `apps/api` |
| `skills/add-celery-task/` | Scaffold a new Celery task in `apps/worker` |
