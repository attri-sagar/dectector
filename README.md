# Detections as Code for Elasticsearch SIEM

This repository contains the configuration and scripts for managing Elasticsearch SIEM detections as code.

## Workflow

### Rule Management

1.  **Upstream Rules:** The `detection-rules` directory contains a clone of the official `elastic/detection-rules` repository. To update the rules from the upstream repository, navigate to the `detection-rules` directory and run `git pull origin main`.

2.  **Custom Rules:** Custom rules can be added to the `custom_rules` directory. These rules should follow the same TOML format as the official rules.

3.  **Branching Model:** A `main` branch should be used for production-ready rules. A `dev` branch should be used for development and testing of new or modified rules. All changes should be made in a feature branch and then merged into `dev`. Once the changes are tested and approved, they can be merged into `main`.

### Deployment

A Python script will be used to parse the rule files and deploy them to the Elasticsearch cluster via the API.

### CI/CD

A GitHub Actions workflow will be used to automate the testing and deployment of the rules.
