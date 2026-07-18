---
trigger: glob
globs: apps/api/**,apps/worker/**,docker/**
description: Docker commands and constraints for api/worker development
---

# Docker Commands

## Compose File Generation

Compose files are environment-specific and **generated**, not hand-written:

```bash
./scripts/generate_compose_file.sh   # reads docker/environments/{development,staging,production}.yaml
                                      # + docker/services/*.yaml, writes docker/run-<env>-compose.yaml
./scripts/manage_services.sh         # down + rebuild worker image + up -d + follow logs
```

Don't hand-edit a generated `docker/run-*-compose.yaml` — edit the source files under
`docker/environments/` or `docker/services/` and regenerate.

## Allowed Commands

```bash
# Run commands inside the container, never on host
docker compose -f docker/run-development-compose.yaml exec api <command>
docker compose -f docker/run-development-compose.yaml exec worker <command>

# Logs
docker compose -f docker/run-development-compose.yaml logs api --tail 100
docker compose -f docker/run-development-compose.yaml logs worker --tail 100

# Migrations (inside the api container)
docker compose -f docker/run-development-compose.yaml exec api alembic revision --autogenerate -m "description"
docker compose -f docker/run-development-compose.yaml exec api alembic upgrade head
```

## API vs Worker Reload Behavior — Important Difference

- **`api`** runs `fastapi dev main.py` (see `docker/services/api.yaml`) — this hot-reloads on file
  changes. Never restart the `api` container for a plain code change.
- **`worker`** runs `celery -A main worker --loglevel=info --logfile=logs/workers.log` — Celery
  workers do **not** hot-reload task code by default. After changing anything under
  `apps/worker/`, the worker container typically **does** need a restart for the change to take
  effect. `scripts/manage_services.sh` already rebuilds the worker image and restarts it on every
  run — if you're iterating manually instead, ask the user before restarting.

## Forbidden Without Explicit Instruction

```bash
docker compose down                  # takes down all services
docker rmi -f cryptobot-development-worker
docker compose up --build            # full rebuild
```

`scripts/manage_services.sh` runs both of the first two on every invocation — treat running that
script as equivalent to an explicit restart request, don't run it casually as a side effect of
an unrelated task.
