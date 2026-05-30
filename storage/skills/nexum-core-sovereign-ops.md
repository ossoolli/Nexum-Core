---
name: nexum-core-sovereign-ops
description: Operations, security, and maintenance playbook for the Nexum-Core Sovereign OS.
version: 1.0.0
author: Nexum Sovereign Core
tags: [nexum, sovereign, ops, security, audit, consensus]
---

# Nexum Core Sovereign Operations

Playbook for maintaining and evolving the Nexum-Core agentic operating system.

## Core Operations
- **System Startup:** `pm2 start ecosystem.config.js`
- **Active PM2 Services:** The system runs under the following key PM2 processes:
  - `nexum-api`: Core FastAPI interface.
  - `nexum-core`: Central orchestrator/agent logic.
  - `nexum-sentinel`: Autonomous self-healing and evolution process.
  - `nexum-chronos`: Hourly system health and heartbeat reporter to the log channel.
  - `telegram-summarizer-bot`: Main channel notification and summarizing helper.
- **Telegram Notification & Log Delivery:** The channel **Mutaz live** (ID: `-1003969021809`), also known as the *Nexum Log Channel*, is configured as the default Home Channel. All terminal operations, logs, and audit alerts are dispatched directly here.
- **Security Audit:** Run `/sec_audit` from Telegram to trigger audit logging.
- **Protocol Execution:** Trigger workflows via `/run_protocol <name>`.
- **Kanban Task Sync:** Use the Kanban board in Telegram to track agent repair tasks.
- **Memory & Skills Indexing:** Run the indexing scripts using Nexum-Core's virtual environment to update sovereign memory after codebase or skill updates:
  - Skills: `/home/madarmutaz/Nexum-Core/venv/bin/python3 index_skills.py`
  - Codebase: `/home/madarmutaz/Nexum-Core/venv/bin/python3 index_codebase.py`
  - Logs/Docs/Protocols: `/home/madarmutaz/Nexum-Core/venv/bin/python3 index_full.py`
  - Triggers: `/home/madarmutaz/Nexum-Core/venv/bin/python3 index_trigger.py`
  - Kanban: `/home/madarmutaz/Nexum-Core/venv/bin/python3 index_kanban.py`
- **Autonomous Self-Healing & Monitoring:**
  * **Monitoring Script:** Located at `/home/madarmutaz/Nexum-Core/storage/scripts/monitor_nexum.py`. It inspects PM2 service states, checks live Gemini Vertex AI connectivity, and scans logs (`err.log`, `api_err.log`, `sentinel.log`) for critical issues. Run it via:
    `/home/madarmutaz/Nexum-Core/venv/bin/python3 /home/madarmutaz/Nexum-Core/storage/scripts/monitor_nexum.py`
  * **Hermes Cron Job:** A scheduled cron job named `Nexum Self-Healing Monitor` is registered to run this script every 30 minutes (with repeat set to 999999). If any failure occurs (non-zero exit), the running agent autonomously uses terminal/file tools to resolve the issue (e.g. running `pm2 delete all && pm2 start ecosystem.config.js` to clear stale environments, or patching code/configs) and posts a detailed Arabic diagnostic and repair report to the log channel `-1003969021809`. If all is well, a clean heartbeat is sent.

## Troubleshooting
- **GCP Authentication:** If Vertex AI fails (with errors like `401 UNAUTHENTICATED` or `404 NOT_FOUND`), ensure `GOOGLE_APPLICATION_CREDENTIALS` points to the correct JSON key in `storage/gcp_key.json`, and **explicitly set** `GOOGLE_CLOUD_PROJECT` to the project ID (e.g., `mytest-496209`) and `GOOGLE_CLOUD_LOCATION` to a valid region (e.g., `us-central1`) in `.env`. Do NOT use `global` as the location for Vertex AI Gemini models as it will fail.
- **Gemini Model Deprecation & Selection:** Legacy model configurations or simulated future names (like `gemini-3.5-flash`) may fail with `404 NOT_FOUND` on Google Vertex AI. The actual active and accessible model in the user's regional GCP project (e.g., `us-central1`) is **`gemini-2.5-flash`**. Ensure `.env` files specify active, validated model names. After editing `.env` files, **always restart PM2 services with the `--update-env` flag** (e.g., `pm2 restart all --update-env`) to force PM2 to reload the new environment variables; a normal restart will NOT load the new `.env` settings.
- **PM2 Environment Inheritance Quirk (Stale Environment):** When launching or restarting PM2 processes from an active agent session (like Hermes), the PM2 process inherits the shell's active environment variables (such as `GEMINI_MODEL=gemini-3.5-flash`). Because standard `load_dotenv()` and Pydantic `BaseSettings` prioritize pre-existing environment variables over `.env` files by default, Nexum-Core will run with the stale inherited models rather than the `.env` values. To resolve this, ensure `load_dotenv` is called with `override=True` in critical configuration files (`config_loader.py`, `nexum/config.py`, `core/llm_factory.py`, `services/gemini_service.py`) to force prioritizing the local `.env` settings. If environment variables are still stale, run `pm2 delete all && pm2 start ecosystem.config.js` to completely flush and rebuild the process environment.
- **google-genai Client Quirk:** In the `google-genai` library, passing both `api_key` and explicit `project`/`location` parameters to the `genai.Client` constructor with `vertexai=True` raises a fatal exception: `Project/location and API key are mutually exclusive in the client initializer`. To avoid this, either initialize with `genai.Client(vertexai=True, api_key=api_key)` (letting the API key determine project/location automatically), or use the standard ADC mode without `api_key` by setting the environment variables `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` and initializing with `genai.Client(http_options=HttpOptions(api_version="v1"))`.
- **Python 3.11 f-string Compatibility:** Python 3.11 does not support backslashes inside f-string expressions (e.g., `f"{x.replace('\"', '\\\"')}"` will raise `SyntaxError`). This can break startup or silently fail tool registration (e.g., in `core/sandbox.py`). Always extract formatting/replacements with backslashes into a local variable before using them in f-strings.
- **System Python vs Virtual Environment (PM2):** PM2 processes might run under system-wide `python3` instead of the venv Python. Ensure critical third-party libraries (such as `supabase`) are installed both in the virtual environment and system-wide (using `pip3 install --user <pkg> --break-system-packages` if PEP 668 is active) to prevent `ModuleNotFoundError` during PM2 startup.
- **HMAC Issues:** Ensure `SOVEREIGN_HMAC_KEY` is set in `.env` for production audit integrity.
- **Sentinel Failures:** Check `storage/logs/sentinel.log` for self-healing repair history.
- **Go Version Mismatches in `go.mod`:** If the Go compiler version is older than the one specified in `core/go.mod` (or if it specifies a 3-digit patch version like `1.26.3` which is invalid in `go.mod`), Go builds will fail with parsing errors. Ensure `core/go.mod` uses `go 1.19` or matches the major.minor of the host's Go version (check with `go version`).
- **Telegram Bot Token Environment Keys:** Some bots look for `TELEGRAM_BOT_TOKEN` while the core uses `TELEGRAM_TOKEN` in `.env`. Ensure scripts support both keys with a fallback: `os.getenv("TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")`.
- **Python Path Resolution in Bots/Scripts:** PM2 services or standalone scripts running inside subfolders (e.g., `storage/templates/bots/`) may throw `ModuleNotFoundError: No module named 'nexum'`. Always inject the project root path at the top of the script: `import sys; sys.path.insert(0, "/home/madarmutaz/Nexum-Core")`.
- **Hanging/Timeouts in Memory/Codebase Indexers:** File indexers that use `os.walk` to traverse the codebase can hang or trigger execution timeouts if they descend into heavy directories like `venv`, `.git`, `__pycache__`, `.pytest_cache`, `.claude`, `home`, or nested duplicate projects. Always prune the `dirs` list in-place during `os.walk` (e.g., `dirs[:] = [d for d in dirs if d not in ignore_dirs]`) to prevent traversing them, and run the indexer with the appropriate python path (e.g., `PYTHONPATH=. python3 nexum/memory/indexer.py`).
- **Pytest Duplicate Projects & Collection Failures:** If a duplicate nested repository folder exists (e.g., `/home/madarmutaz/Nexum-Core/Nexum-Core`), running pytest globally will cause file-mismatch collection errors (e.g. `import file mismatch` between `/home/madarmutaz/Nexum-Core/tests/` and `/home/madarmutaz/Nexum-Core/Nexum-Core/tests/`). Fix this by explicitly ignoring the nested repository path: `pytest /home/madarmutaz/Nexum-Core/tests --ignore=/home/madarmutaz/Nexum-Core/Nexum-Core`.
- **Async Test Failures & Pytest-Asyncio Plugin:** Running the global `pytest` command may fail async tests with `async def functions are not natively supported` due to the lack of the `pytest-asyncio` plugin in the global python environment. Always use the project's virtual environment pytest binary to run tests: `/home/madarmutaz/Nexum-Core/venv/bin/pytest <args>`.
- **Rigid Model Assertions in Integration Tests:** Tests checking model status (e.g. `test_agent_platform.py`) might assert specific names like `gemini-3.5-flash` while `.env` is configured to `gemini-2.5-flash`. Update test assertions to tolerate configured defaults (e.g., `assert model in ['gemini-3.5-flash', 'gemini-2.5-flash']`) to prevent environment-specific test failures.
- **409 Conflict on Telegram Bot Token:** Running multiple processes that use `bot.infinity_polling()` with the same `TELEGRAM_TOKEN` (such as running both `telegram_summarizer_bot.py` and `main.py` simultaneously) will result in a `telebot.apihelper.ApiTelegramException: Error code: 409 ... Conflict: terminated by other getUpdates request` crash loop. Sub-bots must use distinct tokens or be integrated directly within the main `main.py` polling thread.
- **Channel Post vs Message Handlers:** The main Nexum bot (`main.py`) only registers `@bot.message_handler` for direct or group messages, completely ignoring channel posts. If Nexum needs to respond to posts made inside channels, `@bot.channel_post_handler` handlers must be added to the code.
- **Hourly Pulse / Heartbeat Missing:** If the log channel (e.g., `Mutaz live` or `Agent lap 🧪`) is silent and not receiving hourly notifications, ensure the `nexum-chronos` process is running in PM2: `pm2 start /home/madarmutaz/Nexum-Core/agents/chronos.py --name nexum-chronos --interpreter /home/madarmutaz/Nexum-Core/venv/bin/python3`. Save the process list afterwards via `pm2 save`.

## References
- `references/gcp-mcp-operational-protocols.md` — بروتوكولات التشغيل لـ GCP MCP وقدرات الحوسبة السحابية والأتمتة المبنية على الأحداث.
- `references/gcp-simulation-mode.md` — دليل التعامل مع وضع المحاكاة في الموصل السحابي (Simulation Mode).
- `references/gcp-vertex-ai-regional-setup.md` — دليل الربط الإقليمي ومحددات البيئة لخدمة Vertex AI Gemini ($1,000 credit).
- `references/sovereign-gateway-security.md` — Implementation details on HMAC-SHA256 log signing and path traversal mitigation.
- `references/memory-indexing-optimization.md` — Performance guide and troubleshooting for codebase and operational log indexing (handling os.walk hanging).
- `references/secure-browser-sandbox.md` — دليل وإجراءات تشغيل متصفح الطيران الآمن المعزول وتطبيق معايير AAA الأربعة وسجلات HMAC المقاومة للتلاعب.
- `scripts/monitor_nexum.py` — سكربت الرقابة والترميم الذاتي للأنظمة واتصال غوغل السحابي و PM2.
