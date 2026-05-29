import logging
from nexum.kanban.board_manager import board_manager

logger = logging.getLogger("nexum.sentinel.integration")

def sync_sentinel_to_kanban(task_id: str, status: str, result_log: str):
    """
    يقوم الحارس (Sentinel) بتحديث حالة المهام في لوحة الـ Kanban
    تلقائياً عند انتهاء الفحص أو الإصلاح الذاتي.
    """
    try:
        if status == "SUCCESS":
            board_manager.move_task(task_id, "Done")
            logger.info(f"✅ Sentinel moved task {task_id} to Done.")
        elif status == "FAILED":
            board_manager.move_task(task_id, "In Progress")
            board_manager.add_comment(task_id, f"⚠️ Sentinel Error: {result_log[:50]}...")
            logger.warning(f"⚠️ Sentinel reported failure for task {task_id}. Moved to In Progress.")
    except Exception as e:
        logger.error(f"❌ Failed to sync Sentinel with Kanban: {e}")

