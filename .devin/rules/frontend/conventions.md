---
trigger: glob
globs: apps/webapp/**
description: Conventions for the webapp dashboard
---

# Webapp Conventions

## Current State (2026-07-17)

`apps/webapp` is a **minimal Vite + React 19 + TypeScript scaffold** — essentially the default
`npm create vite` output (`App.tsx`, `main.tsx`, `App.css`, `index.css`). There is no Redux, no
router, no API client, and no design system wired up yet. Check `apps/webapp/package.json`
before assuming any library is available — don't reference patterns from other projects
(Redux slices, Axios interceptors, etc.) as if they already exist here.

## Tech Stack (confirmed in `package.json`)

- React 19 + React DOM 19
- Vite 6 (dev server, build via `tsc -b && vite build`)
- TypeScript 5.7
- ESLint 9 (`npm run lint`)

## Dev Server

```bash
cd apps/webapp
npm run dev       # Vite dev server
```

README states the dashboard is served at `http://localhost:1421` — confirm the actual port in
`apps/webapp/vite.config.ts` / `docker/services/frontend.yaml` before relying on it, since the
default Vite port (5173) differs.

## When Adding Structure

If asked to add API calls, state management, or routing to the webapp, treat it as new work —
propose an approach and confirm with the user rather than assuming an established convention
exists. Once a pattern is chosen and used more than once, it should be documented back into this
file (see `workflows/save-as-rule.md`).
