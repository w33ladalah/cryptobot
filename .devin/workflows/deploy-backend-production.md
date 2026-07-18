---
description: Deploy backend to production EC2 (APP instance via AWS SSM)
---

# Deploy Backend to Production

## Prerequisites

- AWS CLI installed and configured (`aws configure` or `aws login`)
- Session Manager plugin installed (`brew install session-manager-plugin`)
- All changes committed and pushed to GitHub

## Versioning

Uses **semantic versioning**: `vMAJOR.MINOR.PATCH`

- `PATCH` — bug fixes / hotfixes (e.g. `v1.0.0 → v1.0.1`)
- `MINOR` — new features, backward-compatible (e.g. `v1.0.0 → v1.1.0`)
- `MAJOR` — breaking changes (e.g. `v1.0.0 → v2.0.0`)

Check the latest tag to decide the next version:

```bash
git tag --list --sort=-version:refname | head -5
```

## Steps

### 1. Commit all changes and merge to main

If on a **feature branch** (not `develop` or `main`):

```bash
git add -A
git commit -m "your descriptive commit message"
git checkout develop
git merge <your-branch>
```

Then merge `develop` → `main`:

```bash
git checkout main
git merge develop
git push origin main
git checkout develop
git push origin develop
```

If already on **`develop`**:

```bash
git add -A
git commit -m "your descriptive commit message"
git push origin develop
git checkout main
git merge develop
git push origin main
git checkout develop
```

### 2. Create and push the version tag

```bash
# Replace v1.0.0 with the correct next version
git tag v1.0.0
git push origin v1.0.0
```

### 3. Deploy on the instance

Run a single non-interactive command via SSM:

```bash
aws ssm send-command \
  --instance-ids i-06df2f36f1836111b \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["sudo chown -R ssm-user:ssm-user /home/ssm-user/aya-ai && sudo -u ssm-user bash -c \"export HOME=/home/ssm-user && cd /home/ssm-user/aya-ai && git pull origin main\""]' \
  --comment "Deploy: git pull origin main" \
  --query "Command.CommandId" \
  --output text
```

Check the output:

```bash
aws ssm get-command-invocation \
  --instance-id i-06df2f36f1836111b \
  --command-id <CommandId from above>
```

If `.env` changed, start an interactive session to edit it:

```bash
aws ssm start-session --target i-06df2f36f1836111b
nano /home/ssm-user/backend/.env
```

### 4. Run database migrations (only if models changed)

> **Run manually — do NOT include in automated deploy commands.**

```bash
aws ssm send-command \
  --instance-ids i-06df2f36f1836111b \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["cd /home/ssm-user/backend && /usr/local/bin/alembic upgrade head"]' \
  --comment "Run Alembic migrations" \
  --query "Command.CommandId" \
  --output text
```

### 5. Restart services

```bash
aws ssm send-command \
  --instance-ids i-06df2f36f1836111b \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["sudo systemctl restart aya-backend"]' \
  --comment "Restart aya-backend" \
  --query "Command.CommandId" \
  --output text
```

Only if Celery task code changed:

```bash
aws ssm send-command \
  --instance-ids i-06df2f36f1836111b \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["sudo systemctl restart aya-celery-worker && sudo systemctl restart aya-celery-beat"]' \
  --comment "Restart Celery services" \
  --query "Command.CommandId" \
  --output text
```

### 6. Verify

```bash
aws ssm send-command \
  --instance-ids i-06df2f36f1836111b \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["sudo systemctl status aya-backend && sudo journalctl -u aya-backend -n 50 --no-pager"]' \
  --comment "Verify aya-backend" \
  --query "Command.CommandId" \
  --output text
```

Check the output with `aws ssm get-command-invocation`. The service should show `active (running)`.

## Key Facts

- **APP + Celery instance**: `i-06df2f36f1836111b` (private subnet — SSM only, no SSH, both backend and Celery run here)
- **Working dir**: `/home/ssm-user/aya-ai` (full repo) — backend code at `/home/ssm-user/aya-ai/backend`
- **S3 bucket**: `s3://aya-ai-bucket`
- **Service names**: `aya-backend`, `aya-celery-worker`, `aya-celery-beat`
- **Celery module**: `-A app.core.celery_app` (NOT `app.core.celery`)
- **No Docker on prod** — bare systemd services
- **Deploy method**: `git pull origin main` inside SSM session at `/home/ssm-user/backend`

## Note: Backend and Celery are on the SAME instance

`i-06df2f36f1836111b` runs both `aya-backend` and `aya-celery-worker`/`aya-celery-beat`. A single SSM session is sufficient for all service restarts.
