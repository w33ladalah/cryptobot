---
description: Deploy frontend or admin to staging server
---

# Deploy to Staging Server

This workflow deploys the frontend or admin application to the staging server.

## Prerequisites

- You must have SSH access to the staging server
- SSH passphrase: `ayakeren`
- Server address: `ubuntu@52.76.72.86`

## Steps

### 0. Check Environment Variables

Before building, ensure `NEXT_PUBLIC_API_BASE_URL` is set to the staging API URL:

```bash
# For frontend
cd frontend
# Check .env file
cat .env | grep NEXT_PUBLIC_API_BASE_URL
# Should be: NEXT_PUBLIC_API_BASE_URL=https://staging-api.ayalive.ai

# For admin
cd admin
# Check .env file
cat .env | grep NEXT_PUBLIC_API_BASE_URL
# Should be: NEXT_PUBLIC_API_BASE_URL=https://staging-api.ayalive.ai
```

If it's set to `http://localhost:8000`, update it to `https://staging-api.ayalive.ai` before building.

### 1. Build Locally

Navigate to the appropriate directory and build:

```bash
# For frontend
cd frontend
npm run build

# For admin
cd admin
npm run build
```

### 2. Create Bundle

Run the tar command to create the deployment bundle:

```bash
tar -czf bundle/next-build-latest.tar.gz \
  --exclude='.next/cache' \
  --exclude='.next/trace' \
  --exclude='*.map' \
  .next/ \
  package.json \
  next.config.ts \
  public/
```

### 3. Upload to Server

SCP the bundle to the server (you will be prompted for passphrase `ayakeren`):

```bash
# For frontend
scp bundle/next-build-latest.tar.gz ubuntu@52.76.72.86:/home/ubuntu/aya-fe

# For admin
scp bundle/next-build-latest.tar.gz ubuntu@52.76.72.86:/home/ubuntu/aya-admin
```

### 4. Deploy on Server

#### Option A: SSH to server directly

SSH to the server (passphrase: `ayakeren`):

```bash
ssh ubuntu@52.76.72.86
```

Then run the deployment commands:

**For frontend:**

```bash
cd /home/ubuntu/aya-fe
export PATH="/home/ubuntu/.nvm/versions/node/v22.19.0/bin:$PATH"
rm -rf .next/ package* public/ && tar xvf next-build-latest.tar.gz && pm2 update && pm2 restart aya-fe
```

**For admin:**

```bash
cd /home/ubuntu/aya-admin
export PATH="/home/ubuntu/.nvm/versions/node/v22.19.0/bin:$PATH"
rm -rf .next/ package* public/ && tar xvf next-build-latest.tar.gz && pm2 update && pm2 restart aya-admin
```

#### Option B: Run from local via SSH

Run the deployment commands directly from local (passphrase: `ayakeren`):

**For frontend:**

```bash
ssh ubuntu@52.76.72.86 "cd /home/ubuntu/aya-fe && export PATH=\"/home/ubuntu/.nvm/versions/node/v22.19.0/bin:\$PATH\" && rm -rf .next/ package* public/ && tar xvf next-build-latest.tar.gz && pm2 update && pm2 restart aya-fe"
```

**For admin:**

```bash
ssh ubuntu@52.76.72.86 "cd /home/ubuntu/aya-admin && export PATH=\"/home/ubuntu/.nvm/versions/node/v22.19.0/bin:\$PATH\" && rm -rf .next/ package* public/ && tar xvf next-build-latest.tar.gz && pm2 update && pm2 restart aya-admin"
```

### 5. Restore Local Environment

After deployment is complete, change `NEXT_PUBLIC_API_BASE_URL` back to local development:

```bash
# For frontend
cd frontend
# Update .env file
# Change: NEXT_PUBLIC_API_BASE_URL=https://staging-api.ayalive.ai
# To: NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# For admin
cd admin
# Update .env file
# Change: NEXT_PUBLIC_API_BASE_URL=https://staging-api.ayalive.ai
# To: NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Notes

- The tar command excludes cache, trace files, and source maps to reduce bundle size
- The server command removes old files before extracting the new bundle
- The `export PATH` command is required to make node and pm2 available in the SSH session
- `pm2 update` ensures PM2 uses the latest configuration
- `pm2 restart` restarts the application with the new build
