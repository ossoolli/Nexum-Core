import os
import pytest
from nexum.kanban.orchestrator import KanbanOrchestrator
from nexum.kanban.board_manager import BoardManager
from nexum.kanban.sentinel_integration import sync_sentinel_to_kanban

def test_kanban_orchestrator(tmp_path):
    storage_path = os.path.join(tmp_path, "boards.json")
    orchestrator = KanbanOrchestrator(storage_path=storage_path)
    
    # Test board creation
    board_id = orchestrator.create_board("Test Board")
    assert board_id is not None
    assert orchestrator.data["boards"][board_id]["name"] == "Test Board"
    
    # Test task addition
    task_id = orchestrator.add_task(board_id, "Test Task", "Description")
    assert task_id is not None
    
    # Test move task
    assert orchestrator.move_task(board_id, task_id, "Done") is True
    tasks = orchestrator.list_tasks(board_id)
    assert tasks[0]["status"] == "Done"

def test_board_manager(tmp_path):
    storage_path = os.path.join(tmp_path, "boards.json")
    
    # Monkeypatch storage path for testing
    import nexum.kanban.board_manager as bm
    original_orchestrator = bm.board_manager.orchestrator
    bm.board_manager.orchestrator = KanbanOrchestrator(storage_path=storage_path)
    
    try:
        # Move task should auto-create it if it doesn't exist
        assert bm.board_manager.move_task("my_test_task", "Done") is True
        
        # Verify it exists and is Done
        board_id, task = bm.board_manager._find_task("my_test_task")
        assert task is not None
        assert task["title"] == "my_test_task"
        assert task["status"] == "Done"
        
        # Test commenting on it
        assert bm.board_manager.add_comment("my_test_task", "This is a comment") is True
        assert len(task["comments"]) == 1
        assert task["comments"][0]["text"] == "This is a comment"
        
        # Test syncing via sentinel integration
        sync_sentinel_to_kanban("my_test_task", "FAILED", "Some error occurred")
        assert task["status"] == "In Progress"
        assert len(task["comments"]) == 2
        assert "Sentinel Error" in task["comments"][1]["text"]
        
    finally:
        bm.board_manager.orchestrator = original_orchestrator
