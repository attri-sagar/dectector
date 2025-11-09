import os
import toml
import requests
from dotenv import load_dotenv

# Load the .env file from the elastic-container directory
dotenv_path = os.path.join(os.path.dirname(__file__), 'elastic-container', '.env')
load_dotenv(dotenv_path=dotenv_path)

def deploy_rules(rules, host, username, password):
    """
    Deploys the given rules to the specified Elasticsearch host.
    """
    print(f"Deploying {len(rules)} rules to {host}...")
    for rule in rules:
        rule_id = rule["rule"]["rule_id"]
        url = f"{host}/api/detection_engine/rules?rule_id={rule_id}"
        headers = {
            "kbn-xsrf": "true",
        }
        try:
            response = requests.post(
                url,
                auth=(username, password),
                headers=headers,
                json=rule["rule"],
                verify=False,
            )
            response.raise_for_status()
            print(f"  - Deployed rule: {rule['rule']['name']}")
        except requests.exceptions.RequestException as e:
            print(f"  - Error deploying rule: {rule['rule']['name']}")
            print(f"    {e}")
    print("Deployment complete.")

def main():
    """
    Parses all detection rules and deploys them to Elasticsearch.
    """
    host = "https://localhost:5601"
    username = "elastic"
    password = os.getenv("ELASTIC_PASSWORD")

    all_rules = []
    # Parse the official rules
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
    for root, dirs, files in os.walk("custom_rules"):
        for file in files:
            if file.endswith(".toml"):
                rule_path = os.path.join(root, file)
                try:
                    with open(rule_path, "r") as f:
                        rule = toml.load(f)
                        all_rules.append(rule)
                except (toml.TomlDecodeError, IndexError):
                    continue

    print(f"Found {len(all_rules)} rules.")
    deploy_rules(all_rules, host, username, password)

if __name__ == "__main__":
    main()
