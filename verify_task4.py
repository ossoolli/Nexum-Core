import os
import sys
import json
from core.sovereign_execution_gateway import execute_command, verify_audit_log

# Add path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

print("--- 1. Testing Terminal Command Execution (dir or ls) ---")
try:
    cmd = "dir" if os.name == "nt" else "ls /tmp"
    result = execute_command(cmd)
    print(f"Result: {result['status']}")
    print(f"STDOUT: {result['stdout']}")
except Exception as e:
    print(f"Error: {e}")

print("\n--- 2. Testing Python Code Execution ---")
# Using a small snippet directly in the sandbox_runs area
code_content = "print('Hello from Sandboxed Python')"
workspace_dir = os.path.join(project_dir, "workspace")
os.makedirs(workspace_dir, exist_ok=True)
run_file = os.path.join(workspace_dir, "test_run.py")

# Manually create it for this test
with open(run_file, "w") as f:
    f.write(code_content)

try:
    python_cmd = sys.executable
    result = execute_command(f"{python_cmd} {run_file}")
    print(f"Result: {result['status']}")
    print(f"STDOUT: {result['stdout']}")
except Exception as e:
    print(f"Error: {e}")

print("\n--- 3. Verifying Audit Logs and HMAC ---")
if verify_audit_log():
    print("✅ Audit log integrity verified successfully.")
else:
    print("❌ Audit log verification FAILED.")
