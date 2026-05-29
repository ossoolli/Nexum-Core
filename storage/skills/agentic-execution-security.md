---
name: agentic-execution-security
description: Hardening runtime execution environments and preventing path traversal, command injection, and log tampering in autonomous agents.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  tags: [security, sandboxing, agentic-security, hmac, path-traversal, command-injection, audit-logs]
---

# Agentic Execution Security & Sandboxing

Autonomous AI agents often require system access to execute code, run shell commands, or manage files. If left unhardened, this access presents critical security vulnerabilities. This skill outlines the essential security paradigms for constructing secure, jailed execution gateways for autonomous agents.

## Core Pillars of Agentic Security

```
                     ┌───────────────────────────┐
                     │  Agent Request (Command)  │
                     └─────────────┬─────────────┘
                                   ▼
                   [ Sovereign Execution Gateway ]
                   ┌─────────────────────────────┐
                   │  1. Command Injection Filter│
                   ├─────────────────────────────┤
                   │  2. Binary Whitelist Match  │
                   ├─────────────────────────────┤
                   │  3. Path Traversal Guard    │
                   └─────────────┬─────────────┘
                                   ▼
                        ┌───────────────────┐
                        │ Secure Execution  │
                        └─────────┬─────────┘
                                  ▼
                     [ Tamper-Proof Audit Log ]
                     (HMAC-SHA256 Signed Chain)
```

### 1. Path Traversal Prevention (Chroot Jail Simulation)
Agents must be strictly confined to a designated workspace directory (`WORKSPACE_DIR`). Never rely on naive substring matching of path parameters (e.g. checking if a path starts with `/home/user`) as this can be easily bypassed using symlinks or relative sequences like `../../`.

**Implementation Pattern:**
Always resolve the absolute, canonical real paths of both the workspace and the target file using `os.path.realpath(os.path.abspath(...))` and then verify that the target lies entirely inside the workspace using `os.path.commonpath`.

```python
import os

def validate_path(user_path: str, workspace_dir: str) -> str:
    """Confines the resolved path strictly to the workspace directory.
    
    Prevents directory traversal bypasses on both Unix and Windows systems.
    """
    # Normalize Windows backslashes to forward slashes to prevent escape sequences
    normalized_user_path = user_path.replace("\\", "/")
    
    abs_workspace = os.path.realpath(os.path.abspath(workspace_dir))
    
    if not os.path.isabs(normalized_user_path):
        resolved_path = os.path.realpath(os.path.abspath(os.path.join(abs_workspace, normalized_user_path)))
    else:
        resolved_path = os.path.realpath(os.path.abspath(normalized_user_path))
        
    try:
        common = os.path.commonpath([abs_workspace, resolved_path])
    except ValueError as e:
        raise PermissionError(f"Access Denied: Path resides on a different drive: {user_path}") from e
        
    if common != abs_workspace:
        raise PermissionError(f"Directory Traversal Detected: {user_path}")
        
    return resolved_path
```

### 2. Command Injection Prevention & Whitelisting
Passing arbitrary shell strings to `os.system` or `subprocess.Popen(shell=True)` is extremely dangerous. Agents must be restricted to a strict whitelist of tools, and their parameters must be sanitized.

**Mitigation Protocol:**
- **No Raw Shell execution:** Never run commands with `shell=True`. Pass arguments as parsed tokens (lists of strings) instead.
- **shlex Parsing:** Use `shlex.split` (with Unix-like POSIX rules) to safely split user command strings.
- **Injection Filtering:** Scan command strings for shell special characters (`&`, `;`, `|`, `` ` ``, `$()`, `<`, `>`) and reject them.
- **Binary Whitelisting:** Match the first token of the parsed command against an explicit whitelist of allowed binaries (e.g. `git`, `python`, `pip`, `ls`).

```python
import shlex
import re
from typing import List

# Enforce a strict command whitelist
ALLOWED_BINARIES = {"git", "python", "python3", "pip", "pip3", "ls", "echo", "cat"}
INJECTION_PATTERN = re.compile(r"[;|`><]|&|\$\(")

def validate_command(command_str: str) -> List[str]:
    """Inspects a command string for shell injection, and matches the binary against a whitelist."""
    if INJECTION_PATTERN.search(command_str):
        raise PermissionError(f"Shell injection attempt detected in command: {command_str}")
        
    # Split using shlex to cleanly separate binary and parameters
    tokens = shlex.split(command_str)
    if not tokens:
        raise ValueError("Empty command string provided.")
        
    binary = tokens[0]
    if binary not in ALLOWED_BINARIES:
        raise PermissionError(f"Binary '{binary}' is not authorized in this jail environment.")
        
    return tokens
```

### 3. Tamper-Evident Auditing (Cryptographic Signature Chaining)
Audit logs must be cryptographically protected from tampering by the agent or any third party. If an agent manages to write or edit files, it should not be able to alter historical security logs without detection.

**HMAC-SHA256 Logging Pattern:**
- Each log entry must be serialized deterministically (e.g., sorting JSON keys).
- Sign each entry using an `HMAC-SHA256` signature using a secure secret key (`SOVEREIGN_HMAC_KEY`) stored exclusively in the environment (`.env`), never embedded as an insecure fallback string inside the source code.
- Prevent startup if the HMAC key is absent or insecure.
- Periodically verify the signature of every line in the log sequence. If any signature fails, sound an immediate security alarm.

```python
import hmac
import hashlib
import json
import os
import time
from typing import Dict, Any

HMAC_KEY = os.getenv("SOVEREIGN_HMAC_KEY")
if not HMAC_KEY or HMAC_KEY == "default_secret_key_for_tamper_proofing":
    raise ValueError(
        "CRITICAL SECURITY CONFIGURATION ERROR: SOVEREIGN_HMAC_KEY env var "
        "is not set, or is using an insecure default value."
    )

def sign_log(log_entry: Dict[str, Any]) -> str:
    """Signs a deterministic JSON string representation of a log entry."""
    serialized = json.dumps(log_entry, sort_keys=True)
    return hmac.new(
        HMAC_KEY.encode("utf-8"),
        serialized.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

def secure_log(action: str, details: Dict[str, Any], status: str, log_path: str) -> Dict[str, Any]:
    """Appends a cryptographically signed entry to the tamper-evident audit log."""
    log_entry = {
        "timestamp": time.time(),
        "action": action,
        "details": details,
        "status": status
    }
    log_entry["signature"] = sign_log(log_entry)
    
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
    return log_entry
```

### 4. Resilient & Silent Import Fallbacks
When agents load modules dynamically or rely on third-party libraries (like cloud SDKs), a missing package can cause critical startup crashes or fill the disk with repetitive tracebacks in error logs.

**Pattern for Resilient Imports:**
Wrap dynamic imports in a try-except block, logging warnings as clean, single-line `logger.info` or `logger.warning` statements (without full tracebacks) and initialize all missing modules and variables to `None`. This satisfies linters, prevents NameErrors under simulated fallbacks, and keeps log directories clean.

## Pitfalls to Avoid

- **Insecure fallbacks:** Never provide a fallback HMAC key string in code. Enforce environment configuration at module import time.
- **Naive substring path checks:** Always normalize both user paths and the workspace root (especially on Windows, handling backslashes) before applying `commonpath`.
- **Allowing pipe/redirect operators:** Operators like `>` and `|` bypass standard command filters and can invoke arbitrary shells. Block them completely.
