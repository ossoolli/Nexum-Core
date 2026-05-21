"""
core/verifier.py
يتحقق من أن العمليات حدثت فعلاً على القرص/النظام
"""
import os
import subprocess
from core.env_config import WORKSPACE_DIR, PROJECT_ROOT, PYTHON_BIN

class Verifier:
    def file_exists(self, path: str) -> bool:
        """يتحقق من وجود ملف بالمسار الحقيقي"""
        if os.path.isabs(path):
            return os.path.exists(path)
        for base in [WORKSPACE_DIR, PROJECT_ROOT]:
            if os.path.exists(os.path.join(base, path)):
                return True
        return False

    def file_contains(self, path: str, text: str) -> bool:
        """يتحقق أن ملفاً يحتوي على نص معين"""
        if not self.file_exists(path):
            return False
        real = path if os.path.isabs(path) else os.path.join(WORKSPACE_DIR, path)
        try:
            with open(real, "r", encoding="utf-8") as f:
                return text in f.read()
        except Exception:
            return False

    def python_syntax_ok(self, path: str) -> dict:
        """يتحقق من صحة syntax ملف Python"""
        real = path if os.path.isabs(path) else os.path.join(WORKSPACE_DIR, path)
        result = subprocess.run(
            [PYTHON_BIN, "-m", "py_compile", real],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return {"valid": True, "errors": None}
        return {"valid": False, "errors": result.stderr}

    def code_runs(self, path: str, expected_output: str = None, timeout: int = 10) -> dict:
        """يشغّل ملف Python ويتحقق من خرجه"""
        real = path if os.path.isabs(path) else os.path.join(WORKSPACE_DIR, path)
        syntax = self.python_syntax_ok(path)
        if not syntax["valid"]:
            return {"success": False, "stage": "syntax", "error": syntax["errors"]}

        result = subprocess.run(
            [PYTHON_BIN, real],
            capture_output=True, text=True, timeout=timeout
        )
        output = result.stdout + result.stderr
        success = result.returncode == 0

        if expected_output and expected_output not in output:
            return {
                "success": False,
                "stage": "output_mismatch",
                "expected": expected_output,
                "got": output[:200]
            }

        return {"success": success, "output": output[:500], "returncode": result.returncode}


verifier = Verifier()
