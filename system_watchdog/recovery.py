# -*- coding: utf-8 -*-
"""
watchdog/recovery.py
مدير الاستعادة والإصلاح الذاتي -- Nexum Pro (v7.2.5)
=====================================================
- Exponential Backoff: 5s -> 15s -> 30s -> 60s
- استعادة آخر حالة مستقرة للذاكرة السيادية
- تنظيف السياق المتلف (Context Flush)
- إشعار المسؤول عبر Telegram
- وضع الأمان (Safe Mode) بعد 5 أعطال متتالية
"""

import os
import time
import logging
import threading
from datetime import datetime
from typing import Optional, Callable

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_recovery_logger = logging.getLogger("nexum.recovery")
_recovery_logger.setLevel(logging.DEBUG)
if not _recovery_logger.handlers:
    _log_dir = os.path.join(BASE_DIR, "storage", "logs")
    os.makedirs(_log_dir, exist_ok=True)
    _fh = logging.FileHandler(
        os.path.join(_log_dir, "recovery.log"), encoding="utf-8"
    )
    _fh.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    ))
    _recovery_logger.addHandler(_fh)


class RecoveryManager:
    """مدير الاستعادة والإصلاح الذاتي مع تراجع أسي."""

    # مصفوفة التراجع الأسي (بالثواني)
    BACKOFF_DELAYS = [5, 15, 30, 60, 120]

    def __init__(self, max_retries: int = 5, bot=None, admin_id: int = None):
        self.max_retries = max_retries
        self.bot = bot
        self.admin_id = admin_id

        self._lock = threading.Lock()
        self._retry_count = 0
        self._in_safe_mode = False
        self._recovery_history = []

    @property
    def is_safe_mode(self) -> bool:
        return self._in_safe_mode

    def get_backoff_delay(self, attempt: int) -> int:
        """حساب مهلة التراجع الأسي."""
        if attempt < len(self.BACKOFF_DELAYS):
            return self.BACKOFF_DELAYS[attempt]
        return self.BACKOFF_DELAYS[-1]

    def handle_failure(self, health_report: dict,
                       consecutive_failures: int) -> dict:
        """معالجة عطل مرصود من الحارس."""
        with self._lock:
            self._retry_count = consecutive_failures

            failed_checks = [
                name for name, result in health_report.get("checks", {}).items()
                if not result.get("healthy")
            ]

            _recovery_logger.warning(
                f"Handling failure #{consecutive_failures}. "
                f"Failed: {failed_checks}"
            )

            recovery_result = {
                "attempt": consecutive_failures,
                "timestamp": datetime.now().isoformat(),
                "failed_checks": failed_checks,
                "actions_taken": []
            }

            # 1. محاولة إصلاح بسيطة (< 3 أعطال)
            if consecutive_failures <= 2:
                recovery_result["actions_taken"].append("context_flush")
                self._flush_context()

            # 2. محاولة استعادة عميقة (3-4 أعطال)
            elif consecutive_failures <= 4:
                recovery_result["actions_taken"].extend([
                    "context_flush", "memory_reload"
                ])
                self._flush_context()
                self._reload_memory()

            # 3. وضع الأمان (>= 5 أعطال)
            if consecutive_failures >= self.max_retries:
                recovery_result["actions_taken"].append("safe_mode_activated")
                self._enter_safe_mode()

            # تطبيق التراجع الأسي
            delay = self.get_backoff_delay(consecutive_failures - 1)
            recovery_result["backoff_delay"] = delay
            recovery_result["actions_taken"].append(
                f"exponential_backoff_{delay}s"
            )

            # تسجيل في التاريخ
            self._recovery_history.append(recovery_result)
            if len(self._recovery_history) > 20:
                self._recovery_history.pop(0)

            # إشعار المسؤول
            self._notify_admin(recovery_result)

            return recovery_result

    def handle_critical(self, health_report: dict) -> dict:
        """معالجة الحالة الحرجة -- تفعيل وضع الأمان الكامل."""
        _recovery_logger.critical("CRITICAL STATE REACHED!")

        self._enter_safe_mode()
        self._flush_context()
        self._reload_memory()

        result = {
            "timestamp": datetime.now().isoformat(),
            "action": "CRITICAL_RECOVERY",
            "safe_mode": True,
            "message": "System entered SAFE MODE. All autonomous actions suspended."
        }

        self._notify_admin(result, critical=True)
        return result

    def handle_recovery(self, health_report: dict) -> dict:
        """معالجة تعافي النظام بعد عطل."""
        with self._lock:
            self._retry_count = 0

            if self._in_safe_mode:
                _recovery_logger.info(
                    "System recovered from safe mode. "
                    "Returning to normal operation."
                )
                self._in_safe_mode = False

            result = {
                "timestamp": datetime.now().isoformat(),
                "action": "RECOVERY_CONFIRMED",
                "safe_mode": False,
                "message": "System recovered and operating normally."
            }

            self._notify_admin(result, recovery=True)
            return result

    def _flush_context(self) -> None:
        """تنظيف السياق المتلف لمنع هجمات حقن السياق."""
        try:
            from core.memory_local import context_memory
            # تنظيف كل السياقات المؤقتة
            context_memory.clear_all()
            _recovery_logger.info("Context flush completed.")
        except Exception as e:
            _recovery_logger.error(f"Context flush failed: {e}")

    def _reload_memory(self) -> None:
        """إعادة تحميل الذاكرة السيادية من آخر حالة مستقرة."""
        try:
            from core.memory.sovereign_memory import SovereignMemory
            mem_path = os.path.join(BASE_DIR, "storage", "sovereign_memory")
            # إعادة التحميل تقرأ آخر ملفات JSON محفوظة ذريا
            _ = SovereignMemory(mem_path)
            _recovery_logger.info("Sovereign memory reloaded from last stable state.")
        except Exception as e:
            _recovery_logger.error(f"Memory reload failed: {e}")

    def _enter_safe_mode(self) -> None:
        """تفعيل وضع الأمان -- تعليق كل العمليات المستقلة."""
        self._in_safe_mode = True
        _recovery_logger.critical(
            "SAFE MODE ACTIVATED. All autonomous actions suspended."
        )

        # محاولة خفض مستويات الثقة لوضع OBSERVE
        try:
            from core.memory.sovereign_memory import SovereignMemory
            mem = SovereignMemory(os.path.join(BASE_DIR, "storage", "sovereign_memory"))
            trust_matrix = mem.infrastructure.map.get("trust_matrix", {})
            for category in trust_matrix:
                if isinstance(trust_matrix[category], dict):
                    trust_matrix[category]["level"] = 0  # OBSERVE
                    trust_matrix[category]["score"] = 0.0
            mem.infrastructure.update_field("trust_matrix", trust_matrix)
            _recovery_logger.info("Trust levels reset to OBSERVE in safe mode.")
        except Exception as e:
            _recovery_logger.error(f"Trust reset failed: {e}")

    def _notify_admin(self, report: dict,
                      critical: bool = False, recovery: bool = False) -> None:
        """إشعار المسؤول عبر Telegram."""
        if not self.bot or not self.admin_id:
            return

        try:
            if critical:
                msg = (
                    "<b>[NEXUM CRITICAL]</b>\n"
                    "System entered SAFE MODE.\n"
                    f"<pre>{report.get('message', 'Critical state reached.')}</pre>"
                )
            elif recovery:
                msg = (
                    "<b>[NEXUM RECOVERY]</b>\n"
                    "System recovered and operating normally."
                )
            else:
                actions = ", ".join(report.get("actions_taken", []))
                msg = (
                    f"<b>[NEXUM WATCHDOG]</b>\n"
                    f"Failure #{report.get('attempt', '?')}\n"
                    f"Actions: {actions}\n"
                    f"Backoff: {report.get('backoff_delay', '?')}s"
                )

            self.bot.send_message(self.admin_id, msg, parse_mode="HTML")
        except Exception as e:
            _recovery_logger.error(f"Admin notification failed: {e}")

    def get_status(self) -> dict:
        """تقرير حالة مدير الاستعادة."""
        return {
            "safe_mode": self._in_safe_mode,
            "retry_count": self._retry_count,
            "max_retries": self.max_retries,
            "recovery_history_count": len(self._recovery_history),
            "last_recovery": (
                self._recovery_history[-1] if self._recovery_history else None
            )
        }
