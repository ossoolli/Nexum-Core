import os
import sys
import json
from core.sovereign_execution_gateway import execute_command, verify_audit_log

# Add path
sys.path.append("/home/madarmutaz/Nexum-Core")

print("--- 1. Testing Terminal Command Execution (ls /tmp) ---")
try:
    result = execute_command("ls /tmp")
    print(f"Result: {result['status']}")
    print(f"STDOUT: {result['stdout']}")
except Exception as e:
    print(f"Error: {e}")

print("\n--- 2. Testing Python Code Execution ---")
# Using a small snippet directly in the sandbox_runs area
code_content = "print('Hello from Sandboxed Python')"
run_file = "/home/madarmutaz/Nexum-Core/workspace/test_run.py"

# Manually create it for this test
with open(run_file, "w") as f:
    f.write(code_content)

try:
    result = execute_command(f"python3 {run_file}")
    print(f"Result: {result['status']}")
    print(f"STDOUT: {result['stdout']}")
except Exception as e:
    print(f"Error: {e}")

print("\n--- 3. Verifying Audit Logs and HMAC ---")
if verify_audit_log():
    print("✅ Audit log integrity verified successfully.")
else:
    print("❌ Audit log verification FAILED.")
