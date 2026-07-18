---
description: How to start an AWS EC2 session using SSM
---

# Start AWS EC2 Session

## Prerequisites

- AWS CLI installed
- AWS credentials configured
- Session Manager plugin installed
- EC2 instance ID

## Steps

### 1. Install AWS CLI (if not installed)

```bash
brew install awscli
```

### 2. Configure AWS Credentials

Option A - Use AWS login (recommended for temporary credentials):

```bash
aws login
```

- Select region (e.g., ap-southeast-1)
- Complete browser authentication

Option B - Use AWS configure (for long-term credentials):

```bash
aws configure
```

- Enter AWS Access Key ID
- Enter AWS Secret Access Key
- Enter default region (e.g., ap-southeast-1)
- Enter default output format (optional, leave blank)

### 3. Install Session Manager Plugin

```bash
brew install session-manager-plugin
```

This requires sudo password during installation.

### 4. Start SSM Session

```bash
aws ssm start-session --target <instance-id>
```

Replace `<instance-id>` with your EC2 instance ID (e.g., i-0bc4233a59420ff7f).

### 5. Exit Session

When done, type `exit` to terminate the session.

## Common Issues

### "NoRegion" Error

AWS CLI needs a region configured. Run `aws configure` or `aws login` to set it.

### "SessionManagerPlugin is not found"

Install the plugin: `brew install session-manager-plugin`

### Instance Not Accessible

Ensure:

- SSM Agent is installed and running on the instance
- Instance has the correct IAM role with SSM permissions
- Instance is in a running state
- Security groups allow SSM traffic (no need for open SSH ports when using SSM)
