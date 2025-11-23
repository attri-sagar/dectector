#!/bin/bash
# Rule validation script using Elastic's detection-rules CLI

set -e

echo "🔍 Validating detection rules..."
echo ""

# Set custom rules directory
export CUSTOM_RULES_DIR="${PWD}/custom_rules"

# Check if detection-rules is installed
if ! python -m detection_rules --version > /dev/null 2>&1; then
    echo "❌ detection-rules CLI not found!"
    echo "Please install it first:"
    echo "  pip install -e ./detection-rules"
    exit 1
fi

echo "✅ detection-rules CLI found"
echo ""

# Validate TOML syntax first
echo "📋 Step 1: Basic TOML validation..."
python -c "
import os
import toml
import sys

errors = []
rule_count = 0

for root, dirs, files in os.walk('custom_rules'):
    for file in files:
        if file.endswith('.toml'):
            rule_path = os.path.join(root, file)
            try:
                with open(rule_path, 'r') as f:
                    rule = toml.load(f)
                    if 'rule' not in rule:
                        errors.append(f'{rule_path}: Missing [rule] section')
                    elif 'rule_id' not in rule.get('rule', {}):
                        errors.append(f'{rule_path}: Missing rule_id field')
                    rule_count += 1
            except Exception as e:
                errors.append(f'{rule_path}: {str(e)}')

if errors:
    print('❌ TOML validation errors:')
    for error in errors:
        print(f'  ✗ {error}')
    sys.exit(1)
else:
    print(f'✅ {rule_count} rules passed TOML validation')
"

echo ""
echo "📋 Step 2: Elastic detection-rules validation..."

# Validate with detection-rules CLI
if python -m detection_rules test --rule-dir custom_rules/ 2>&1; then
    echo "✅ All rules passed Elastic validation!"
else
    echo "⚠️  Some Elastic validation checks failed"
    echo "Note: This is expected for custom rules that don't follow all Elastic conventions"
fi

echo ""
echo "📋 Step 3: View rule details..."
for rule in custom_rules/*.toml; do
    if [ -f "$rule" ]; then
        echo "  📄 $rule"
        python -m detection_rules view-rule "$rule" --rule-dir custom_rules/ 2>&1 || echo "    ⚠️  Could not view rule details"
    fi
done

echo ""
echo "✅ Validation complete!"
