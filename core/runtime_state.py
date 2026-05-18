"""
Runtime State (`runtime_state.py`)
===================================
مصدر الحقيقة الموحد (Single Source of Truth) لتخزين الجلسات،
الحاويات النشطة، وحالات سير عمل الوكلاء في الذاكرة.
"""

import threading
from typing import Dict, List, Any
from datetime import datetime

class RuntimeState:
    def __init__(self):
        self._lock = threading.Lock()
        self.state: Dict[str, Any] = {
            "agents": {},
            "sessions": {},
            "events_history": [],
            "system_metrics": {
                "uptime_start": datetime.now().isoformat(),
                "status": "ONLINE"
            }
        }

    def push_event(self, event: dict):
        """تسجيل الحدث في السجل للحفاظ على الحالة الحية"""
        with self._lock:
            # الحد الأقصى للأحداث المحفوظة بالذاكرة
            if len(self.state["events_history"]) > 1000:
                self.state["events_history"].pop(0)
            self.state["events_history"].append(event)
            
    def get_recent_events(self, limit: int = 50) -> List[dict]:
        with self._lock:
            return self.state["events_history"][-limit:]

    def update_agent_state(self, agent_id: str, data: dict):
        with self._lock:
            if agent_id not in self.state["agents"]:
                self.state["agents"][agent_id] = {}
            self.state["agents"][agent_id].update(data)
            
    def set_agent(self, agent_id: str, data: dict):
        """تحديث بيانات وحالة الوكيل بالكامل"""
        with self._lock:
            self.state["agents"][agent_id] = data

    def get_agent_state(self, agent_id: str) -> dict:
        with self._lock:
            return self.state["agents"].get(agent_id, {})

    def get_all_agents_state(self) -> dict:
        with self._lock:
            return self.state.get("agents", {})

# Singleton
runtime_state = RuntimeState()
