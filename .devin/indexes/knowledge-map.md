---
trigger: model_decision
description: Index of all .windsurf knowledge files — use to find the right file quickly
---

# Knowledge Map

Quick reference to find the right knowledge file.

## Always-On Rules (loaded every context)

| File | Content |
|------|---------|
| `rules/always-on/core-principles.md` | Project overview, monorepo, live URLs, non-negotiables |
| `rules/always-on/safety.md` | Docker safety, secrets, DB safety constraints |
| `rules/always-on/architecture-invariants.md` | Model/CRUD/router/points/download system contracts |
| `rules/always-on/self-review.md` | Pre-commit checklist for Cascade |

## Backend Rules (loaded for backend/**)

| File | Content |
|------|---------|
| `rules/backend/conventions.md` | Models, CRUD, schemas, routers, auth deps, Celery, timezone |
| `rules/backend/known-bugs.md` | belongs_to_user bug, Replicate wait(), TalkingVideoStatus, circular imports |
| `rules/backend/points-system.md` | Service aliases, deduction pattern, reference to docs/AYA_POINTS_SYSTEM.md |

## Frontend Rules (loaded for frontend/**)

| File | Content |
|------|---------|
| `rules/frontend/conventions.md` | Next.js 15, Redux, Axios, TailwindCSS, auth modal, video blobs |
| `rules/frontend/admin-conventions.md` | Next.js 16, Lucide, fetch(), differences from frontend |

## Infra Rules (loaded for backend/**)

| File | Content |
|------|---------|
| `rules/infra/docker-commands.md` | Allowed/forbidden Docker commands, why never restart |
| `rules/infra/migrations.md` | Alembic migration steps and checklist |

## Security Rules

| File | Content |
|------|---------|
| `rules/security/imgproxy-s3.md` | Never expose S3/Replicate URLs, correct imgproxy usage |
| `rules/security/env-secrets.md` | .env locations, never commit secrets, NEXT_PUBLIC_ rules |

## Architecture

| File | Content |
|------|---------|
| `architecture/overview.md` | System diagram, data flows, domain models, WebSocket endpoints |

## ADRs (Architecture Decision Records)

| File | Decision |
|------|---------|
| `adr/001-single-download-history-table.md` | All downloads in one table with media_type |
| `adr/002-imgproxy-only-for-s3.md` | Never pass Replicate URLs to imgproxy |
| `adr/003-dual-currency-points.md` | Green + Blue points system |
| `adr/004-no-backend-container-restart.md` | uvicorn --reload, never restart backend |

## Examples (Reference Implementations)

| File | Content |
|------|---------|
| `examples/backend-download-endpoint.md` | Full download endpoint with license + points + history |
| `examples/backend-s3-async-upload.md` | Async S3 upload pattern using httpx + asyncio.to_thread |
| `examples/frontend-redux-slice.md` | Complete Redux slice + thunk + store registration |
| `examples/admin-crud-service.md` | Admin service + list page with Lucide + native fetch |

## Workflows (Manual Multi-Step Processes)

| File | When to Use |
|------|------------|
| `workflows/add-new-feature.md` | Full-stack feature from scratch |
| `workflows/add-api-endpoint.md` | Backend API endpoint only |
| `workflows/add-frontend-page.md` | Frontend page with Redux |
| `workflows/add-redux-slice.md` | Redux slice + thunk only |
| `workflows/database-migration.md` | Alembic migration |
| `workflows/fix-backend-bug.md` | Backend debugging workflow |
| `workflows/fix-frontend-bug.md` | Frontend debugging workflow |
| `workflows/improve-existing-feature.md` | Refactor/enhance existing feature |
| `workflows/should-write-tests.md` | Decide if tests are needed |
| `workflows/should-save-knowledge.md` | Decide knowledge type to save |
| `workflows/save-as-memory.md` | When and how to save memories |
| `workflows/git-commit-all.md` | Commit all changes |
| `workflows/download-functionality.md` | Download system reference |
| `workflows/review.md` | Code review workflow |
| `workflows/add-admin-page.md` | Admin page creation |
| `workflows/fix-admin-bug.md` | Admin debugging workflow |
| `workflows/image-generation-reference-rule.md` | Image generation system reference |
| `workflows/save-as-rule.md` | Save knowledge as a Windsurf rule |
| `workflows/save-as-skill.md` | Save knowledge as a Windsurf skill |
| `workflows/save-as-workflow.md` | Save knowledge as a Windsurf workflow |
| `workflows/should-document.md` | Decide if documentation is needed |
| `workflows/update-docs.md` | Update project documentation |

## Skills (Auto-Invoked Code Generation)

| File | When Used |
|------|----------|
| `skills/scaffold-backend-entity/` | Scaffold model + schema + CRUD + router |
| `skills/scaffold-admin-crud/` | Scaffold admin service + list + edit pages |

## Contextual AGENTS.md Files

| File | Scope |
|------|-------|
| `backend/AGENTS.md` | Backend-specific context for AI agents |
| `frontend/AGENTS.md` | Frontend-specific context for AI agents |
| `admin/AGENTS.md` | Admin-specific context for AI agents |
