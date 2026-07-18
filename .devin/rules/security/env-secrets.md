---
trigger: model_decision
description: Environment variable and secrets management rules
---

# Secrets & Environment Management

## Environment File Locations

| File | Purpose |
|------|---------|
| `env_vars/.env` | Real values — **gitignored, must never be committed**. Does not exist yet as of 2026-07-17. |
| `env_vars/.env.example` | Template with all required keys, no real values. Tracked in git. |
| `apps/worker/.env.example` | Worker-specific template (may overlap with the root one). |

`docker/services/*.yaml` maps these env vars into each container's environment — when adding a
new var, update `.env.example`, the relevant `docker/services/*.yaml`, and the consuming
`Config` class together.

## Rules

- **Never commit `env_vars/.env`** — gitignored by design.
- **Never hardcode secrets** in source code (private keys, API keys, tokens, passwords).
- **Never log or print** `WALLET_PRIVATE_KEY`, `WEB3_WALLET_PRIVATE_KEY`, `LLM_API_KEY`,
  `DISCORD_BOT_TOKEN`, or DB credentials — even at DEBUG level.
- Access config only through the `Config` classes (`apps/worker/config/settings.py`, and the
  equivalent in `apps/api`) — never scattered `os.getenv()` calls.

## Sensitive Keys (currently in `.env.example`)

`API_ENCRYPTION_SECRET_KEY`, `MYSQL_PASSWORD`, `MYSQL_ROOT_PASSWORD`, `DISCORD_BOT_TOKEN`,
`WALLET_PRIVATE_KEY`, `WALLET_ADDRESS`, `OPENROUTER_API_KEY`, `LLM_API_KEY`, `REDIS_PASSWORD`,
`WEB3_WALLET_PRIVATE_KEY`, `WEB3_WALLET_ADDRESS`.

## Config Pattern

```python
# worker
from apps.worker.config.settings import Config
config = Config()
config.WALLET_PRIVATE_KEY  # SecretStr — never str(config.WALLET_PRIVATE_KEY) into logs
```

`pydantic-settings` loads values from the environment via `load_dotenv()` — sensitive fields use
`SecretStr` so they don't accidentally render in reprs/logs. Preserve that typing when adding new
secret fields (don't downgrade `SecretStr` to `str`).
