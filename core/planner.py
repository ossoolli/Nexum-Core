import json
import re


class AIPlanner:
    """وكيل التخطيط الذكي — يحول الأهداف النصية إلى خطط تنفيذية مرحلية"""

    SYSTEM_PROMPT = (
        "أنت مهندس DevOps خبير. عند استلام هدف، أرجع خطة تنفيذية كـ JSON فقط بدون أي نص إضافي.\n"
        "التنسيق المطلوب:\n"
        '{"plan_name": "اسم الخطة", "steps": [{"command": "الأمر", "description": "الوصف"}]}\n'
        "قواعد:\n"
        "- استخدم أوامر Linux/bash فقط\n"
        "- لا تستخدم أوامر تفاعلية (مثل nano, vim, vi)\n"
        "- استخدم -y للتثبيت التلقائي حيثما أمكن\n"
        "- أبقِ الخطوات بسيطة وواضحة\n"
        "- لا تتجاوز 10 خطوات\n"
    )

    def __init__(self, gemini_service):
        self.gemini = gemini_service

    def create_plan(self, goal: str) -> dict:
        """تحويل هدف نصي إلى خطة تنفيذية مرحلية"""
        try:
            prompt = f"الهدف: {goal}"
            raw = self.gemini.ask(prompt, system_instruction=self.SYSTEM_PROMPT)

            if not raw:
                return {"error": "لم يتم استلام رد من المحرك الذكي."}

            return self._parse_plan(raw)

        except Exception as e:
            return {"error": f"خطأ في التخطيط: {str(e)}"}

    def create_correction_plan(self, goal: str, failed_cmd: str, error_output: str) -> dict:
        """تصحيح ذاتي — يحلل الخطأ ويقترح أمراً بديلاً"""
        try:
            prompt = (
                f"الهدف الأصلي: {goal}\n"
                f"الأمر الذي فشل: {failed_cmd}\n"
                f"رسالة الخطأ: {error_output[:500]}\n\n"
                "أرجع JSON فقط بهذا التنسيق:\n"
                '{"fixed_command": "الأمر المصحح", "reason": "سبب التصحيح"}\n'
                "إذا لا يمكن الإصلاح، أرجع: {}"
            )
            raw = self.gemini.ask(prompt, system_instruction="أنت مهندس DevOps خبير. أرجع JSON فقط.")

            if not raw:
                return {}

            return self._parse_json(raw)

        except Exception:
            return {}

    def _parse_plan(self, raw: str) -> dict:
        """استخراج JSON من رد النموذج"""
        parsed = self._parse_json(raw)

        if not parsed:
            return {"error": "فشل تحليل الخطة — الرد غير صالح كـ JSON."}

        if "steps" not in parsed:
            return {"error": "الخطة لا تحتوي على خطوات (steps)."}

        if not parsed["steps"]:
            return {"error": "الخطة فارغة — لا توجد خطوات."}

        return parsed

    @staticmethod
    def _parse_json(raw: str) -> dict:
        """استخراج وتحليل أول كتلة JSON من نص حر"""
        # محاولة مباشرة
        try:
            return json.loads(raw.strip())
        except (json.JSONDecodeError, ValueError):
            pass

        # استخراج من كتلة ```json ... ```
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except (json.JSONDecodeError, ValueError):
                pass

        # استخراج أول { ... } من النص
        match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except (json.JSONDecodeError, ValueError):
                pass

        return {}
