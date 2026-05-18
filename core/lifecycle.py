"""
NEXUM PRIME — Agent Lifecycle Manager

يدير دورة حياة الوكلاء داخل الـ Runtime:
CREATED → READY → RUNNING → WAITING → FAILED → RETRYING → TERMINATED
"""

from datetime import datetime
import threading
import time

from core.agent_registry import agent_registry
from core.event_bus import event_bus
from core.runtime_state import runtime_state


class AgentLifecycle:

    # =========================
    # Agent States
    # =========================

    CREATED = "CREATED"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    TERMINATED = "TERMINATED"

    VALID_TRANSITIONS = {
        CREATED: [READY, TERMINATED],

        READY: [
            RUNNING,
            TERMINATED
        ],

        RUNNING: [
            WAITING,
            FAILED,
            READY,
            TERMINATED
        ],

        WAITING: [
            RUNNING,
            FAILED,
            TERMINATED
        ],

        FAILED: [
            RETRYING,
            TERMINATED
        ],

        RETRYING: [
            RUNNING,
            FAILED,
            TERMINATED
        ],

        TERMINATED: [],
    }

    def __init__(self):

        self._states = {}
        self._lock = threading.Lock()

    # =========================
    # Helpers
    # =========================

    def _now(self):
        return datetime.utcnow().isoformat()

    def _emit(self, event_type: str, payload: dict):

        payload["timestamp"] = self._now()

        try:
            event_bus.emit(event_type, payload)
        except Exception as e:
            print(f"[LIFECYCLE] Event emit failed: {e}")

    # =========================
    # Init Agent
    # =========================

    def init_agent(self, agent_id: str):

        with self._lock:

            if agent_id in self._states:
                return self._states[agent_id]

            state = {
                "agent_id": agent_id,

                "state": self.CREATED,

                "history": [
                    {
                        "state": self.CREATED,
                        "at": self._now(),
                    }
                ],

                "metrics": {
                    "tasks_completed": 0,
                    "tasks_failed": 0,
                    "retries": 0,
                    "uptime_seconds": 0,
                },

                "started_at": self._now(),
                "last_active": self._now(),
                "terminated_at": None,
            }

            self._states[agent_id] = state

            # sync runtime state
            runtime_state.set_agent(agent_id, state)

            # emit spawn event
            self._emit(
                event_bus.EVENT_TYPES["AGENT_SPAWNED"],
                {
                    "agent_id": agent_id,
                    "state": self.CREATED,
                }
            )

            return state

    # =========================
    # Transition
    # =========================

    def transition(self, agent_id: str, new_state: str) -> bool:

        with self._lock:

            if agent_id not in self._states:
                self.init_agent(agent_id)

            current_state = self._states[agent_id]["state"]

            allowed = self.VALID_TRANSITIONS.get(
                current_state,
                []
            )

            if new_state not in allowed:

                print(
                    f"[LIFECYCLE] Invalid transition "
                    f"{agent_id}: "
                    f"{current_state} → {new_state}"
                )

                return False

            # update state
            self._states[agent_id]["state"] = new_state

            self._states[agent_id]["last_active"] = self._now()

            self._states[agent_id]["history"].append({
                "state": new_state,
                "at": self._now(),
            })

            # terminated timestamp
            if new_state == self.TERMINATED:
                self._states[agent_id]["terminated_at"] = self._now()

            # retries metric
            if new_state == self.RETRYING:
                self._states[agent_id]["metrics"]["retries"] += 1

            # uptime metric
            started = datetime.fromisoformat(
                self._states[agent_id]["started_at"]
            )

            uptime = int(
                (datetime.utcnow() - started).total_seconds()
            )

            self._states[agent_id]["metrics"]["uptime_seconds"] = uptime

            # sync runtime state
            runtime_state.set_agent(
                agent_id,
                self._states[agent_id]
            )

            # update registry
            agent = agent_registry.get_agent(agent_id)

            if agent:

                agent["status"] = new_state

                try:
                    agent_registry._save_registry()
                except Exception as e:
                    print(f"[LIFECYCLE] Registry save failed: {e}")

            # =========================
            # Emit Events
            # =========================

            if new_state == self.RUNNING:

                self._emit(
                    event_bus.EVENT_TYPES["TASK_STARTED"],
                    {
                        "agent_id": agent_id,
                    }
                )

            elif new_state == self.WAITING:

                self._emit(
                    event_bus.EVENT_TYPES["TASK_COMPLETED"],
                    {
                        "agent_id": agent_id,
                    }
                )

            elif new_state == self.FAILED:

                self._emit(
                    event_bus.EVENT_TYPES["AGENT_FAILED"],
                    {
                        "agent_id": agent_id,
                    }
                )

            elif new_state == self.TERMINATED:

                self._emit(
                    event_bus.EVENT_TYPES["AGENT_STOPPED"],
                    {
                        "agent_id": agent_id,
                    }
                )

            return True

    # =========================
    # Record Task Result
    # =========================

    def record_task(self, agent_id: str, success: bool):

        with self._lock:

            if agent_id not in self._states:
                return

            if success:
                self._states[agent_id]["metrics"]["tasks_completed"] += 1

            else:
                self._states[agent_id]["metrics"]["tasks_failed"] += 1

            self._states[agent_id]["last_active"] = self._now()

            runtime_state.set_agent(
                agent_id,
                self._states[agent_id]
            )

    # =========================
    # Getters
    # =========================

    def get_state(self, agent_id: str):

        with self._lock:
            return self._states.get(
                agent_id,
                {
                    "state": "UNKNOWN"
                }
            )

    def get_all_states(self):

        with self._lock:
            return dict(self._states)

    # =========================
    # Cleanup
    # =========================

    def cleanup_terminated(self, older_than_seconds=3600):

        now = datetime.utcnow()

        with self._lock:

            to_delete = []

            for agent_id, state in self._states.items():

                if state["state"] != self.TERMINATED:
                    continue

                terminated_at = state.get("terminated_at")

                if not terminated_at:
                    continue

                terminated_dt = datetime.fromisoformat(
                    terminated_at
                )

                age = (now - terminated_dt).total_seconds()

                if age > older_than_seconds:
                    to_delete.append(agent_id)

            for agent_id in to_delete:

                self._states.pop(agent_id, None)

                runtime_state.del_agent(agent_id)

                print(
                    f"[LIFECYCLE] Cleaned terminated agent: {agent_id}"
                )


# Singleton
lifecycle = AgentLifecycle()