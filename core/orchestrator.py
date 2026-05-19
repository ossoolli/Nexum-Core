import os, telebot, threading, time, uuid, subprocess
from core.execution_graph import ExecutionGraph, TaskNode

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
bot = telebot.TeleBot(TOKEN) if TOKEN else None

class FlowOrchestrator:
    def __init__(self):
        self.active_graphs = {}
        self._lock = threading.Lock()
        threading.Thread(target=self._run_scheduler, daemon=True).start()

    def set_planner(self, planner): self.planner = planner

    def execute_goal(self, goal):
        protocol_id = f"proto_{uuid.uuid4().hex[:6]}"
        graph = self.planner.generate_execution_graph(goal, protocol_id)
        with self._lock: self.active_graphs[protocol_id] = graph
        return {"protocol_id": protocol_id}

    def _execute_task(self, graph, task):
        task.status = "RUNNING"
        from core.tool_registry import tool_registry
        try:
            # تنفيذ الأداة وجلب النتيجة الحقيقية
            result = tool_registry.execute_tool(task.action, task.params)
            task.status = "COMPLETED"
            
            # --- إرسال النتيجة فوراً للمستخدم ---
            if bot and ADMIN_ID:
                msg = f"✨ **تمت المهمة بنجاح!**\n📊 **النتيجة:**\n{str(result)[:1000]}"
                bot.send_message(ADMIN_ID, msg)
        except Exception as e:
            task.status = "FAILED"
            if bot and ADMIN_ID: bot.send_message(ADMIN_ID, f"❌ **فشل:** {str(e)}")

    def _run_scheduler(self):
        while True:
            graphs = []
            with self._lock: graphs = list(self.active_graphs.values())
            for g in graphs:
                for t in g.get_executable_nodes():
                    threading.Thread(target=self._execute_task, args=(g, t)).start()
            time.sleep(1)

orchestrator = FlowOrchestrator()
