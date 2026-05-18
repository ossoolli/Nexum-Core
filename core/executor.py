import os
import subprocess
import html
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from core.security import validator

DANGEROUS_PATTERNS = ["rm -rf /", "mkfs", "dd if=", "reboot", "shutdown"]

class TaskExecutor:
    def __init__(self, timeout=60):
        self.timeout = timeout

    def execute(self, command, force=False) -> dict:
        # فحص الأمان
        allowed, reason = validator.is_safe(command)
        if not allowed:
            return {'status': 'blocked', 'output': '🚫 أمر محظور أمنياً.'}
        if reason == 'confirm' and not force:
            return {'status': 'confirm', 'output': command}

        try:
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                executable='/bin/bash'
            )
            raw = process.stdout + process.stderr
            output = html.escape(raw) if raw else '✅ Done.'
            return {
                'status': 'success' if process.returncode == 0 else 'failed',
                'output': output[:3500]
            }
        except subprocess.TimeoutExpired:
            return {'status': 'timeout', 'output': f'⏳ انتهت المهلة ({self.timeout}s).'}
        except Exception as e:
            return {'status': 'error', 'output': str(e)}

    def validate_command(self, cmd):
        """توافق مع security.py القديم"""
        allowed, reason = validator.is_safe(cmd)
        if not allowed:
            return False, "🚫 أمر محظور."
        if reason == 'confirm':
            return True, "⚠️ أمر يحتاج تأكيداً."
        return True, "✅"

executor = TaskExecutor()
