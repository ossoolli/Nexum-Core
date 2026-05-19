import time
from typing import Dict, Any

class RuntimeMetricsEngine:
    """
    Sovereign Runtime Metrics Engine
    يجمع مقاييس أداء النظام بشكل حي لمعالجة الضغط (Backpressure)
    وعرض الأداء العام في الـ Mini App
    """
    def __init__(self):
        self.metrics = {
            "agent_execution_time": {}, # { agent_id: avg_time }
            "task_retries": 0,
            "event_latency": 0.0,
            "queue_depth": 0,
            "memory_pressure": 0.0,
            "websocket_throughput": 0
        }
        self.start_times = {}

    def start_timer(self, task_id: str):
        self.start_times[task_id] = time.time()

    def stop_timer(self, task_id: str, agent_id: str = None):
        if task_id in self.start_times:
            duration = time.time() - self.start_times.pop(task_id)
            if agent_id:
                current_avg = self.metrics["agent_execution_time"].get(agent_id, duration)
                # Simple moving average
                self.metrics["agent_execution_time"][agent_id] = (current_avg * 0.8) + (duration * 0.2)
            return duration
        return 0

    def record_retry(self):
        self.metrics["task_retries"] += 1

    def update_queue_depth(self, depth: int):
        self.metrics["queue_depth"] = depth
        
    def get_current_metrics(self) -> Dict[str, Any]:
        return dict(self.metrics)

metrics_engine = RuntimeMetricsEngine()
