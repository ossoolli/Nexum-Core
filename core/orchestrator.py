"""
NEXUM Orchestrator – The Sovereign Runtime Controller
===================================================
1. يستقبل أهدافاً (Goals) أو ملفات بروتوكول ويحولها لـ Execution Graph.
2. يدير الجدولة (Scheduling) وتشغيل الوكلاء.
3. يتعافى من الأخطاء من خلال Retry Policies.
4. يبقيك على اطلاع حيوي عبر Event Bus و Lifecycle State Machine.
"""

import threading
import time
import uuid
from typing import Dict, Any
from core.execution_graph import ExecutionGraph, TaskNode
from core.event_bus import event_bus
from core.lifecycle import lifecycle
from core.agent_registry import agent_registry

class FlowOrchestrator:
    def __init__(self):
        self.active_graphs: Dict[str, ExecutionGraph] = {}
        self._lock = threading.Lock()
        
        # وحدة معالجة خلفية لجدولة المهام بشكل دوري
        self._scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self._scheduler_thread.start()

    def execute_goal(self, goal: str) -> Dict[str, Any]:
        """
        يحول تعليمات المستخدم اللغوية إلى `ExecutionGraph` ويضعها في الطابور للتنفيذ.
        """
        protocol_id = f"proto_{uuid.uuid4().hex[:8]}"
        
        # مؤقتاً: سنقوم ببناء مسار وهمي مبدئي (Graph Generation بواسطة LLM هي خطوتك التالية)
        graph = ExecutionGraph(protocol_id=protocol_id)
        
        # مثال وهمي لمحاكاة Graph
        node1 = TaskNode("task_1", "agent_frontend", "init_project", {"goal": goal})
        node2 = TaskNode("task_2", "agent_docker", "build_container", {}, retries=3)
        node3 = TaskNode("task_3", "agent_monitor", "verify_health", {})
        
        node2.add_dependency("task_1")
        node3.add_dependency("task_2")
        
        graph.add_node(node1)
        graph.add_node(node2)
        graph.add_node(node3)
        
        with self._lock:
            self.active_graphs[protocol_id] = graph

        event_bus.emit(event_bus.PROTOCOL_COMPILED, {
            "protocol_id": protocol_id, 
            "nodes": len(graph.nodes)
        })
        
        return {"protocol_id": protocol_id, "status": "Executing"}

    def _execute_task(self, graph: ExecutionGraph, task: TaskNode):
        """تنفيذ المهمة عبر الوكيل ومراقبة حالتها"""
        task.status = "RUNNING"
        task.attempts += 1
        task.started_at = time.time()
        
        # 1. تحديث دورة حياة الوكيل
        lifecycle.transition(task.agent_id, lifecycle.RUNNING)
        event_bus.emit(event_bus.TASK_STARTED, {
            "protocol_id": graph.protocol_id,
            "task_id": task.task_id,
            "agent_id": task.agent_id
        })
        
        try:
            # 2. تشغيل الحاوية أو دالة الوكيل (Mock temporarily)
            # here we would actually call the sandbox or agent handler
            print(f"🚀 [Orchestrator] Executing task {task.task_id} on {task.agent_id}...")
            time.sleep(2) # محاكاة معالجة طويلة
            
            # إذا فشلت كمحاكاة يمكن رفع استثناء لتجربة استراتيجية الـ Retry
            # if task.task_id == "task_2" and task.attempts < 2:
            #     raise Exception("Container build random error")
                
            task.result = {"status": "ok", "logs": "Done processing."}
            task.completed_at = time.time()
            task.status = "COMPLETED"
            
            lifecycle.record_task(task.agent_id, success=True)
            lifecycle.transition(task.agent_id, lifecycle.READY)
            
            event_bus.emit(event_bus.TASK_COMPLETED, {
                "protocol_id": graph.protocol_id,
                "task_id": task.task_id,
                "agent_id": task.agent_id,
                "duration": task.completed_at - task.started_at
            })
            
        except Exception as e:
            # 3. إدارة الفشل ومحاولات الإعادة
            task.error = str(e)
            print(f"❌ [Orchestrator] Task {task.task_id} failed: {e}")
            lifecycle.record_task(task.agent_id, success=False)
            
            if task.attempts <= task.max_retries:
                task.status = "PENDING"
                lifecycle.transition(task.agent_id, lifecycle.RETRYING)
                event_bus.emit(event_bus.SYSTEM_ALERT, {
                    "level": "warning", 
                    "msg": f"Retrying task {task.task_id} ({task.attempts}/{task.max_retries})"
                })
            else:
                task.status = "FAILED"
                lifecycle.transition(task.agent_id, lifecycle.FAILED)
                event_bus.emit(event_bus.TASK_FAILED, {
                    "protocol_id": graph.protocol_id,
                    "task_id": task.task_id,
                    "agent_id": task.agent_id,
                    "error": str(e)
                })

    def _run_scheduler(self):
        """مجدول غير متزامن يعمل في الخلفية لمراقبة Graphs وتنفيذها"""
        while True:
            graphs_snapshot = []
            with self._lock:
                graphs_snapshot = list(self.active_graphs.values())
                
            for graph in graphs_snapshot:
                if graph.is_completed() or graph.is_failed():
                    if graph.protocol_id in self.active_graphs:
                        # التنظيف في حال الانتهاء
                        with self._lock:
                            del self.active_graphs[graph.protocol_id]
                    continue
                
                # جلب المهام الجاهزة للتنفيذ والتي لم تبدأ بعد
                ready_tasks = graph.get_executable_nodes()
                for task in ready_tasks:
                    # نطلق التنفيذ في thread جديد لعدم قفل الـ scheduler
                    t = threading.Thread(target=self._execute_task, args=(graph, task))
                    t.start()
                    
            time.sleep(1) # استراحة المجدول

# Singleton
orchestrator = FlowOrchestrator()
