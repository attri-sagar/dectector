# Detections Engineering

This repository contains tools and configurations for managing detection rules for Elastic Security.

## Overview

This project provides a streamlined workflow for:
- Creating custom detection rules in TOML format
- Validating rule syntax automatically
- Deploying rules to Kibana via CI/CD pipeline
- Managing detection rules with version control

## Project Structure

```
detections_engineering/
├── custom_rules/          # Your custom detection rules (TOML format)
├── detection-rules/       # Elastic's official detection rules (submodule)
├── .github/workflows/     # CI/CD pipeline configuration
│   └── deploy.yml        # Automated deployment workflow
├── deploy.py             # Deployment script with API key support
└── requirements.txt      # Python dependencies
```

## CI/CD Pipeline

The GitHub Actions pipeline automatically:
1. **Validates** all detection rules on pull requests and pushes
2. **Deploys** rules to Kibana when code is pushed to `main` branch
3. **Uploads** deployment logs as artifacts for troubleshooting

### Workflow Triggers

- **Push to main**: Validates and deploys rules
- **Pull Request**: Validates rules only (no deployment)
- **Manual Dispatch**: Deploy on-demand via GitHub Actions UI

## Configuration

### Required GitHub Secrets

Configure these secrets in your GitHub repository settings to enable automated deployment:

**Required Secrets:**
- `KIBANA_URL` - Your Kibana instance URL (e.g., `https://logs.r42ipu.com` or `https://logs.r42ipu.com/api/detection_engine/rules`)
- `KIBANA_API_KEY` - Your Kibana API key for authentication

**Optional Secrets:**
- `VERIFY_SSL` - Set to `false` to disable SSL verification (default: `true`)

**Note:** The script automatically handles the API endpoint path. You can provide either:
- Just the domain: `https://logs.r42ipu.com`
- Or the full endpoint: `https://logs.r42ipu.com/api/detection_engine/rules`

### How to Add GitHub Secrets

1. Navigate to your repository on GitHub
2. Go to **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Add each required secret with its name and value
5. Click **"Add secret"** to save

### How to Create a Kibana API Key

API keys are the recommended authentication method for production deployments.

**Via Kibana UI:**
1. Log into Kibana
2. Navigate to **Stack Management** → **API Keys**
3. Click **"Create API key"**
4. Name your key (e.g., "GitHub Actions Deployment")
5. Set appropriate privileges (minimum: `manage` on Detection Engine)
6. Click **"Create API key"**
7. Copy the encoded API key (you'll only see this once!)
8. Add it as `KIBANA_API_KEY` secret in GitHub

**Via API:**
```bash
curl -X POST "https://logs.r42ipu.com/api/security/api_key" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -H "Authorization: ApiKey YOUR_EXISTING_API_KEY" \
  -d '{
    "name": "github-actions-deploy",
    "role_descriptors": {
      "detection_deployer": {
        "cluster": [],
        "index": [],
        "applications": [{
          "application": "kibana-.kibana",
          "privileges": ["feature_siem.all"],
          "resources": ["*"]
        }]
      }
    }
  }'
```

## Local Development

### Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd detections_engineering
```

2. Initialize the submodule (Elastic's official rules):
```bash
git submodule update --init --recursive
```

3. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file (optional for local testing):
```bash
# .env
KIBANA_URL=https://logs.r42ipu.com
KIBANA_API_KEY=your_api_key_here
VERIFY_SSL=true
```

**Important:** Never commit the `.env` file to version control!

### Creating Custom Rules

1. Create a new `.toml` file in the `custom_rules/` directory
2. Follow the Elastic Detection Rule schema:

```toml
[metadata]
creation_date = "2025/01/15"
updated_date = "2025/01/15"
maturity = "production"

[rule]
author = ["Your Name"]
description = "Detects suspicious activity..."
from = "now-9m"
index = ["logs-endpoint.events.*"]
language = "eql"
license = "Elastic License v2"
name = "Your Detection Rule Name"
risk_score = 47
severity = "medium"
rule_id = "your-unique-uuid-here"
type = "eql"
query = '''
process where event.type == "start" and
  process.name : "suspicious.exe"
'''

[[rule.threat]]
framework = "MITRE ATT&CK"

[[rule.threat.technique]]
id = "T1059"
name = "Command and Scripting Interpreter"

[rule.threat.tactic]
id = "TA0002"
name = "Execution"
```

3. Validate your rule locally:
```bash
python deploy.py  # With proper .env configuration
```

### Manual Deployment

To deploy rules manually (without CI/CD):

```bash
# Ensure .env is configured or export environment variables
export KIBANA_URL="https://logs.r42ipu.com"
export KIBANA_API_KEY="your_api_key"

# Run deployment script
python deploy.py
```

## Workflow Details

### Validation Job
- Runs on all pull requests and pushes
- Validates TOML syntax
- Checks for required fields (`[rule]` section, `rule_id`)
- Fails the build if validation errors are found

### Deployment Job
- Runs only on pushes to `main` or manual workflow dispatch
- Requires validation job to pass first
- Deploys all custom rules from `custom_rules/` directory
- Uploads deployment logs as artifacts (retained for 30 days)

## Troubleshooting

### Common Issues

**Authentication Failures:**
- Verify your API key or credentials are correct
- Check that the Kibana URL is accessible from GitHub Actions runners
- Ensure your API key has sufficient permissions

**SSL Verification Errors:**
- For development/testing, set `VERIFY_SSL=false` (not recommended for production)
- For production, ensure your Kibana instance has a valid SSL certificate

**Rule Deployment Failures:**
- Check deployment logs artifact in GitHub Actions
- Verify rule syntax is valid TOML
- Ensure `rule_id` is unique and properly formatted as UUID
- Check that required fields are present in rule definition

**No Rules Found:**
- Ensure `.toml` files are in the `custom_rules/` directory
- Verify files are committed to the repository
- Check that submodules are initialized if using official rules

### Viewing Deployment Logs

1. Go to your GitHub repository
2. Click on **Actions** tab
3. Select the workflow run you want to inspect
4. Click on the **deploy** job
5. Scroll to **"Artifacts"** section
6. Download **deployment-logs** artifact

## Security Best Practices

1. **Never commit secrets** to the repository (`.env` is in `.gitignore`)
2. **Use API key authentication** (format: `"ApiKey " + your_api_key`)
3. **Enable SSL verification** in production environments
4. **Rotate API keys** periodically
5. **Use branch protection** to require PR reviews before merging to main
6. **Limit API key permissions** to only what's needed for rule deployment

## Quick Start for Testing

1. **Set up your environment variables:**
```bash
# Create .env file
echo 'KIBANA_URL=https://logs.r42ipu.com' > .env
echo 'KIBANA_API_KEY=your_actual_api_key_here' >> .env
echo 'VERIFY_SSL=true' >> .env
```

2. **Test deployment locally:**
```bash
python deploy.py
```

3. **Configure GitHub Secrets** for automated deployment:
   - Go to repository Settings → Secrets and variables → Actions
   - Add `KIBANA_URL` = `https://logs.r42ipu.com`
   - Add `KIBANA_API_KEY` = your API key
   - (Optional) Add `VERIFY_SSL` = `false` for testing with self-signed certs

4. **Push to main branch** to trigger automatic deployment

## Additional Resources

- [Elastic Detection Rules Documentation](https://www.elastic.co/guide/en/security/current/rules-ui-management.html)
- [Elastic Detection Rules Repository](https://github.com/elastic/detection-rules)
- [TOML Format Specification](https://toml.io/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)