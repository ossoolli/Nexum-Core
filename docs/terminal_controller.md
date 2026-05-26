# Terminal Controller Documentation

## Overview
`core/terminal_controller.py` implements a **secure, asynchronous terminal execution layer** for the Nexum‑Core platform. It provides:
- **Command validation** using regex patterns for forbidden and sensitive commands.
- **Structured JSON logging** with log rotation via `pythonjsonlogger`.
- **Async execution** (`execute_async`) that runs commands in a subprocess without `shell=True` and respects time‑outs.
- A **synchronous wrapper** (`execute`) for backward‑compatibility with existing code.
- **Statistics** (`get_stats`) for execution counts and blocked commands.

## Key Classes & Functions
- `CommandValidationError` – custom exception raised when a command fails validation.
- `SovereignTerminalController`
  - `validate_command(command: str) -> dict` – returns a dict with `safe`, `level`, and `reason`.
  - `execute_async(command: str, cwd: str = None, timeout: int = None, skip_validation: bool = False) -> dict` – runs the command asynchronously, logs before/after execution, and returns a result dict.
  - `execute(command: str, cwd: str = None, timeout: int = None, skip_validation: bool = False) -> dict` – synchronous convenience method.
  - `get_stats() -> dict` – execution statistics.
- Module‑level singleton `terminal_controller` for easy import.

## Logging
Logs are written to `storage/logs/terminal.log` in **JSON** format, rotated after 10 MB (5 backups). Example log entry:
```json
{"asctime": "2026-05-26T19:22:00Z", "levelname": "INFO", "message": "EXECUTING: echo hello | cwd=/app | timeout=45s"}
```

## Security Model
- **FORBIDDEN_REGEX** – commands that are never allowed (e.g., `rm -rf /`, `mkfs`).
- **SENSITIVE_REGEX** – commands that require additional approval in higher‑level workflows.
- Validation is performed **before** any subprocess is spawned.

## Usage Example
```python
from core.terminal_controller import terminal_controller

result = terminal_controller.execute("echo hello")
print(result["output"])  # => "hello"
```

## Extending/Modifying
1. **Add new patterns** – Append compiled regex to `FORBIDDEN_REGEX` or `SENSITIVE_REGEX`.
2. **Change logging** – Adjust `RotatingFileHandler` parameters or formatter.
3. **Adjust defaults** – Change `default_cwd` or `default_timeout` via the class constructor.

---
*Documentation generated on 2026‑05‑26.*
