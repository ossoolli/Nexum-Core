import threading
import time
import uuid
import os
import telebot
from typing import Dict, Any
from core.execution_graph import ExecutionGraph, TaskNode

# نربط البوت مباشرة هنا لإرسال الإشعارات المستقلة
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
feedback_bot = telebot.TeleBot(TOKEN) if TOKEN else None

class FlowOrchestrator:
    def __init__(self):
        self.active_graphs: Dict[str, ExecutionGraph] = {}
        self._lock = threading.Lock()
        self._scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self._scheduler_thread.start()

    def set_planner(self, planner):
        self.planner = planner

    def execute_goal(self, goal: str) -> Dict[str, Any]:
        protocol_id = f"proto_{uuid.uuid4().hex[:8]}"
        graph = self.planner.generate_execution_graph(goal=goal, protocol_id=protocol_id)
        with self._lock:
            self.active_graphs[protocol_id] = graph
        return {"protocol_id": protocol_id, "status": "Executing"}

    def _execute_task(self, graph: ExecutionGraph, task: TaskNode):
        task.status = "RUNNING"
        from core.tool_registry import tool_registry
        try:
            result = tool_registry.execute_tool(task.action, task.params)
            task.status = "COMPLETED"
            
            # --- إشعار النجاح الفوري ---
            if feedback_bot and ADMIN_ID:
                msg = f"✅ **تم الإنجاز بنجاح!**\n📋 الأداة: `{task.action}`\n📂 المسار: `{task.params.get('filepath', 'Host')}`\n🧬 البروتوكول: `{graph.protocol_id}`"
                feedback_bot.send_message(ADMIN_ID, msg, parse_mode="Markdown")
            
            # --- تشغيل الـ Auto Sync التلقائي لرفع الملف لـ GitHub ---
            from core.git_bot import auto_sync
            auto_sync()

        except Exception as e:
            task.status = "FAILED"
            if feedback_bot and ADMIN_ID:
                feedback_bot.send_message(ADMIN_ID, f"❌ **فشل في التنفيذ:**\n`{str(e)}`")

    def _run_scheduler(self):
        while True:
            graphs = []
            with self._lock:
                graphs = list(self.active_graphs.values())
            for graph in graphs:
                for task in graph.get_executable_nodes():
                    t = threading.Thread(target=self._execute_task, args=(graph, task))
                    t.start()
            time.sleep(1)

orchestrator = FlowOrchestrator()
