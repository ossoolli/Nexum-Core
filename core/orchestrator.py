"""
🔱 NEXUM Flow Orchestrator — المنسق المركزي
=============================================
يدير تنفيذ المهام عبر الـ Execution Graph ويبث النتائج للمستخدم والقناة.
"""
import threading
import time
import uuid
from typing import Dict, Any, Optional

from core.execution_graph import ExecutionGraph, TaskNode


class FlowOrchestrator:
    def __init__(self):
        self.active_graphs: Dict[str, ExecutionGraph] = {}
        self._lock = threading.Lock()
        self._bot = None
        self._admin_id = None
        self._channel_id = None
        self.planner = None

        # بدء المجدول في الخلفية
        self._scheduler = threading.Thread(target=self._run_scheduler, daemon=True)
        self._scheduler.start()

    def set_planner(self, planner):
        """ربط المخطط الذكي"""
        self.planner = planner

    def set_bot(self, bot, admin_id, channel_id=None):
        """ربط بوت تيليجرام للإشعارات والبث"""
        self._bot = bot
        self._admin_id = str(admin_id)
        self._channel_id = channel_id

    def _notify(self, msg: str, to_channel: bool = True):
        """إرسال إشعار للمستخدم وللقناة"""
        if not self._bot:
            return
        try:
            if self._admin_id:
                self._bot.send_message(self._admin_id, msg, parse_mode="Markdown")
        except Exception as e:
            print(f"[Orchestrator] Admin notify error: {e}")

        if to_channel and self._channel_id:
            try:
                self._bot.send_message(self._channel_id, msg, parse_mode="Markdown")
            except Exception as e:
                print(f"[Orchestrator] Channel broadcast error: {e}")

    # ─── تنفيذ هدف جديد ───
    def execute_goal(self, goal: str) -> Dict[str, Any]:
        if not self.planner:
            raise Exception("Planner not initialized.")

        protocol_id = f"proto_{uuid.uuid4().hex[:8]}"

        try:
            graph = self.planner.generate_execution_graph(goal, protocol_id)
        except Exception as e:
            raise Exception(f"Planning failed: {str(e)}")

        with self._lock:
            self.active_graphs[protocol_id] = graph

        return {"protocol_id": protocol_id, "status": "Executing"}

    # ─── تنفيذ مهمة واحدة ───
    def _execute_task(self, graph: ExecutionGraph, task: TaskNode):
        task.status = "RUNNING"

        from core.tool_registry import tool_registry

        try:
            result = tool_registry.execute_tool(task.action, task.params)
            
            # التحقق من النتيجة فعلياً (v7.2)
            verification = self._verify_step_result(task.action, task.params, result)
            
            if verification["verified"]:
                task.status = "COMPLETED"
                task.result = result
                # إرسال النتيجة
                result_preview = str(result)[:800]
                self._notify(
                    f"✅ **مهمة مكتملة**\n"
                    f"🧬 `{graph.protocol_id}`\n"
                    f"🛠️ `{task.action}`\n"
                    f"📊 {result_preview}"
                )
            else:
                raise Exception(verification["output"])

            # مزامنة Git إذا كانت العملية كتابة ملف
            if task.action in ("write_file", "run_host_terminal"):
                try:
                    from core.git_bot import auto_sync
                    auto_sync()
                except Exception:
                    pass

        except Exception as e:
            task.status = "FAILED"
            task.error = str(e)
            self._notify(f"❌ **فشل المهمة**\n🛠️ `{task.action}`\n`{str(e)}`")

    def _verify_step_result(self, tool_name: str, params: dict, raw_result: Any) -> dict:
        """
        يتحقق من صحة نتيجة كل خطوة قبل الإعلان عن النجاح.
        لا hallucination — إما نجح فعلاً أو فشل.
        """
        import os
        from core.system_tools import BASE_DIR

        # أدوات كتابة الملفات: تحقق من وجود الملف
        if tool_name in ("write_file", "create_file", "save_file"):
            path = params.get("filepath", "") or params.get("path", "")
            full_path = os.path.abspath(os.path.join(BASE_DIR, path)) if not os.path.isabs(path) else path
            if not os.path.exists(full_path):
                return {
                    "verified": False,
                    "output": f"الأداة ادّعت النجاح لكن الملف في '{path}' غير موجود فعلياً"
                }

        # أدوات Shell: تحقق من exit code (إذا توفر)
        if tool_name in ("run_host_terminal", "terminal", "shell"):
            if isinstance(raw_result, dict) and raw_result.get("status") == "failed":
                return {
                    "verified": False,
                    "output": raw_result.get("output", "الأمر فشل برمز خطأ")
                }

        return {"verified": True, "output": raw_result}

    # ─── المجدول (Scheduler Loop) ───
    def _run_scheduler(self):
        while True:
            graphs_to_process = []
            with self._lock:
                graphs_to_process = list(self.active_graphs.values())

            for graph in graphs_to_process:
                executable = graph.get_executable_nodes()
                for task in executable:
                    t = threading.Thread(target=self._execute_task, args=(graph, task))
                    t.start()

                # تنظيف: حذف الرسوم البيانية المكتملة
                if graph.is_completed() or graph.is_failed():
                    with self._lock:
                        self.active_graphs.pop(graph.protocol_id, None)

            time.sleep(1)


# Singleton
orchestrator = FlowOrchestrator()
