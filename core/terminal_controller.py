# -*- coding: utf-8 -*-
"""
core/terminal_controller.py
المتحكم الأمني الموحد بأوامر الترمنال -- Nexum Pro (v7.2.5)
============================================================
- قائمة أوامر محظورة أمنيا (Forbidden Commands) لحماية السيرفر من التدمير
- تنفيذ معزول عبر subprocess مع Timeout وCwd isolation
- تدقيق كامل: كل أمر يُسجل في storage/logs/terminal.log
- تكامل مع DelegationEngine و TrustEngine
"""

import os
import subprocess
import logging
import threading
import shlex
import asyncio
import re
from datetime import datetime
from typing import Optional
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, "storage", "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# إعداد سجل التدقيق
_audit_logger = logging.getLogger("nexum.terminal")
_audit_logger.setLevel(logging.DEBUG)
if not _audit_logger.handlers:
    _fh = RotatingFileHandler(
        os.path.join(LOGS_DIR, "terminal.log"),
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    _formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s')
    _fh.setFormatter(_formatter)
    _audit_logger.addHandler(_fh)


class CommandValidationError(Exception):
    """Exception raised when a command fails validation."""
    pass


def _log_event(level: int, message: str) -> None:
    """Helper to emit a structured log entry.

    Args:
        level: Logging level (e.g., logging.INFO).
        message: Log message.
    """
    _audit_logger.log(level, message)


class SovereignTerminalController:
    """المتحكم الأمني الموحد بأوامر الترمنال.

    Provides secure command validation, async execution, and structured JSON logging.
    """

    # قائمة الأوامر المحظورة أمنيا -- لا يسمح بتنفيذها أبدا (Regex مع حدود الكلمات)
    FORBIDDEN_REGEX = [
        re.compile(r"\brm\s+-rf\s+\/\b", re.IGNORECASE),
        re.compile(r"\brm\s+-rf\s+\/\*\b", re.IGNORECASE),
        re.compile(r"\bmkfs\b", re.IGNORECASE),
        re.compile(r"\bshutdown\b", re.IGNORECASE),
        re.compile(r"\breboot\b", re.IGNORECASE),
        re.compile(r"dd\s+if=", re.IGNORECASE),
        re.compile(r":\(\)\{\s*:\s*\|\s*:\s*;\s*\}\s*;\s*:", re.IGNORECASE),
        re.compile(r"chmod\s+777\s+\/", re.IGNORECASE),
        re.compile(r"chown\s+root", re.IGNORECASE),
        re.compile(r">\s+\/dev\/sda", re.IGNORECASE),
        re.compile(r"mv\s+\/", re.IGNORECASE),
        re.compile(r"rm\s+-rf\s+\.", re.IGNORECASE),
        re.compile(r"format\s+c:\\", re.IGNORECASE),
        re.compile(r"del\s+/f\s+/s\s+/q\s+c:\\", re.IGNORECASE),
        re.compile(r"rd\s+/s\s+/q\s+c:\\", re.IGNORECASE),
    ]

    # أوامر تحتاج تأكيد إضافي (لا تُحظر لكن تُرفع للمراجعة)
    SENSITIVE_REGEX = [
        re.compile(r"\brm\s+", re.IGNORECASE),
        re.compile(r"delete", re.IGNORECASE),
        re.compile(r"drop", re.IGNORECASE),
        re.compile(r"sudo", re.IGNORECASE),
        re.compile(r"kill", re.IGNORECASE),
        re.compile(r"git\s+push\s+--force", re.IGNORECASE),
        re.compile(r"git\s+reset\s+--hard", re.IGNORECASE),
        re.compile(r"pip\s+uninstall", re.IGNORECASE),
        re.compile(r"npm\s+uninstall", re.IGNORECASE),
        re.compile(r"truncate", re.IGNORECASE),
        re.compile(r"ufw", re.IGNORECASE),
        re.compile(r"iptables", re.IGNORECASE),
    ]

    def __init__(self, default_cwd: str = None, default_timeout: int = 45):
        self.default_cwd = default_cwd or BASE_DIR
        self.default_timeout = default_timeout
        self._lock = threading.Lock()
        self._execution_count = 0
        self._blocked_count = 0
        self.lockdown_mode = False  # Persistent forced Open Mode
        self.lockdown_mode = False

    def validate_command(self, command: str) -> dict:
        """فحص أمني مسبق للأمر قبل التنفيذ باستخدام regex."""
        cmd = command.strip()
        cmd_lower = cmd.lower()

        # 1. فحص الأوامر المحظورة عبر regex
        for pattern in self.FORBIDDEN_REGEX:
            if pattern.search(cmd_lower):
                _audit_logger.warning(f"BLOCKED forbidden command: {command}")
                self._blocked_count += 1
                return {
                    "safe": False,
                    "level": "FORBIDDEN",
                    "reason": f"Command matches forbidden pattern: '{pattern.pattern}'",
                }

        # 2. فحص الأوامر الحساسة عبر regex
        for pattern in self.SENSITIVE_REGEX:
            if pattern.search(cmd_lower):
                return {
                    "safe": True,
                    "level": "SENSITIVE",
                    "reason": f"Command matches sensitive pattern: '{pattern.pattern}'. Requires elevated approval.",
                }

        # 3. آمن
        return {
            "safe": True,
            "level": "SAFE",
            "reason": "Command passed all security checks.",
        }

    async def execute_async(self, command: str, cwd: str = None,
                         timeout: int = None, skip_validation: bool = False) -> dict:
        """تنفيذ أمر نظام بشكل غير متزامن مع تدقيق كامل."""
        if not command or not command.strip():
            return {
                "success": False,
                "output": "Empty command provided.",
                "return_code": -1,
                "blocked": True,
            }

        # Check Lockdown Mode
        if getattr(self, "lockdown_mode", False):
            return {
                "success": False,
                "output": "🚨 ERROR: System is in Lockdown Mode. Remote execution is strictly prohibited.",
                "return_code": -1,
                "blocked": True,
            }

        # 1. التحقق الأمني
        if not skip_validation:
            validation = self.validate_command(command)
            if not validation["safe"]:
                _audit_logger.warning(
                    f"EXECUTION DENIED: {command} | Reason: {validation['reason']}"
                )
                return {
                    "success": False,
                    "output": validation["reason"],
                    "return_code": -1,
                    "blocked": True,
                    "validation": validation,
                }

        effective_cwd = cwd or self.default_cwd
        effective_timeout = timeout or self.default_timeout

        # 2. تسجيل قبل التنفيذ
        _audit_logger.info(
            f"EXECUTING: {command} | cwd={effective_cwd} | timeout={effective_timeout}s"
        )

        # 3. التنفيذ المعزول بإستخدام asyncio
        try:
            async with asyncio.Semaphore():
                # Increment execution count safely
                with self._lock:
                    self._execution_count += 1

            # تجزئة الأمر لتقليل الاعتماد على shell إذا كان ممكنًا
            cmd_list = shlex.split(command)
            proc = await asyncio.create_subprocess_exec(
                *cmd_list,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=effective_cwd,
            )
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=effective_timeout)
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                _audit_logger.error(
                    f"TIMEOUT: Command timed out after {effective_timeout}s: {command[:80]}"
                )
                return {
                    "success": False,
                    "output": f"Command timed out after {effective_timeout}s.",
                    "return_code": -1,
                    "blocked": False,
                }

            output = stdout.decode().strip() if stdout else stderr.decode().strip()
            success = proc.returncode == 0

            # 4. تسجيل بعد التنفيذ
            _audit_logger.log(
                logging.INFO if success else logging.WARNING,
                f"RESULT: rc={proc.returncode} | output_len={len(output)} | cmd={command[:80]}"
            )

            return {
                "success": success,
                "output": output or "Executed successfully (no output).",
                "return_code": proc.returncode,
                "blocked": False,
            }
        except Exception as e:
            _audit_logger.error(f"ERROR: {e} | cmd={command[:80]}")
            return {
                "success": False,
                "output": str(e),
                "return_code": -1,
                "blocked": False,
            }

    def execute(self, command: str, cwd: str = None,
                timeout: int = None, skip_validation: bool = False) -> dict:
        """واجهة متزامنة تحافظ على التوافق مع الكود الموجود،
        تستدعي `execute_async` باستخدام asyncio.run إذا لم يكن داخل loop."""
        try:
            # إذا تم استدعاؤه من داخل حدث asyncio، نستخدم create_task
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # لا يوجد حلقة جارية؛ نستدعي مباشرة
            return asyncio.run(self.execute_async(command, cwd, timeout, skip_validation))
        else:
            # داخل حلقة asyncio، نعيد مهمة coroutine
            return asyncio.create_task(self.execute_async(command, cwd, timeout, skip_validation))

    def get_stats(self) -> dict:
        """إحصائيات التنفيذ."""
        return {
            "total_executions": self._execution_count,
            "blocked_commands": self._blocked_count,
            "default_timeout": self.default_timeout,
            "default_cwd": self.default_cwd
        }


# Singleton
terminal_controller = SovereignTerminalController()
