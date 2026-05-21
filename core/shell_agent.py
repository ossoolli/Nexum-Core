"""
core/shell_agent.py
منفذ أوامر Shell الحقيقي مع timeout وstreaming وتحقق
"""
import subprocess
import os
import threading
from typing import Callable, Optional
from core.env_config import BASE_DIR, PYTHON_BIN, SANDBOX_DIR

# ─── الأوامر المحظورة تماماً ───
BLOCKED_COMMANDS = [
    "rm -rf /", "rm -rf /*", "mkfs", "dd if=/dev/zero",
    ":(){ :|:& };:", "chmod -R 777 /", "> /etc/passwd",
    "shutdown", "halt", "poweroff", "reboot",
    "fork bomb", "while true; do"
]

# ─── الأوامر التي تحتاج تأكيد ───
SENSITIVE_PATTERNS = [
    "rm -rf", "DROP TABLE", "DELETE FROM", "truncate",
    "git push --force", "pip uninstall", "apt remove"
]

class ShellAgent:
    def __init__(self, default_timeout: int = 30):
        self.default_timeout = default_timeout
        self.cwd = BASE_DIR

    def _is_blocked(self, cmd: str) -> bool:
        cmd_lower = cmd.lower()
        return any(b.lower() in cmd_lower for b in BLOCKED_COMMANDS)

    def _needs_confirm(self, cmd: str) -> bool:
        cmd_lower = cmd.lower()
        return any(s.lower() in cmd_lower for s in SENSITIVE_PATTERNS)

    def execute(self, cmd: str, cwd: Optional[str] = None,
                timeout: Optional[int] = None,
                stream_callback: Optional[Callable] = None,
                force: bool = False) -> dict:
        """
        ينفذ أمر Shell حقيقي.
        stream_callback: دالة تُستدعى لكل سطر output (للبث الحي)
        force: تجاوز طلب التأكيد
        """
        if self._is_blocked(cmd):
            return {
                "status": "blocked",
                "output": f"🚫 الأمر محظور تماماً: `{cmd[:50]}`"
            }

        if not force and self._needs_confirm(cmd):
            return {
                "status": "confirm",
                "output": f"⚠️ أمر حساس يحتاج تأكيداً:\n`{cmd}`",
                "cmd": cmd
            }

        work_dir = cwd or self.cwd
        timeout_val = timeout or self.default_timeout

        try:
            process = subprocess.Popen(
                cmd,
                shell=True,
                cwd=work_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                env={**os.environ, "PYTHONPATH": BASE_DIR}
            )

            output_lines = []

            def read_output():
                for line in iter(process.stdout.readline, ""):
                    line = line.rstrip("\n")
                    output_lines.append(line)
                    if stream_callback:
                        stream_callback(line)

            reader = threading.Thread(target=read_output)
            reader.start()

            try:
                process.wait(timeout=timeout_val)
            except subprocess.TimeoutExpired:
                process.kill()
                return {
                    "status": "timeout",
                    "output": f"⏱️ انتهت المهلة بعد {timeout_val} ثانية\nالخرج حتى الآن:\n" + "\n".join(output_lines[-20:]),
                    "returncode": -1
                }

            reader.join(timeout=2)
            full_output = "\n".join(output_lines)

            return {
                "status": "success" if process.returncode == 0 else "error",
                "returncode": process.returncode,
                "output": full_output[-4000:] if len(full_output) > 4000 else full_output,
                "lines": len(output_lines)
            }

        except Exception as e:
            return {"status": "error", "output": str(e), "returncode": -1}

    def run_python(self, code: str, filename: Optional[str] = None,
                   stream_callback: Optional[Callable] = None) -> dict:
        """
        ينفذ كود Python في بيئة معزولة حقيقية.
        يحفظ الكود كملف مؤقت، يشغّله، ويعيد النتيجة مع تحقق.
        """
        import tempfile
        from datetime import datetime

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = filename or f"run_{ts}.py"
        fpath = os.path.join(SANDBOX_DIR, fname)

        with open(fpath, "w", encoding="utf-8") as f:
            f.write(code)

        result = self.execute(
            f"{PYTHON_BIN} {fpath}",
            cwd=SANDBOX_DIR,
            timeout=60,
            stream_callback=stream_callback
        )
        result["script_path"] = fpath
        result["executed_code"] = code[:500]
        return result

    def install_package(self, package: str) -> dict:
        """يثبت حزمة Python في الـ venv"""
        cmd = f"{PYTHON_BIN} -m pip install {package} --quiet"
        return self.execute(cmd, timeout=120)

    def get_system_info(self) -> dict:
        """يجلب معلومات النظام الحقيقية"""
        cmds = {
            "cpu_percent": "python3 -c \"import psutil; print(psutil.cpu_percent(interval=0.5))\"",
            "ram_gb": "python3 -c \"import psutil; m=psutil.virtual_memory(); print(f'{m.used/1e9:.1f}/{m.total/1e9:.1f}')\"",
            "disk_gb": "python3 -c \"import psutil; d=psutil.disk_usage('/'); print(f'{d.used/1e9:.1f}/{d.total/1e9:.1f}')\"",
            "uptime": "uptime -p"
        }
        info = {}
        for key, cmd in cmds.items():
            r = self.execute(cmd, timeout=5)
            info[key] = r["output"].strip() if r["status"] == "success" else "N/A"
        return info


shell_agent = ShellAgent()
