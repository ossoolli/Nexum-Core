"""
Execution Graph Engine – لمحرك الأوركستريتور
========================================
يمرّر مهام (Tasks) لـ الوكلاء عبر بناء هيكل (Directed Acyclic Graph (DAG)).
يتأكد من:
1. الاعتماديات (Dependencies) بين المهام لا يحدث لها Race Conditions.
2. السياسات مثل محاولات الإعادة (Retries) قبل إعلان الفشل.
3. بث أحداث (Execution) بشكل لحظي للـ Event Bus.
"""

from typing import Dict, List, Any, Optional
import time
import threading
from datetime import datetime
from core.event_bus import event_bus
from core.lifecycle import lifecycle

class TaskNode:
    """يمثل عقدة واحدة في مسار التنفيذ (مهمة لوكيل)"""
    def __init__(self, task_id: str, agent_id: str, action: str, params: dict, retries: int = 2):
        self.task_id = task_id
        self.agent_id = agent_id
        self.action = action
        self.params = params
        self.status = "PENDING"  # PENDING, RUNNING, COMPLETED, FAILED
        self.max_retries = retries
        self.attempts = 0
        self.result = None
        self.error = None
        
        self.dependencies: List[str] = [] # task_ids التي يجب أن تنتهي قبل أن أبدأ
        self.started_at: Optional[str] = None
        self.completed_at: Optional[str] = None

    def add_dependency(self, task_id: str):
        if task_id not in self.dependencies:
            self.dependencies.append(task_id)


class ExecutionGraph:
    """يدير مجموعة المهام والعلاقات بينها ضمن بروتوكول محدد"""
    def __init__(self, protocol_id: str):
        self.protocol_id = protocol_id
        self.nodes: Dict[str, TaskNode] = {}
        self.status = "CREATED"  # RUNNING, COMPLETED, FAILED
        self._lock = threading.Lock()

    def add_node(self, node: TaskNode):
        with self._lock:
            self.nodes[node.task_id] = node

    def get_executable_nodes(self) -> List[TaskNode]:
        """إرجاع المهام القابلة للتنفيذ حالياً (جاهزة لعدم وجود اعتمادات أو تم إنجازها)"""
        executable = []
        with self._lock:
            for node in self.nodes.values():
                if node.status == "PENDING":
                    # التأكد أن جميع الاعتمادات قد اكتملت
                    is_ready = all(
                        self.nodes[dep].status == "COMPLETED" 
                        for dep in node.dependencies if dep in self.nodes
                    )
                    if is_ready:
                        executable.append(node)
        return executable

    def is_completed(self) -> bool:
        with self._lock:
            return all(n.status == "COMPLETED" for n in self.nodes.values())
            
    def is_failed(self) -> bool:
         with self._lock:
            return any(n.status == "FAILED" for n in self.nodes.values())
