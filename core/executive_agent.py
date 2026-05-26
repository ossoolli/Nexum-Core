"""
core/executive_agent.py
الوكيل التنفيذي — يستقبل المهام من المايسترو وينسق تنفيذها عبر ExecutionEngine
"""
from core.base_agent import BaseAgent
from core.execution_engine import execution_engine
from services.gemini_service import gemini_service


class ExecutiveAgent(BaseAgent):
    """
    الوكيل التنفيذي الرئيسي:
    1. يستقبل أمراً نصياً من المستخدم
    2. يمرره إلى ExecutionEngine للتخطيط والتنفيذ
    3. يعيد تقريراً منسّقاً بصيغة HTML
    """

    def __init__(self):
        super().__init__(
            name="executive_agent",
            description="الوكيل التنفيذي — ينسق تنفيذ المهام عبر ExecutionEngine",
            version="1.0"
        )
        # ربط Gemini بـ ExecutionEngine
        execution_engine.set_gemini(gemini_service)

    def run(self, input_data: dict) -> dict:
        """التنفيذ الرئيسي — يستقبل dict ويعيد dict"""
        mission = input_data.get("text", input_data.get("mission", ""))
        if not mission:
            return {"status": "error", "error": "لا يوجد أمر للتنفيذ"}

        try:
            result = execution_engine.execute_goal(mission)
            return result
        except Exception as e:
            self.log(f"Executive mission failed: {e}", level="ERROR")
            return {"status": "error", "error": str(e)}

    def execute_mission(self, mission_text: str) -> str:
        """
        واجهة مبسطة — يستقبل نصاً ويعيد تقريراً HTML.
        هذه هي الدالة التي يستدعيها main.py مباشرة.
        """
        self.log(f"Mission received: {mission_text[:80]}")

        try:
            result = self.run({"text": mission_text})
            return self._format_report(result, mission_text)
        except Exception as e:
            self.log(f"Mission error: {e}", level="ERROR")
            return f"❌ <b>[Executive Error]:</b>\n<code>{str(e)}</code>"

    def _format_report(self, result: dict, mission: str) -> str:
        """تنسيق التقرير النهائي بصيغة HTML لتيليجرام"""
        status = result.get("status", "unknown")

        if status == "error":
            error = result.get("error", "خطأ غير معروف")
            return (
                f"❌ <b>[Mission Failed]</b>\n"
                f"📝 <i>{mission[:100]}</i>\n"
                f"<code>{error}</code>"
            )

        # تقرير ناجح أو مكتمل جزئياً
        done = result.get("done", 0)
        total = result.get("total", 0)
        plan = result.get("plan", {})
        title = plan.get("title", "مهمة تنفيذية") if plan else "مهمة تنفيذية"

        icon = "✅" if done == total else "⚠️"

        report = (
            f"{icon} <b>[Mission Report]</b>\n"
            f"📋 <b>{title}</b>\n"
            f"📊 اكتملت <b>{done}/{total}</b> خطوة\n"
        )

        # تفاصيل الخطوات
        results = result.get("results", [])
        for r in results[:10]:  # أقصى 10 خطوات في التقرير
            step_ok = r.get("result", {}).get("success", False)
            step_icon = "✅" if step_ok else "❌"
            desc = r.get("desc", r.get("type", "خطوة"))
            report += f"  {step_icon} {desc}\n"

        if len(results) > 10:
            report += f"  ... و {len(results) - 10} خطوات أخرى\n"

        return report


# Singleton
executive_agent = ExecutiveAgent()
