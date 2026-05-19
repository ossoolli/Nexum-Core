import threading
import time
import uuid
from typing import Dict, Any
from core.execution_graph import ExecutionGraph, TaskNode
from core.event_bus import event_bus
from core.lifecycle import lifecycle

class FlowOrchestrator:
    def __init__(self):
        self.active_graphs: Dict[str, ExecutionGraph] = {}
        self._lock = threading.Lock()
        self._scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self._scheduler_thread.start()

    def set_planner(self, planner):
        self.planner = planner

    def execute_goal(self, goal: str) -> Dict[str, Any]:
        if not hasattr(self, "planner") or not self.planner:
            raise Exception("AI Planner is not configured.")
        protocol_id = f"proto_{uuid.uuid4().hex[:8]}"
        try:
            graph = self.planner.generate_execution_graph(goal=goal, protocol_id=protocol_id)
            with self._lock:
                self.active_graphs[protocol_id] = graph
            return {"protocol_id": protocol_id, "status": "Executing"}
        except Exception as e:
            raise e

    def _execute_task(self, graph: ExecutionGraph, task: TaskNode):
        task.status = "RUNNING"
        from core.tool_registry import tool_registry
        try:
            # التنفيذ المباشر للأداة
            result = tool_registry.execute_tool(task.action, task.params)
            task.result = result
            task.status = "COMPLETED"
            print(f"✅ Executed {task.action}: {result}")
        except Exception as e:
            task.status = "FAILED"
            task.error = str(e)
            print(f"❌ Failed {task.action}: {e}")

    def _run_scheduler(self):
        while True:
            graphs = []
            with self._lock:
                graphs = list(self.active_graphs.values())
            for graph in graphs:
                for task in graph.get_executable_nodes():
                    self._execute_task(graph, task)
            time.sleep(1)

orchestrator = FlowOrchestrator()
