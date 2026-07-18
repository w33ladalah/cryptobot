---
description: Deploy frontend or admin to production EC2 (FE instance via S3 + AWS SSM)
---

# Deploy Frontend / Admin to Production

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

## Git Flow (before building)

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

Create and push the version tag:

```bash
# Replace v1.0.0 with the correct next version
git tag v1.0.0
git push origin v1.0.0
```

## Key Facts

- **FE instance**: `i-0e598569b320c8906` (AYA-EC2-FE-prod, public, accessible via SSM)
- **Working dirs**: `/home/ssm-user/frontend` and `/home/ssm-user/admin`
- **User**: `ssm-user` (PM2 must run as this user — NOT root or ec2-user)
- **PM2 app names**: `aya-fe` (frontend), `aya-admin` (admin)
- **API base URL (prod)**: `https://api.ayamodels.ai`
- **S3 bucket**: `aya-ai-bucket`

---

## Deploy Frontend

### 1. Set environment variable for production build

Ensure `frontend/.env` has:

```env
NEXT_PUBLIC_API_BASE_URL=https://api.ayamodels.ai
```

### 2. Build locally

```bash
npm run build
```

Run from the `frontend/` directory.

### 3. Bundle the build

```bash
COPYFILE_DISABLE=1 tar -czf /tmp/next-build-latest.tar.gz \
  --exclude='.next/cache' \
  --exclude='.next/trace' \
  --exclude='*.map' \
  .next/ \
  package.json \
  next.config.ts \
  public/
```

Run from the `frontend/` directory.

### 4. Upload to S3

```bash
aws s3 cp /tmp/next-build-latest.tar.gz s3://aya-ai-bucket/frontend-deploy/next-build-latest.tar.gz
```

### 5. Deploy on the instance

```bash
aws ssm send-command \
  --instance-ids i-0e598569b320c8906 \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["aws s3 cp s3://aya-ai-bucket/frontend-deploy/next-build-latest.tar.gz /tmp/ && cd /home/ssm-user/frontend && rm -rf .next/ package* public/ && tar -xzf /tmp/next-build-latest.tar.gz && sudo chown -R ssm-user:ssm-user /home/ssm-user/frontend && export PATH=/home/ssm-user/.nvm/versions/node/v22.19.0/bin:$PATH && pm2 update && pm2 restart aya-fe"]' \
  --comment "Deploy frontend" \
  --query "Command.CommandId" \
  --output text
```

Check the output:

```bash
aws ssm get-command-invocation \
  --instance-id i-0e598569b320c8906 \
  --command-id <CommandId from above>
```

### 6. Verify

```bash
aws ssm send-command \
  --instance-ids i-0e598569b320c8906 \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["export PATH=/home/ssm-user/.nvm/versions/node/v22.19.0/bin:$PATH && pm2 status && pm2 logs aya-fe --lines 30 --nostream"]' \
  --comment "Verify aya-fe" \
  --query "Command.CommandId" \
  --output text
```

### 7. Restore local env (important!)

Change `frontend/.env` back to local development:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

## Deploy Admin

### 1. Set admin env for production build

Ensure `admin/.env` has:

```env
NEXT_PUBLIC_API_BASE_URL=https://api.ayamodels.ai
```

### 2. Build admin locally

```bash
npm run build
```

Run from the `admin/` directory.

### 3. Bundle the admin build

```bash
COPYFILE_DISABLE=1 tar -czf /tmp/admin-build-latest.tar.gz \
  --exclude='.next/cache' \
  --exclude='.next/trace' \
  --exclude='*.map' \
  .next/ \
  package.json \
  next.config.ts \
  public/
```

Run from the `admin/` directory.

### 4. Upload admin build to S3

```bash
aws s3 cp /tmp/admin-build-latest.tar.gz s3://aya-ai-bucket/frontend-deploy/admin-build-latest.tar.gz
```

### 5. Deploy admin on the instance

```bash
aws ssm send-command \
  --instance-ids i-0e598569b320c8906 \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["aws s3 cp s3://aya-ai-bucket/frontend-deploy/admin-build-latest.tar.gz /tmp/ && cd /home/ssm-user/admin && rm -rf .next/ package* public/ && tar -xzf /tmp/admin-build-latest.tar.gz && sudo chown -R ssm-user:ssm-user /home/ssm-user/admin && export PATH=/home/ssm-user/.nvm/versions/node/v22.19.0/bin:$PATH && pm2 update && pm2 restart aya-admin"]' \
  --comment "Deploy admin" \
  --query "Command.CommandId" \
  --output text
```

Check the output:

```bash
aws ssm get-command-invocation \
  --instance-id i-0e598569b320c8906 \
  --command-id <CommandId from above>
```

### 6. Verify admin

```bash
aws ssm send-command \
  --instance-ids i-0e598569b320c8906 \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["export PATH=/home/ssm-user/.nvm/versions/node/v22.19.0/bin:$PATH && pm2 status && pm2 logs aya-admin --lines 30 --nostream"]' \
  --comment "Verify aya-admin" \
  --query "Command.CommandId" \
  --output text
```

### 7. Restore admin local env (important!)

Change `admin/.env` back to local development:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

## Common Issues

### PM2 EADDRINUSE (port already in use) / pm2 restart doesn't work

**Root cause (confirmed Jul 2026):** Multiple orphaned PM2 daemons can end up running simultaneously as different users (`root`, `ec2-user`, `ssm-user`) — sometimes even *duplicate* daemons for the same user. Each daemon has its own isolated `PM2_HOME` (`/root/.pm2`, `/home/ec2-user/.pm2`, `/home/ssm-user/.pm2`) and its own process registry. Because of this:

- `pm2 restart aya-fe` from an SSM/SSH session may attach to a *different* daemon than the one actually bound to port 3000/3001, so the restart appears to succeed but the live process is untouched.
- Each daemon independently tries to keep its own copy of `aya-fe`/`aya-admin` alive, so killed `next-server` processes get instantly respawned by a different daemon — looks like "PM2 won't let me kill it."

**Diagnose first** — check for multiple daemons before doing anything else:

```bash
ps -eo pid,ppid,user,cmd | grep "PM2 v7" | grep -v grep
```

If you see more than one line (or duplicates for the same user), you have this problem.

**Full fix — kill everything and start exactly one daemon as `ssm-user`:**

```bash
# 1. Kill all PM2 daemons and app processes across all users
sudo pkill -9 -f "PM2 v7" || true
sudo pkill -9 -f next-server || true
sudo pkill -9 -f "npm start" || true
sleep 3

# 2. Remove ALL .pm2 state directories (this is what actually breaks the loop)
sudo rm -rf /root/.pm2 /home/ec2-user/.pm2 /home/ssm-user/.pm2

# 3. Verify clean slate
ps -eo pid,ppid,user,cmd | grep -E "PM2 v7|next-server|npm start" | grep -v grep || echo "clean"
sudo ss -tulpn | grep -E "3000|3001" || echo "ports free"

# 4. Start fresh, only as ssm-user, then persist
sudo chown -R ssm-user:ssm-user /home/ssm-user/frontend /home/ssm-user/admin
sudo -u ssm-user bash -c 'export PATH=/home/ssm-user/.nvm/versions/node/v22.19.0/bin:$PATH && cd /home/ssm-user/frontend && pm2 start npm --name aya-fe -- start'
sudo -u ssm-user bash -c 'export PATH=/home/ssm-user/.nvm/versions/node/v22.19.0/bin:$PATH && cd /home/ssm-user/admin && pm2 start npm --name aya-admin -- start'
sudo -u ssm-user bash -c 'export PATH=/home/ssm-user/.nvm/versions/node/v22.19.0/bin:$PATH && pm2 save'
```

**Prevention — always run PM2 commands scoped to `ssm-user` explicitly:**

```bash
sudo -u ssm-user bash -c 'export PATH=/home/ssm-user/.nvm/versions/node/v22.19.0/bin:$PATH && pm2 <command>'
```

Never run bare `pm2 ...` in a root shell, and never `sudo su - ec2-user` then run `pm2` — both create a new orphaned daemon under that user.

### EACCES / permission errors on public/

```bash
sudo chown -R ssm-user:ssm-user /home/ssm-user/frontend
sudo chown -R ssm-user:ssm-user /home/ssm-user/admin
```

### PM2 not found in SSM session

```bash
export PATH="/home/ssm-user/.nvm/versions/node/v22.19.0/bin:$PATH"
```
