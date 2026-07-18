---
trigger: glob
globs: backend/**
description: Docker commands and constraints for backend development
---

# Docker Commands

## Allowed Commands

```bash
# Run backend commands (ALWAYS inside Docker)
docker compose exec backend <command>

# Check logs
docker compose logs backend --tail 100
docker compose logs celery-worker --tail 100

# Start services (if not running)
docker compose -f docker-compose.local.yaml up -d backend db redis

# Run migrations
docker compose exec backend alembic revision --autogenerate -m "description"
docker compose exec backend alembic upgrade head
docker compose exec backend alembic current
docker compose exec backend alembic downgrade -1

# Run tests
docker compose exec backend pytest backend/tests/ -v
docker compose exec backend pytest backend/tests/test_<module>.py -v
```

## Forbidden Commands

NEVER run these without explicit user instruction:

```bash
docker compose restart backend        # disrupts uvicorn --reload
docker compose up --build backend     # rebuilds container unnecessarily
docker compose down                   # takes down all services
docker compose stop backend           # stops uvicorn
```

## Why Never Restart

Backend uses `uvicorn --reload`. All code changes are detected automatically. Restarting:
- Disrupts active WebSocket connections
- Interrupts in-progress AI predictions
- Is unnecessary for 99% of changes

## When Restart IS Needed

- New `pip` dependency added to `requirements.txt` → ask user to rebuild manually
- Environment variable changes → ask user to restart manually
- Never do it automatically

## Frontend / Admin (Host, Not Docker)

```bash
# From /Users/hendrowibowo/Projects/aya-ai/frontend
npm run dev

# From /Users/hendrowibowo/Projects/aya-ai/admin
npm run dev
```
