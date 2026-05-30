import sys
import os
# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from typing import Optional
from core.sovereign_execution_gateway import read_file as gateway_read_file, write_file as gateway_write_file, secure_log, validate_path

def read_file(path: str) -> str:
    return gateway_read_file(path)

def write_file(path: str, content: str) -> None:
    gateway_write_file(path, content)

def patch(path: str, old_string: str, new_string: str) -> None:
    """
    Performs targeted find-and-replace.
    """
    resolved_path = validate_path(path)
    content = read_file(path)
    if old_string not in content:
        raise ValueError(f"Target string not found in {path}")
    new_content = content.replace(old_string, new_string)
    write_file(path, new_content)
    secure_log("patch", {"path": path}, "success")

def search_files(pattern: str) -> list:
    """
    Finds files and content.
    """
    import subprocess
    # Using grep for searching content
    result = subprocess.run(["grep", "-r", pattern, "."], capture_output=True, text=True)
    secure_log("search_files", {"pattern": pattern}, "success")
    return result.stdout.splitlines()
