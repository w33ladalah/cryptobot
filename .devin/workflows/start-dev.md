---
description: Start Crypto Bot development environment
---

# Start Crypto Bot Development Environment

1. **Generate the compose file for the target environment** (from project root)

   ```bash
   ./scripts/generate_compose_file.sh   # defaults to development; see docker/environments/
   ```

2. **Start the stack**

   ```bash
   ./scripts/manage_services.sh   # down -> rebuild worker -> up -d -> follow logs
   ```

   This brings up `api`, `worker`, `db`, `redis`, `adminer`, and `frontend` (see `docker/services/*.yaml`).

3. **Webapp dev server** (if iterating on the UI outside the container)

   ```bash
   cd apps/webapp
   npm run dev
   ```

## Notes

- `env_vars/.env` must exist (copy from `env_vars/.env.example`) before bringing up any service —
  `CELERY_BROKER_URL`/`CELERY_RESULT_BACKEND` have no defaults and the worker won't boot without it.
- The `worker` service does not hot-reload — see `adr/004-no-backend-container-restart.md` for
  when a restart is actually needed.
- `apps/adminer` gives DB inspection at whatever port `docker/services/adminer.yaml` maps.
