# GitHub Secrets Configuration

This document lists all required GitHub Secrets for the CI/CD pipeline.

## Required Secrets

### Coverage & Reporting

- **`CODECOV_TOKEN`**: Token for uploading coverage reports to Codecov
  - **Obtain from**: <https://codecov.io/> (after connecting repository)
  - **Used in**: `pr-validation.yml`, `main-integration.yml`, `nightly-checks.yml`
  - **Required**: Yes
  - **Format**: UUID string (e.g., `a1b2c3d4-e5f6-7890-abcd-ef1234567890`)

### Notifications

- **`SLACK_WEBHOOK`**: Slack incoming webhook URL for team notifications
  - **Obtain from**: Slack App settings → Incoming Webhooks
  - **Used in**: `main-integration.yml`, `nightly-checks.yml`, `production-deploy.yml`
  - **Required**: No (notifications will be skipped if not configured)
  - **Format**: `https://hooks.slack.com/services/TXXXXXXXXX/BXXXXXXXXX/YOUR_WEBHOOK_TOKEN_HERE`

- **`DISCORD_WEBHOOK`**: Discord webhook URL (alternative to Slack)
  - **Obtain from**: Discord Server Settings → Integrations → Webhooks
  - **Used in**: Same as `SLACK_WEBHOOK`
  - **Required**: No
  - **Format**: `https://discord.com/api/webhooks/000000000000000000/xxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Deployment Keys

- **`STAGING_DEPLOY_KEY`**: SSH private key for staging environment deployment
  - **Obtain from**: Generate with `ssh-keygen -t ed25519 -C "github-actions-staging"`
  - **Used in**: `main-integration.yml`
  - **Required**: Yes (if automatic staging deployment is enabled)
  - **Format**: Multi-line SSH private key (include `-----BEGIN OPENSSH PRIVATE KEY-----` header/footer)
  - **Public key**: Add to `~/.ssh/authorized_keys` on staging server

- **`PRODUCTION_DEPLOY_KEY`**: SSH private key for production environment deployment
  - **Obtain from**: Generate with `ssh-keygen -t ed25519 -C "github-actions-production"`
  - **Used in**: `production-deploy.yml`
  - **Required**: Yes (for production deployments)
  - **Format**: Multi-line SSH private key
  - **Public key**: Add to `~/.ssh/authorized_keys` on production server

### Deployment Configuration (Optional Environment-Specific)

- **`STAGING_HOST`**: Hostname/IP of staging server (e.g., `staging.heatflow.world`)
- **`STAGING_USER`**: SSH username for staging deployment (e.g., `deploy`)
- **`PRODUCTION_HOST`**: Hostname/IP of production server (e.g., `heatflow.world`)
- **`PRODUCTION_USER`**: SSH username for production deployment (e.g., `deploy`)

These can be configured as secrets or in workflow files depending on sensitivity.

## Setup Instructions

### 1. Configure Secrets in GitHub

1. Navigate to repository: `Settings` → `Secrets and variables` → `Actions`
2. Click `New repository secret`
3. Add each secret with its name and value
4. Click `Add secret`

### 2. Generate SSH Deploy Keys

```bash
# For staging
ssh-keygen -t ed25519 -C "github-actions-staging" -f ./staging_deploy_key
# Copy content of staging_deploy_key (private key) to STAGING_DEPLOY_KEY secret
# Copy content of staging_deploy_key.pub (public key) to staging server

# For production
ssh-keygen -t ed25519 -C "github-actions-production" -f ./production_deploy_key
# Copy content of production_deploy_key (private key) to PRODUCTION_DEPLOY_KEY secret
# Copy content of production_deploy_key.pub (public key) to production server
```

### 3. Add Public Keys to Deployment Servers

On staging/production servers:

```bash
# As deploy user
mkdir -p ~/.ssh
chmod 700 ~/.ssh
cat >> ~/.ssh/authorized_keys << EOF
<paste public key content here>
EOF
chmod 600 ~/.ssh/authorized_keys
```

### 4. Configure Codecov

1. Go to <https://codecov.io/> and sign in with GitHub
2. Add the repository to Codecov
3. Copy the upload token
4. Add as `CODECOV_TOKEN` secret in GitHub

### 5. Configure Slack/Discord Webhooks

**Slack**:

1. Go to <https://api.slack.com/apps>
2. Create new app → From scratch
3. Enable Incoming Webhooks
4. Add New Webhook to Workspace
5. Copy webhook URL and add as `SLACK_WEBHOOK` secret

**Discord**:

1. Go to Server Settings → Integrations → Webhooks
2. Create webhook
3. Copy webhook URL and add as `DISCORD_WEBHOOK` secret

## Verification

After configuring secrets, verify they are available:

1. Go to repository `Settings` → `Secrets and variables` → `Actions`
2. You should see all configured secrets listed (values are hidden)
3. Workflows will fail with clear error messages if required secrets are missing

## Security Best Practices

- **Never commit secrets to the repository**
- **Rotate deploy keys periodically** (at least annually)
- **Use separate keys for staging and production**
- **Limit SSH key permissions** on servers (read-only for application user where possible)
- **Use environment protection rules** for production deployments (Settings → Environments → production → Required reviewers)
- **Audit secret usage** regularly in workflow runs

## Troubleshooting

### Secret not found error

```text
Error: Secret CODECOV_TOKEN is not defined
```

**Solution**: Verify the secret name matches exactly (case-sensitive) and is configured in repository settings.

### SSH authentication failed

```text
Permission denied (publickey)
```

**Solution**:

1. Verify public key is added to `~/.ssh/authorized_keys` on target server
2. Verify private key is correctly pasted into GitHub secret (include BEGIN/END lines)
3. Check SSH user and host are correct in workflow configuration

### Webhook notification failed

```text
⚠️  Notification failed with HTTP 404
```

**Solution**:

1. Verify webhook URL is correct and not expired
2. Check webhook is still active in Slack/Discord settings
3. Test webhook manually using curl
