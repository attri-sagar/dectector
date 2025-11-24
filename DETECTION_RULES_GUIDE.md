# Using Elastic Detection Rules CLI

This guide explains how to use the official Elastic detection-rules CLI tools for rule creation, validation, deletion, and management.

## Installation

The detection-rules package is installed automatically when you run:

```bash
# Ensure submodule is initialized
git submodule update --init --recursive

# Install dependencies including detection-rules CLI
pip install -r requirements.txt
```

This installs the official Elastic package from the `detection-rules/` submodule in editable mode.

## Rule Lifecycle Management

### Creating New Rules

Use the official detection-rules CLI to create new rules:

```bash
# Create a new rule using the CLI
python -m detection_rules create-rule

# Or use templates from the official repo
cp detection-rules/rules/windows/example.toml custom_rules/my_new_rule.toml
```

Edit your rule in `custom_rules/` directory following the Elastic schema.

### Viewing Rules

```bash
# List all custom rules
python -m detection_rules view-rule custom_rules/*.toml

# View specific rule details
python -m detection_rules view-rule custom_rules/example_rule.toml
```

### Deleting Rules

To delete a rule:

1. **Remove from local repository:**
```bash
rm custom_rules/rule_to_delete.toml
git add custom_rules/rule_to_delete.toml
git commit -m "Remove rule: rule_to_delete"
git push origin main
```

2. **Delete from Kibana (manual):**
```bash
# Using the Kibana Detection Engine API
curl -X DELETE "https://logs.r42ipu.com/api/detection_engine/rules?rule_id=YOUR_RULE_ID" \
  -H "kbn-xsrf: true" \
  -H "Authorization: ApiKey YOUR_API_KEY"
```

Or delete via Kibana UI: Security → Manage → Rules → Delete

### Updating Rules

1. Edit the `.toml` file in `custom_rules/`
2. Update the `updated_date` in metadata
3. Validate: `./validate_rules.sh`
4. Commit and push - the CI/CD will deploy the update

## Available CLI Commands

### 1. View Rule Details

View detailed information about a specific rule:

```bash
python -m detection_rules view-rule custom_rules/example_rule.toml
```

### 2. Validate Rules

Run comprehensive validation tests on your custom rules:

```bash
# Validate all rules in custom_rules directory
python -m detection_rules test --rule-dir custom_rules/

# Validate specific rule
python -m detection_rules test custom_rules/example_rule.toml
```

### 3. List Rules

List all available rules:

```bash
# List custom rules
CUSTOM_RULES_DIR=./custom_rules python -m detection_rules view-rule --rule-dir custom_rules/
```

### 4. Rule Schema Validation

Validate against Elastic's rule schema:

```bash
# This happens automatically during 'test' command
python -m detection_rules test --rule-dir custom_rules/
```

### 5. Query Validation

Validate KQL, EQL, or ESQL queries (requires Elasticsearch connection):

```bash
# Set Elasticsearch connection
export ELASTICSEARCH_URL="https://your-es-instance.com:9200"
export ELASTICSEARCH_USERNAME="elastic"
export ELASTICSEARCH_PASSWORD="your_password"

# Validate queries
python -m detection_rules test --rule-dir custom_rules/ --es-validate
```

## Helper Scripts

### Quick Validation Script

Use the provided validation script for quick checks:

```bash
./validate_rules.sh
```

This script runs:
1. Basic TOML syntax validation
2. Elastic schema validation
3. Rule details view

### Local Testing Before Commit

Before committing new rules, run:

```bash
# Validate rules
./validate_rules.sh

# Test deployment locally (requires .env setup)
python deploy.py
```

## Common Use Cases

### Creating a New Rule

1. Create a new `.toml` file in `custom_rules/`
2. Use an existing rule as a template
3. Validate with: `./validate_rules.sh`
4. Test deployment: `python deploy.py`

### Debugging Rule Validation Errors

If validation fails:

```bash
# Get detailed error messages
python -m detection_rules test custom_rules/your_rule.toml -v

# View rule structure
python -m detection_rules view-rule custom_rules/your_rule.toml
```

### Checking Rule Schema Requirements

```bash
# View available schemas
python -m detection_rules dev schema-map

# Get current package version requirements
python -m detection_rules dev current-stack-version
```

## Advanced Features

### Using Detection Rules Python API

You can import detection-rules in your Python scripts:

```python
from detection_rules.rule_loader import RuleCollection
from detection_rules.rule import TOMLRule

# Load rules
rules = RuleCollection.default()

# Validate a specific rule
rule = TOMLRule.load_from_file('custom_rules/example_rule.toml')
rule.validate()
```

### Custom Validation in deploy.py

You can add custom validation before deployment:

```python
from detection_rules.rule import TOMLRule

# In your deploy script, before deploying
for rule_path in rule_files:
    try:
        rule = TOMLRule.load_from_file(rule_path)
        rule.validate()
        print(f"✅ {rule_path} validated")
    except Exception as e:
        print(f"❌ {rule_path} failed: {e}")
        raise
```

## CI/CD Integration

The GitHub Actions workflow automatically:
1. Checks out the detection-rules submodule
2. Installs the detection-rules package
3. Runs validation on all custom rules
4. Deploys validated rules to Kibana

See [.github/workflows/deploy.yml](.github/workflows/deploy.yml) for details.

## Troubleshooting

### Issue: "Module 'detection_rules' not found"

**Solution:**
```bash
# Ensure submodule is initialized
git submodule update --init --recursive

# Reinstall requirements
pip install -r requirements.txt
```

### Issue: Validation fails with schema errors

**Solution:**
- Check that your rule follows the Elastic Detection Rule schema
- Compare with examples in `detection-rules/rules/`
- Use `view-rule` to see expected structure

### Issue: Query validation fails

**Solution:**
- Ensure Elasticsearch connection is configured
- Check that your query syntax is correct for the query language (KQL/EQL/ESQL)
- Test queries in Kibana Dev Tools first

## Resources

- [Elastic Detection Rules Repo](https://github.com/elastic/detection-rules)
- [Detection Rules CLI Documentation](https://github.com/elastic/detection-rules/blob/main/CLI.md)
- [Rule Schema Definitions](https://github.com/elastic/detection-rules/tree/main/detection_rules/schemas)
- [MITRE ATT&CK Framework](https://attack.mitre.org/)

## Complete Rule Lifecycle Workflows

### Workflow 1: Create a New Rule

```bash
# 1. Use an existing rule as template
cp detection-rules/rules/windows/credential_access_cmdline_dump_tool.toml custom_rules/my_new_rule.toml

# 2. Edit the rule - update ALL fields including rule_id
vim custom_rules/my_new_rule.toml

# 3. Generate new UUID for rule_id
python -c "import uuid; print(uuid.uuid4())"

# 4. Validate with detection-rules CLI
python -m detection_rules view-rule custom_rules/my_new_rule.toml
./validate_rules.sh

# 5. Test deployment locally (optional)
python deploy.py

# 6. Commit and push
git add custom_rules/my_new_rule.toml
git commit -m "feat: Add new detection rule for XYZ"
git push origin main
```

### Workflow 2: Update an Existing Rule

```bash
# 1. Edit the rule
vim custom_rules/existing_rule.toml

# 2. Update the metadata updated_date
# [metadata]
# updated_date = "2025/01/24"

# 3. Validate changes
./validate_rules.sh

# 4. Commit and push
git add custom_rules/existing_rule.toml
git commit -m "update: Improve detection logic for existing_rule"
git push origin main
```

### Workflow 3: Delete a Rule

```bash
# 1. Note the rule_id first (you'll need it for Kibana)
grep "rule_id" custom_rules/rule_to_delete.toml

# 2. Delete local file
rm custom_rules/rule_to_delete.toml

# 3. Commit deletion
git add custom_rules/rule_to_delete.toml
git commit -m "remove: Delete obsolete rule"
git push origin main

# 4. Delete from Kibana (using curl or Kibana UI)
curl -X DELETE "https://logs.r42ipu.com/api/detection_engine/rules?rule_id=RULE_UUID" \
  -H "kbn-xsrf: true" \
  -H "Authorization: ApiKey $KIBANA_API_KEY"
```

### Workflow 4: Bulk Operations

```bash
# View all rules
python -m detection_rules view-rule custom_rules/*.toml

# Validate all rules
python -m detection_rules test --rule-dir custom_rules/

# Export rules for backup
for rule in custom_rules/*.toml; do
  python -m detection_rules view-rule "$rule" > "${rule}.json"
done
```

## Using Detection-Rules CLI Tools

The detection-rules submodule provides powerful CLI commands:

```bash
# Show all available commands
python -m detection_rules --help

# Create new rule (if supported in your version)
cd detection-rules
python -m detection_rules create-rule

# Run tests on your rules
python -m detection_rules test --rule-dir ../custom_rules/

# View rule schema
python -m detection_rules dev schema

# Check package version
python -m detection_rules dev current-stack-version
```

The CI/CD pipeline will automatically validate and deploy your rules!
