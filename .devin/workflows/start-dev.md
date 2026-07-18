---
description: Start AYA development environment
---

# Start AYA Development Environment

Follow these steps in order to start the full AYA development stack:

1. **Start Docker containers** (from project root)

   ```bash
   docker compose up -d
   ```

2. **Start Cloudflare tunnel** (from project root)

   ```bash
   cloudflared tunnel run aya-webhook
   ```

3. **Start frontend dev server** (in `frontend/` directory)

   ```bash
   cd frontend
   npm run dev
   ```

4. **Start admin dev server** (in `admin/` directory)

   ```bash
   cd admin
   npm run dev
   ```

## Notes

- Steps 3 and 4 run in parallel (each in its own terminal) but make sure step 3 always running first then step 4 after about 3 seconds.
- The Cloudflare tunnel (step 2) enables webhook delivery from external services (Replicate, etc.)
- Docker containers (step 1) include backend, database, Redis, and other services
