# -*- coding: utf-8 -*-
"""
watchdog/monitor.py
نظام فحص النبض والمراقبة التلقائية -- Nexum Pro (v7.2.5)
========================================================
- Heartbeat Monitor يعمل كخيط خلفي (Daemon Thread)
- يفحص صحة النواة والموديولات الحيوية كل N ثانية
- يسجل النبضات في storage/logs/watchdog.log
- ينشر أحداث النبض عبر EventBus
- يتتبع الأعطال المتتالية لتفعيل Exponential Backoff
"""

import os
import time
import threading
import logging
from datetime import datetime
from typing import Optional, Callable, Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, "storage", "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# إعداد سجل الحارس
_watchdog_logger = logging.getLogger("nexum.watchdog")
_watchdog_logger.setLevel(logging.DEBUG)
if not _watchdog_logger.handlers:
    _fh = logging.FileHandler(
        os.path.join(LOGS_DIR, "watchdog.log"), encoding="utf-8"
    )
    _fh.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    ))
    _watchdog_logger.addHandler(_fh)


class Watchdog:
    """نظام المراقبة المستقل مع نبض تلقائي ومعالجة أعطال."""

    def __init__(self, heartbeat_interval: int = 30, max_consecutive_failures: int = 5):
        self.heartbeat_interval = heartbeat_interval
        self.max_consecutive_failures = max_consecutive_failures

        # حالة النظام
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # عدادات النبض
        self._heartbeat_count = 0
        self._consecutive_failures = 0
        self._total_failures = 0
        self._last_heartbeat: Optional[str] = None
        self._last_failure: Optional[str] = None
        self._system_healthy = True

        # معالجات الأحداث
        self._on_failure_callback: Optional[Callable] = None
        self._on_recovery_callback: Optional[Callable] = None
        self._on_critical_callback: Optional[Callable] = None

        # فحوصات صحية مسجلة
        self._health_checks: Dict[str, Callable] = {}

        # تسجيل الفحوصات الأساسية
        self._register_core_checks()

    def _register_core_checks(self):
        """تسجيل فحوصات صحية لموديولات النواة."""

        def check_memory_module():
            try:
                from core.memory.sovereign_memory import SovereignMemory
                return True
            except Exception:
                return False

        def check_context_module():
            try:
                from core.context.context_engine import ContextEngine
                return True
            except Exception:
                return False

        def check_trust_module():
            try:
                from core.trust.trust_engine import TrustEngine
                return True
            except Exception:
                return False

        def check_storage_writable():
            try:
                test_path = os.path.join(BASE_DIR, "storage", ".watchdog_test")
                with open(test_path, "w") as f:
                    f.write("heartbeat")
                os.remove(test_path)
                return True
            except Exception:
                return False

        self._health_checks["memory_module"] = check_memory_module
        self._health_checks["context_module"] = check_context_module
        self._health_checks["trust_module"] = check_trust_module
        self._health_checks["storage_writable"] = check_storage_writable

    def register_health_check(self, name: str, check_fn: Callable) -> None:
        """تسجيل فحص صحي مخصص."""
        self._health_checks[name] = check_fn

    def set_callbacks(self, on_failure: Callable = None,
                      on_recovery: Callable = None,
                      on_critical: Callable = None) -> None:
        """تعيين معالجات أحداث الأعطال والاستعادة."""
        self._on_failure_callback = on_failure
        self._on_recovery_callback = on_recovery
        self._on_critical_callback = on_critical

    def check_health(self) -> dict:
        """تنفيذ جميع الفحوصات الصحية وإرجاع تقرير شامل."""
        results = {}
        all_healthy = True

        for name, check_fn in self._health_checks.items():
            try:
                healthy = check_fn()
                results[name] = {"healthy": healthy, "error": None}
                if not healthy:
                    all_healthy = False
            except Exception as e:
                results[name] = {"healthy": False, "error": str(e)}
                all_healthy = False

        return {
            "timestamp": datetime.now().isoformat(),
            "all_healthy": all_healthy,
            "checks": results,
            "heartbeat_count": self._heartbeat_count,
            "consecutive_failures": self._consecutive_failures
        }

    def _heartbeat_loop(self):
        """حلقة النبض الرئيسية -- تعمل كخيط خلفي."""
        _watchdog_logger.info(
            f"Watchdog started. Interval={self.heartbeat_interval}s, "
            f"Max failures={self.max_consecutive_failures}"
        )

        while self._running:
            try:
                time.sleep(self.heartbeat_interval)
                if not self._running:
                    break

                health = self.check_health()
                self._heartbeat_count += 1
                self._last_heartbeat = health["timestamp"]

                if health["all_healthy"]:
                    # نبض سليم
                    if not self._system_healthy:
                        # تعافي من عطل سابق
                        _watchdog_logger.info(
                            f"RECOVERY: System restored after "
                            f"{self._consecutive_failures} failures."
                        )
                        self._system_healthy = True
                        if self._on_recovery_callback:
                            try:
                                self._on_recovery_callback(health)
                            except Exception:
                                pass

                    self._consecutive_failures = 0
                    _watchdog_logger.debug(
                        f"HEARTBEAT #{self._heartbeat_count}: OK"
                    )

                    # نشر حدث النبض عبر EventBus
                    try:
                        from core.event_bus import event_bus
                        event_bus.emit("watchdog.heartbeat", {
                            "status": "healthy",
                            "count": self._heartbeat_count
                        })
                    except Exception:
                        pass

                else:
                    # عطل مرصود
                    self._consecutive_failures += 1
                    self._total_failures += 1
                    self._last_failure = health["timestamp"]
                    self._system_healthy = False

                    failed_checks = [
                        name for name, result in health["checks"].items()
                        if not result["healthy"]
                    ]
                    _watchdog_logger.warning(
                        f"FAILURE #{self._consecutive_failures}: "
                        f"Failed checks: {failed_checks}"
                    )

                    # إشعار بالعطل
                    if self._on_failure_callback:
                        try:
                            self._on_failure_callback(health, self._consecutive_failures)
                        except Exception:
                            pass

                    # فحص الحالة الحرجة
                    if self._consecutive_failures >= self.max_consecutive_failures:
                        _watchdog_logger.critical(
                            f"CRITICAL: {self._consecutive_failures} consecutive "
                            f"failures reached threshold!"
                        )
                        if self._on_critical_callback:
                            try:
                                self._on_critical_callback(health)
                            except Exception:
                                pass

            except Exception as e:
                _watchdog_logger.error(f"Watchdog loop error: {e}")

        _watchdog_logger.info("Watchdog stopped.")

    def start(self) -> None:
        """تشغيل الحارس كخيط خلفي."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(
            target=self._heartbeat_loop,
            name="NexumWatchdog",
            daemon=True
        )
        self._thread.start()
        _watchdog_logger.info("Watchdog daemon thread started.")

    def stop(self) -> None:
        """إيقاف الحارس."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=self.heartbeat_interval + 5)
        _watchdog_logger.info("Watchdog daemon thread stopped.")

    def get_status(self) -> dict:
        """تقرير حالة الحارس."""
        return {
            "running": self._running,
            "system_healthy": self._system_healthy,
            "heartbeat_count": self._heartbeat_count,
            "consecutive_failures": self._consecutive_failures,
            "total_failures": self._total_failures,
            "last_heartbeat": self._last_heartbeat,
            "last_failure": self._last_failure,
            "interval_seconds": self.heartbeat_interval,
            "registered_checks": list(self._health_checks.keys())
        }
