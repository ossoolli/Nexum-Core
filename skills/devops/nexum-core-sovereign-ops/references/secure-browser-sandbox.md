# Secure Browser Sandbox Operations (NEXUM-Core)

Guide for maintaining and operating the secure browser sandbox capability in NEXUM-Core.

## Overview
The browser sandbox (`core/browser_sandbox.py`) is designed to safely interact with technical web documentation (Playwright/Puppeteer) while strictly enforcing the **AAA Unanimous Security Protocol**:
1. **Isolated Sandbox (Docker Container)**: Runs Playwright inside `mcr.microsoft.com/playwright:v1.40.0-focal` with memory limits (512MB), single CPU, and bridge network isolation to prevent local host OS traversal. Falls back to a local restricted process if Docker is unavailable, logging a high-fidelity warning.
2. **Human-in-the-Loop for Write Actions**: Automatically permits read-only actions (`goto`, `scrape`, `screenshot`). Strictly intercepts and blocks any state-modifying actions (`click`, `type`, `submit`, `press`, `fill`) with a `pending_approval` status, requiring an explicit `approved_by_human: True` parameter.
3. **Domain Whitelisting**: Limits browser navigation to certified programming documentation and official packages (e.g., `github.com`, `stackoverflow.com`, `docs.python.org`, `pypi.org`, `npmjs.com`, `playwright.dev`, `localhost`). Instantly aborts navigation to forbidden domains (e.g., banking portals, cloud console panels) with `DOMAIN_BLOCKED`.
4. **Output Sanitization (Indirect Prompt Injection Defense)**: Immediately filters and scans scraped text for hostile instruction overrides (e.g., "ignore all previous instructions", "format C drive", "delete files"). Neutralizes triggers by substituting them with `[REDACTED_POTENTIAL_INJECTION]`.

## Cryptographic Security Logging
All browser actions are signed via HMAC-SHA256 to create a tamper-evident audit log in `storage/logs/browser_audit.log`. 
- **HMAC Key Management**: Uses `SOVEREIGN_HMAC_KEY` from the environment. If missing, dynamically generates a secure 32-byte hex key at `storage/.sovereign_key`.
- **Validation**: Any security audit check can verify the signature matching `hmac.new(key, "action=X|details=Y", sha256).hexdigest()`.

## Integration as System Tool
Exposed via `core/system_tools.py` under:
- Tool Name: `execute_browser_command(action: str, url: str, selector: str = "", value: str = "", approved_by_human: bool = False)`

## Operational Commands
- **Run Sandbox Tests**: `python3 -m unittest tests/test_browser_sandbox.py`
- **Audit Logs Check**: `cat storage/logs/browser_audit.log`
