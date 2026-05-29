import os
import re
from nexum.kanban.orchestrator import KanbanOrchestrator

class PredictiveSentinel:
    def __init__(self, log_path="/home/madarmutaz/Nexum-Core/storage/logs/out.log", kanban_storage="/home/madarmutaz/Nexum-Core/storage/kanban/boards.json"):
        self.log_path = log_path
        self.orchestrator = KanbanOrchestrator(storage_path=kanban_storage)
        self.board_id = self._get_or_create_board("System Maintenance")
    
    def _get_or_create_board(self, name):
        boards = self.orchestrator.data.get("boards", {})
        for bid, b in boards.items():
            if b.get("name") == name:
                return bid
        return self.orchestrator.create_board(name)

    def analyze_logs(self):
        if not os.path.exists(self.log_path):
            return
        
        try:
            with open(self.log_path, 'r') as f:
                lines = f.readlines()
                # Analyze last 50 lines for patterns
                recent_logs = "".join(lines[-50:])
            
            # Prediction logic
            if "Memory" in recent_logs or "Latency" in recent_logs:
                self.create_proactive_task()
        except Exception as e:
            print(f"Error analyzing logs: {e}")

    def create_proactive_task(self):
        task_id = self.orchestrator.add_task(self.board_id, "Proactive Optimization", "System detected memory or latency patterns in out.log.")
        if task_id:
            print(f"Created proactive optimization task: {task_id}")
