import os
import toml
import requests
import base64
from dotenv import load_dotenv

# Load the .env file from the elastic-container directory
dotenv_path = os.path.join(os.path.dirname(__file__), 'elastic-container', '.env')
load_dotenv(dotenv_path=dotenv_path)

def _build_auth_header(api_key: str) -> str:
    """
    Build the Authorization header value for an API key.

    The api_key can be either:
    - a raw ApiKey token (already base64-encoded or the token string),
      in which case it will be used as-is, or
    - in the form "id:api_key", in which case it will be base64-encoded
      per Elasticsearch/Kibana API Key spec.
    """
    if ":" in api_key:
        # If provided as id:api_key, base64 encode it
        return "ApiKey " + base64.b64encode(api_key.encode()).decode()
    # Otherwise assume the user provided the final token to send
    return "ApiKey " + api_key

def deploy_rules(rules, host, api_key):
    """
    Deploys the given rules to the specified Kibana/Elasticsearch host using API Key auth.
    """
    if not api_key:
        raise ValueError("API key is required to deploy rules. Set ELASTIC_API_KEY (or API_KEY) in the environment.")

    auth_header = _build_auth_header(api_key)

    print(f"Deploying {len(rules)} rules to {host}...")
    for rule in rules:
        rule_id = rule["rule"]["rule_id"]
        url = f"{host}/api/detection_engine/rules?rule_id={rule_id}"
        headers = {
            "kbn-xsrf": "true",
            "Authorization": auth_header,
            "Content-Type": "application/json",
        }
        try:
            response = requests.post(
                url,
                headers=headers,
                json=rule["rule"],
                verify=False,  # keep False to match previous behavior; set to True in production with valid certs
            )
            response.raise_for_status()
            print(f"  - Deployed rule: {rule['rule']['name']}")
        except requests.exceptions.RequestException as e:
            print(f"  - Error deploying rule: {rule['rule']['name']}")
            print(f"    {e}")
    print("Deployment complete.")

def main():
    """
    Parses all detection rules and deploys them to the target host.
    Uses API key authentication (ELASTIC_API_KEY / API_KEY environment variable).
    """
    host = "https://logs.r42ipu.com"
    # Prefer ELASTIC_API_KEY, fall back to generic API_KEY
    api_key = os.getenv("ELASTIC_API_KEY") or os.getenv("API_KEY")

    all_rules = []

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
    deploy_rules(all_rules, host, api_key)

if __name__ == "__main__":
    main()
