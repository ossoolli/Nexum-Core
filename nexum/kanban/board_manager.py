import os
import logging
from nexum.kanban.orchestrator import KanbanOrchestrator

logger = logging.getLogger("nexum.kanban.board_manager")

class BoardManager:
    def __init__(self):
        self.orchestrator = KanbanOrchestrator()
        self.default_board_name = "Sentinel Tasks"
        self._ensure_default_board()

    def _ensure_default_board(self) -> str:
        """
        Ensures at least one board exists. If not, creates a default one.
        Returns the board_id of the default/first board.
        """
        boards = self.orchestrator.data.get("boards", {})
        if not boards:
            logger.info("No Kanban boards found. Creating default 'Sentinel Tasks' board.")
            return self.orchestrator.create_board(self.default_board_name)
        # Return the first available board_id
        return list(boards.keys())[0]

    def _find_task(self, task_id: str):
        """
        Finds a task by its ID or title across all boards.
        Returns tuple of (board_id, task_dict) if found, otherwise (None, None).
        """
        boards = self.orchestrator.data.get("boards", {})
        for board_id, board in boards.items():
            for task in board.get("tasks", []):
                if task.get("id") == task_id or task.get("title") == task_id:
                    return board_id, task
        return None, None

    def move_task(self, task_id: str, new_status: str) -> bool:
        """
        Moves a task to a new status. If the task is not found,
        it is created in the default board first and then moved.
        """
        board_id, task = self._find_task(task_id)
        if not task:
            # Task not found, create a new one
            logger.info(f"Task '{task_id}' not found. Creating it in default board.")
            default_board_id = self._ensure_default_board()
            created_task_id = self.orchestrator.add_task(
                default_board_id,
                title=task_id,
                description="Autonomously created task"
            )
            if created_task_id:
                return self.orchestrator.move_task(default_board_id, created_task_id, new_status)
            return False

        # Task found, move it using its actual UUID
        return self.orchestrator.move_task(board_id, task["id"], new_status)

    def add_comment(self, task_id: str, comment: str) -> bool:
        """
        Adds a comment to a task. If the task is not found,
        it is created in the default board first and then commented.
        """
        board_id, task = self._find_task(task_id)
        if not task:
            logger.info(f"Task '{task_id}' not found for commenting. Creating it in default board.")
            default_board_id = self._ensure_default_board()
            created_task_id = self.orchestrator.add_task(
                default_board_id,
                title=task_id,
                description="Autonomously created task"
            )
            if created_task_id:
                return self.orchestrator.add_comment(default_board_id, created_task_id, comment)
            return False

        return self.orchestrator.add_comment(board_id, task["id"], comment)

# Expose a singleton instance of board_manager
board_manager = BoardManager()
