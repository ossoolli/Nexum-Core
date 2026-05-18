"""
Agent Lifecycle Manager — إدارة دورة حياة الوكلاء
كل وكيل يمر بحالات واضحة: CREATED → READY → RUNNING → WAITING → FAILED → TERMINATED
"""
import time
from datetime import datetime
from core.agent_registry import agent_registry
from core.event_bus import event_bus


class AgentLifecycle:
    """
    يدير حالة كل وكيل ويسجل التحولات ويبث أحداثها عبر الـ Event Bus.
    """

    # الحالات الممكنة
    CREATED = "CREATED"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    TERMINATED = "TERMINATED"

    VALID_TRANSITIONS = {
        CREATED: [READY, TERMINATED],
        READY: [RUNNING, TERMINATED],
        RUNNING: [WAITING, FAILED, TERMINATED, READY],
        WAITING: [RUNNING, FAILED, TERMINATED],
        FAILED: [RETRYING, TERMINATED],
        RETRYING: [RUNNING, FAILED, TERMINATED],
        TERMINATED: [],
    }

    def __init__(self):
        # agent_id -> { state, history, metrics }
        self._states = {}

    def init_agent(self, agent_id: str):
        """تسجيل وكيل جديد في نظام دورة الحياة"""
        self._states[agent_id] = {
            "state": self.CREATED,
            "history": [{"state": self.CREATED, "at": datetime.now().isoformat()}],
            "tasks_completed": 0,
            "tasks_failed": 0,
            "started_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat(),
        }
        event_bus.emit(event_bus.AGENT_SPAWNED, {
            "agent_id": agent_id,
            "state": self.CREATED,
        })
        return self._states[agent_id]

    def transition(self, agent_id: str, new_state: str) -> bool:
        """نقل وكيل إلى حالة جديدة مع التحقق من صحة التحول"""
        if agent_id not in self._states:
            self.init_agent(agent_id)

        current = self._states[agent_id]["state"]
        allowed = self.VALID_TRANSITIONS.get(current, [])

        if new_state not in allowed:
            print(f"[LIFECYCLE] Invalid transition: {agent_id} {current} → {new_state}")
            return False

        self._states[agent_id]["state"] = new_state
        self._states[agent_id]["last_active"] = datetime.now().isoformat()
        self._states[agent_id]["history"].append({
            "state": new_state,
            "at": datetime.now().isoformat(),
        })

        # بث الحدث
        if new_state == self.FAILED:
            event_bus.emit(event_bus.AGENT_FAILED, {"agent_id": agent_id})
        elif new_state == self.TERMINATED:
            event_bus.emit(event_bus.AGENT_STOPPED, {"agent_id": agent_id})

        # تحديث السجل الرئيسي
        agent = agent_registry.get_agent(agent_id)
        if agent:
            agent["status"] = new_state
            agent_registry._save_registry()

        return True

    def record_task(self, agent_id: str, success: bool):
        """تسجيل نتيجة مهمة لوكيل (نجاح أو فشل)"""
        if agent_id not in self._states:
            return
        if success:
            self._states[agent_id]["tasks_completed"] += 1
        else:
            self._states[agent_id]["tasks_failed"] += 1

    def get_state(self, agent_id: str) -> dict:
        """جلب الحالة الكاملة لوكيل"""
        return self._states.get(agent_id, {"state": "UNKNOWN"})

    def get_all_states(self) -> dict:
        """جلب حالات جميع الوكلاء"""
        return dict(self._states)


lifecycle = AgentLifecycle()
