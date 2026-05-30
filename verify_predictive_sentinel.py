import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from nexum.kanban.predictive_monitor import PredictiveSentinel

# Test init
ps = PredictiveSentinel()
ps.analyze_logs()

# Check if task was created
boards = ps.orchestrator.data.get("boards", {})
task_found = False
for bid, b in boards.items():
    for task in b["tasks"]:
        if "Proactive Optimization" in task["title"]:
            task_found = True
            print(f"Task found: {task['title']}")
            break

if task_found:
    print("Verification successful: Task created.")
else:
    print("Verification failed: Task not found.")
