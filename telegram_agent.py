import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from core.executor import executor
from core.planner import AIPlanner
from core.memory_local import LongTermMemory
from services.gemini_service import GeminiService


class TelegramAgent:
    """وكيل موحد يجمع كل المكونات"""

    def __init__(self):
        self.gemini = GeminiService(os.getenv("GOOGLE_API_KEY"))
        self.memory = LongTermMemory(os.path.join(BASE_DIR, "storage", "memory.json"))
        self.planner = AIPlanner(self.gemini)

    def handle(self, user_id: int, text: str) -> str:
        EXEC_KEYWORDS = [
            'ثبت', 'install', 'تثبيت', 'شغل', 'ارفع', 'deploy',
            'احذف', 'remove', 'أنشئ', 'create', 'أوقف', 'stop',
            'أعد', 'restart', 'حدّث', 'update', 'upgrade', 'نفذ', 'ابنِ', 'build'
        ]
        is_exec = any(kw in text.lower() for kw in EXEC_KEYWORDS)

        self.memory.save_context(user_id, text, role='user')

        if is_exec:
            plan = self.planner.create_plan(text)
            if "error" in plan:
                return f"❌ فشل التخطيط: {plan['error']}"

            results = []
            for step in plan.get('steps', []):
                cmd = step.get('command', '')
                desc = step.get('description', '')
                res = executor.execute(cmd, force=True)
                icon = "✅" if res['status'] == 'success' else "❌"
                results.append(f"{icon} {desc}\n{res.get('output', '')[:500]}")

            reply = "\n\n".join(results)
        else:
            reply = self.gemini.ask(text)

        self.memory.save_context(user_id, reply, role='assistant')
        return reply


agent = TelegramAgent()
