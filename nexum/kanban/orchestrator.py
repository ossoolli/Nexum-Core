import json
import os
import uuid
from datetime import datetime

class KanbanOrchestrator:
    def __init__(self, storage_path="/home/madarmutaz/Nexum-Core/storage/kanban/boards.json"):
        self.storage_path = storage_path
        self._load_data()

    def _load_data(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {"boards": {}}

    def _save_data(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.data, f, indent=2)

    def create_board(self, name):
        board_id = str(uuid.uuid4())
        self.data["boards"][board_id] = {
            "name": name,
            "tasks": [],
            "created_at": datetime.now().isoformat()
        }
        self._save_data()
        return board_id

    def add_task(self, board_id, title, description=""):
        if board_id not in self.data["boards"]:
            return None
        task = {
            "id": str(uuid.uuid4()),
            "title": title,
            "description": description,
            "status": "todo",
            "assignee": None,
            "comments": []
        }
        self.data["boards"][board_id]["tasks"].append(task)
        self._save_data()
        return task["id"]

    def move_task(self, board_id, task_id, new_status):
        board = self.data["boards"].get(board_id)
        if not board: return False
        for task in board["tasks"]:
            if task["id"] == task_id:
                task["status"] = new_status
                self._save_data()
                return True
        return False

    def assign_task(self, board_id, task_id, assignee):
        board = self.data["boards"].get(board_id)
        if not board: return False
        for task in board["tasks"]:
            if task["id"] == task_id:
                task["assignee"] = assignee
                self._save_data()
                return True
        return False

    def add_comment(self, board_id, task_id, comment):
        board = self.data["boards"].get(board_id)
        if not board: return False
        for task in board["tasks"]:
            if task["id"] == task_id:
                task["comments"].append({"text": comment, "timestamp": datetime.now().isoformat()})
                self._save_data()
                return True
        return False

    def list_tasks(self, board_id):
        return self.data["boards"].get(board_id, {}).get("tasks", [])
