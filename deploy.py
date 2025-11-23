import os
import toml
import requests
from dotenv import load_dotenv

# Load the .env file from the project root
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

def deploy_rules(rules, host, api_key, verify_ssl=True):
    """
    Deploys the given rules to the specified Kibana host using API key authentication.

    Args:
        rules: List of rules to deploy
        host: Kibana URL (e.g., logs.r42ipu.com/api/detection_engine/rules)
        api_key: API key for authentication
        verify_ssl: Whether to verify SSL certificates (default: True)
    """
    print(f"Deploying {len(rules)} rules to {host}...")
    print("Using API key authentication")

    headers = {
        "kbn-xsrf": "true",
        "Content-Type": "application/json",
        "Authorization": "ApiKey " + api_key
    }

    deployed_count = 0
    failed_count = 0

    for rule in rules:
        rule_id = rule["rule"]["rule_id"]
        rule_name = rule["rule"]["name"]

        # Ensure the URL ends with the detection_engine/rules endpoint
        if not host.endswith("/api/detection_engine/rules"):
            if host.endswith("/"):
                url = f"{host}api/detection_engine/rules"
            else:
                url = f"{host}/api/detection_engine/rules"
        else:
            url = host

        try:
            response = requests.post(
                url,
                headers=headers,
                json=rule["rule"],
                verify=verify_ssl,
            )
            response.raise_for_status()
            print(f"  ✓ Deployed rule: {rule_name}")
            deployed_count += 1
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Error deploying rule: {rule_name}")
            print(f"    {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"    Status Code: {e.response.status_code}")
                print(f"    Response: {e.response.text}")
            failed_count += 1

    print(f"\nDeployment complete: {deployed_count} successful, {failed_count} failed")

def main():
    """
    Parses all detection rules and deploys them to Kibana using API key authentication.
    """
    host = os.getenv("KIBANA_URL", "https://logs.r42ipu.com")
    api_key = os.getenv("KIBANA_API_KEY")
    verify_ssl = os.getenv("VERIFY_SSL", "true").lower() in ("true", "1", "yes")

    # Validate API key is provided
    if not api_key:
        print("Error: KIBANA_API_KEY environment variable must be set.")
        return

    all_rules = []

    # Parse the official rules (uncomment to deploy Elastic's official rules)
    # for root, dirs, files in os.walk("detection-rules/rules"):
    #     for file in files:
    #         if file.endswith(".toml"):
    #             rule_path = os.path.join(root, file)
    #             try:
    #                 with open(rule_path, "r") as f:
    #                     rule = toml.load(f)
    #                     all_rules.append(rule)
    #             except (toml.TomlDecodeError, IndexError):
    #                 continue

    # Parse the custom rules
    custom_rules_dir = os.path.join(os.path.dirname(__file__), "custom_rules")
    if os.path.exists(custom_rules_dir):
        for root, dirs, files in os.walk(custom_rules_dir):
            for file in files:
                if file.endswith(".toml"):
                    rule_path = os.path.join(root, file)
                    try:
                        with open(rule_path, "r") as f:
                            rule = toml.load(f)
                            all_rules.append(rule)
                    except (toml.TomlDecodeError, IndexError) as e:
                        print(f"Warning: Failed to parse {rule_path}: {e}")
                        continue

    print(f"Found {len(all_rules)} rules.")

    if len(all_rules) == 0:
        print("No rules found to deploy.")
        return

    deploy_rules(all_rules, host, api_key, verify_ssl=verify_ssl)

if __name__ == "__main__":
    main()
