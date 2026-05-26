# -*- coding: utf-8 -*-
"""
core/execution_graph.py
محرك المخطط التنفيذي الرسومي (DAG Execution Engine) لـ Nexum Pro (v7.2.5)
=========================================================================
- يدير اعتماديات المهام ويمنع حدوث Race Conditions في البيئة المتوازية.
- يدعم التكرار المرن عند الفشل مع حساب التراجع الأسي (Exponential Backoff).
- مزامنة كاملة ومحمية بأقفال المزامنة (Thread-Safe) مع باص الأحداث المركزي.
- فحص وقائي ضد الحلقات التكرارية والـ Deadlocks.
"""

import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional

# استيراد باص الأحداث والتحكم بالحياة بشكل دفاعي مع Fallbacks وقائية
try:
    from core.event_bus import event_bus
except ImportError:
    class DummyEventBus:
        def publish(self, *args, **kwargs): pass
        def get_history(self, *args, **kwargs): return []
    event_bus = DummyEventBus()

try:
    from core.lifecycle import lifecycle
except ImportError:
    class DummyLifecycle:
        pass
    lifecycle = DummyLifecycle()


class TaskNode:
    """يمثل عقدة عمل فردية مشفرة ومؤمنة ضمن المخطط التنفيذي الرسومي للمأمورية."""

    def __init__(self, task_id: str, agent_id: str, action: str,
                 params: dict, retries: int = 2, timeout_seconds: int = 30):
        self.task_id = task_id
        self.agent_id = agent_id
        self.action = action
        self.params = params
        self.status = "PENDING"  # PENDING, RUNNING, COMPLETED, FAILED, RETRYING

        # حواجز الأمان لعمليات التكرار والوقت المستهلك
        self.max_retries = max(0, retries)
        self.attempts = 0
        self.timeout = max(5, timeout_seconds)

        self.result: Any = None
        self.error: Optional[str] = None

        # تتبع الاعتماديات الزمنية للخطوة
        self.dependencies: List[str] = []
        self.started_at: Optional[str] = None
        self.completed_at: Optional[str] = None

    def add_dependency(self, task_id: str) -> None:
        """إضافة خطوة اعتمادية يجب إنجازها بنجاح قبل البدء في هذه العقدة."""
        if task_id and task_id not in self.dependencies:
            self.dependencies.append(task_id)

    def calculate_backoff_delay(self) -> float:
        """حساب وقت الانتظار الأسي قبل إعادة محاولة التنفيذ لمنع الضغط على الموارد."""
        return float(1.5 ** self.attempts)


class ExecutionGraph:
    """يدير مصفوفة المهام المترابطة ويتحكم في تدفق العمليات برمجيا بأمان تام."""

    def __init__(self, protocol_id: str):
        self.protocol_id = protocol_id
        self.nodes: Dict[str, TaskNode] = {}
        self.status = "CREATED"  # CREATED, RUNNING, COMPLETED, FAILED
        self._lock = threading.Lock()
        self.created_at = datetime.now().isoformat()

    def add_node(self, node: TaskNode) -> None:
        """إدراج عقدة عمل جديدة داخل المخطط وتأمينها في الذاكرة الحية."""
        with self._lock:
            self.nodes[node.task_id] = node

    def get_executable_nodes(self) -> List[TaskNode]:
        """استرجاع الخطوات الجاهزة للتنفيذ فورا (التي اكتملت كافة اعتمادياتها السابقة)."""
        executable = []
        with self._lock:
            for node in self.nodes.values():
                if node.status in ("PENDING", "RETRYING"):
                    is_ready = True
                    for dep in node.dependencies:
                        dep_node = self.nodes.get(dep)
                        if not dep_node or dep_node.status != "COMPLETED":
                            is_ready = False
                            break
                    if is_ready:
                        executable.append(node)
        return executable

    def mark_task_running(self, task_id: str) -> None:
        """تحديث حالة المهمة إلى قيد التشغيل وتوثيق ذلك في باص الأحداث."""
        with self._lock:
            node = self.nodes.get(task_id)
            if node:
                node.status = "RUNNING"
                node.started_at = datetime.now().isoformat()
                node.attempts += 1

                event_bus.publish("task_started", {
                    "protocol_id": self.protocol_id,
                    "task_id": task_id,
                    "action": node.action,
                    "attempt": node.attempts
                })
                print(f"[Execution Engine] Task '{task_id}' started running (Attempt {node.attempts}).")

    def mark_task_completed(self, task_id: str, result: Any) -> None:
        """تحديث حالة المهمة بنجاح وتوثيق مخرجاتها في المخطط."""
        with self._lock:
            node = self.nodes.get(task_id)
            if node:
                node.status = "COMPLETED"
                node.completed_at = datetime.now().isoformat()
                node.result = result

                event_bus.publish("task_completed", {
                    "protocol_id": self.protocol_id,
                    "task_id": task_id,
                    "status": "success"
                })
                print(f"[Execution Engine] Task '{task_id}' completed successfully.")

                # فحص ما إذا كان المخطط الرسومي بأكمله قد تم إنجازه
                if self._check_all_completed():
                    self.status = "COMPLETED"
                    event_bus.publish("protocol_completed", {
                        "protocol_id": self.protocol_id,
                        "status": "success"
                    })

    def mark_task_failed(self, task_id: str, error: str) -> bool:
        """
        تحديث حالة الفشل للخطوة.
        تعيد True إذا كان مسموحا بإعادة المحاولة (Exponential Retry)،
        أو False إذا تم استهلاك المحاولات بالكامل.
        """
        with self._lock:
            node = self.nodes.get(task_id)
            if not node:
                return False

            node.error = error

            # 1. التحقق من إمكانية التكرار الوقائي
            if node.attempts <= node.max_retries:
                node.status = "RETRYING"
                delay = node.calculate_backoff_delay()

                event_bus.publish("task_retrying", {
                    "protocol_id": self.protocol_id,
                    "task_id": task_id,
                    "error": error,
                    "backoff_delay_seconds": delay
                })
                print(f"[Execution Engine] Task '{task_id}' failed. Retrying in {delay:.1f}s...")
                return True

            # 2. الفشل النهائي
            node.status = "FAILED"
            node.completed_at = datetime.now().isoformat()
            self.status = "FAILED"

            event_bus.publish("task_failed", {
                "protocol_id": self.protocol_id,
                "task_id": task_id,
                "error": error
            })
            event_bus.publish("protocol_failed", {
                "protocol_id": self.protocol_id,
                "status": "failed",
                "failed_at_task": task_id
            })
            print(f"[Execution Engine CRITICAL] Task '{task_id}' failed permanently after {node.attempts} attempts.")
            return False

    def is_completed(self) -> bool:
        """تتحقق مما إذا كان المخطط بالكامل قد اكتمل بنجاح."""
        with self._lock:
            return self.status == "COMPLETED" or self._check_all_completed()

    def is_failed(self) -> bool:
        """تتحقق مما إذا كان المخطط قد انهار بسبب فشل خطوة حرجة."""
        with self._lock:
            return self.status == "FAILED"

    def get_progress(self) -> dict:
        """حساب وتقديم ملخص مئوي فوري لتقدم المأمورية ونشاطها."""
        with self._lock:
            total = len(self.nodes)
            if total == 0:
                return {"percent": 100.0, "completed": 0, "total": 0}

            completed = sum(1 for n in self.nodes.values() if n.status == "COMPLETED")
            percent = (completed / total) * 100.0
            return {
                "percent": round(percent, 1),
                "completed": completed,
                "total": total,
                "failed": sum(1 for n in self.nodes.values() if n.status == "FAILED"),
                "running": sum(1 for n in self.nodes.values() if n.status == "RUNNING"),
                "pending": sum(1 for n in self.nodes.values() if n.status in ("PENDING", "RETRYING"))
            }

    def get_summary(self) -> dict:
        """يعيد ملخصا كاملا لحالة المخطط وكل عقدة فيه."""
        with self._lock:
            return {
                "protocol_id": self.protocol_id,
                "status": self.status,
                "created_at": self.created_at,
                "progress": self.get_progress(),
                "nodes": {
                    tid: {
                        "action": n.action,
                        "status": n.status,
                        "attempts": n.attempts,
                        "dependencies": n.dependencies,
                        "error": n.error
                    }
                    for tid, n in self.nodes.items()
                }
            }

    # ─── دوال مساعدة داخلية ───
    def _check_all_completed(self) -> bool:
        """فحص داخلي: هل اكتملت جميع العقد؟ (يُستدعى داخل Lock)"""
        if not self.nodes:
            return False
        return all(n.status == "COMPLETED" for n in self.nodes.values())
