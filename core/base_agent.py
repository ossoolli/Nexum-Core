"""
🔱 BaseAgent — الكلاس الأساسي لجميع وكلاء NEXUM
=================================================
كل وكيل في النظام يرث من هذا الكلاس.
يوفر: حالة، مقاييس، تسجيل، Event Bus، فحص صحة.
"""
import os
import time
import logging
import threading
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, "storage", "logs", "agents")
os.makedirs(LOGS_DIR, exist_ok=True)


class AgentStatus(Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    TERMINATED = "TERMINATED"
    ERROR = "ERROR"


class BaseAgent(ABC):
    """كلاس أساسي لجميع الوكلاء — يجب أن يرث كل وكيل منه"""

    def __init__(self, name: str, description: str = "", version: str = "1.0"):
        self.name = name
        self.description = description
        self.version = version
        self.status = AgentStatus.IDLE
        self.created_at = time.time()
        self.last_active = time.time()
        self.error_count = 0
        self.metrics: Dict[str, Any] = {}
        self._lock = threading.Lock()

        # إعداد التسجيل
        log_file = os.path.join(LOGS_DIR, f"{self.name}.log")
        self._logger = logging.getLogger(f"nexum.agent.{self.name}")
        self._logger.setLevel(logging.DEBUG)
        if not self._logger.handlers:
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setFormatter(logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            ))
            self._logger.addHandler(fh)

        self.log(f"Agent '{self.name}' v{self.version} initialized.")

    # ═══════════════════════════════════════
    # الوظيفة الرئيسية (يجب تنفيذها)
    # ═══════════════════════════════════════

    @abstractmethod
    def run(self, input_data: dict) -> dict:
        """التشغيل الرئيسي — يجب أن ينفذه كل وكيل"""
        pass

    # ═══════════════════════════════════════
    # التحكم بالحالة
    # ═══════════════════════════════════════

    def start(self, input_data: dict = None) -> dict:
        """تشغيل الوكيل مع معالجة الأخطاء"""
        self._set_status(AgentStatus.RUNNING)
        try:
            result = self.run(input_data or {})
            self.last_active = time.time()
            self.record_metric("last_run_success", True)
            self._set_status(AgentStatus.IDLE)
            return result
        except Exception as e:
            self.error_count += 1
            self.record_metric("last_run_success", False)
            self.record_metric("last_error", str(e))
            self._set_status(AgentStatus.ERROR)
            self.log(f"Error in run(): {e}", level="ERROR")
            return {"status": "error", "error": str(e)}

    def pause(self):
        """إيقاف مؤقت"""
        self._set_status(AgentStatus.PAUSED)
        self.log("Agent paused.")

    def resume(self):
        """استئناف"""
        self._set_status(AgentStatus.IDLE)
        self.log("Agent resumed.")

    def terminate(self):
        """إنهاء نهائي"""
        self._set_status(AgentStatus.TERMINATED)
        self.log("Agent terminated.")

    # ═══════════════════════════════════════
    # التقارير والمقاييس
    # ═══════════════════════════════════════

    def get_status(self) -> dict:
        """تقرير حالة كامل"""
        uptime = time.time() - self.created_at
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "status": self.status.value,
            "uptime_seconds": round(uptime, 1),
            "uptime_human": self._format_uptime(uptime),
            "error_count": self.error_count,
            "last_active": datetime.fromtimestamp(self.last_active).isoformat(),
            "created_at": datetime.fromtimestamp(self.created_at).isoformat(),
            "metrics": dict(self.metrics),
        }

    def health_check(self) -> bool:
        """فحص صحة الوكيل — يعيد True إذا كان يعمل بشكل سليم"""
        return self.status not in (AgentStatus.ERROR, AgentStatus.TERMINATED)

    def record_metric(self, key: str, value: Any):
        """تسجيل مقياس"""
        with self._lock:
            self.metrics[key] = value

    # ═══════════════════════════════════════
    # الأحداث والتسجيل
    # ═══════════════════════════════════════

    def on_event(self, event: dict):
        """معالج الأحداث — يمكن تجاوزه"""
        self.log(f"Event received: {event.get('type', 'unknown')}")

    def log(self, message: str, level: str = "INFO"):
        """تسجيل موحّد"""
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
        }
        self._logger.log(level_map.get(level, logging.INFO), message)

    # ═══════════════════════════════════════
    # دوال داخلية
    # ═══════════════════════════════════════

    def _set_status(self, new_status: AgentStatus):
        """تغيير الحالة مع إرسال حدث"""
        old = self.status
        self.status = new_status
        self.log(f"Status: {old.value} → {new_status.value}")

        # بث الحدث
        try:
            from core.event_bus import event_bus
            event_bus.emit("agent.status_changed", {
                "agent": self.name,
                "old_status": old.value,
                "new_status": new_status.value,
                "timestamp": datetime.utcnow().isoformat(),
            })
        except Exception:
            pass  # EventBus قد لا يكون متوفراً

    @staticmethod
    def _format_uptime(seconds: float) -> str:
        """تنسيق وقت التشغيل"""
        h, r = divmod(int(seconds), 3600)
        m, s = divmod(r, 60)
        if h > 0:
            return f"{h}h {m}m"
        return f"{m}m {s}s"

    def __repr__(self):
        return f"<{self.__class__.__name__}('{self.name}') [{self.status.value}]>"
