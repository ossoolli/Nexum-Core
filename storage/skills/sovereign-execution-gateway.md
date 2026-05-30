---
name: sovereign-execution-gateway
description: "Security and audit orchestration for sovereign agentic systems."
version: 1.0.0
author: Nexum-Core Sentinel
---

# Sovereign Execution Gateway

Handles secure execution, path validation, and tamper-evident auditing for sovereign agents.

## Core Concepts
- **Path Isolation**: Validates all file operations against a `WORKSPACE_DIR` to prevent path traversal.
- **Command Whitelisting**: Restricts shell commands to a predefined set (`git`, `python`, `pip`, `ls`, etc.) to prevent command injection.
- **Tamper-Evident Audit Logs**: All security-critical actions are logged and signed using HMAC-SHA256 to ensure log integrity.
- **Key Management**: Uses `SOVEREIGN_HMAC_KEY`. If missing, the system dynamically generates a secure 32-byte hex key and persists it to `storage/.sovereign_key`.

## Pitfalls
- **Missing HMAC Key**: Always ensure `SOVEREIGN_HMAC_KEY` is present in the environment for production deployments.
- **Dependency Issues**: Ensure `google-cloud-dialogflow-cx` and other GCP libs are installed to prevent unnecessary "simulated mode" fallbacks.

## Verification
- Run tests via: `python3 -m pytest tests/test_sovereign_execution_gateway.py`.
