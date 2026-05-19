"""
🤖 AgentSmith — مصنع الوكلاء الذكي
=====================================
يصمّم ويبني وينشر وكلاء جاهزة للتشغيل.
يرث من BaseAgent.
"""
import os
import sys
import json
import shutil
import zipfile
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from core.base_agent import BaseAgent

SPECS_DIR = os.path.join(BASE_DIR, "storage", "agent_specs")
GENERATED_DIR = os.path.join(BASE_DIR, "agents", "generated")
os.makedirs(SPECS_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)


class AgentSmith(BaseAgent):
    """مصنع الوكلاء — يصمّم ويبني ويختبر وكلاء NEXUM"""

    def __init__(self):
        super().__init__(
            name="agent_smith",
            description="يصمّم ويبني وينشر وكلاء ذكاء اصطناعي",
            version="1.0"
        )

    def run(self, input_data: dict) -> dict:
        action = input_data.get("action", "design")
        if action == "design":
            return self.design_agent(
                input_data.get("name", "custom_agent"),
                input_data.get("purpose", ""),
                input_data.get("tools_needed", []),
                input_data.get("triggers", []),
            )
        elif action == "build":
            return {"path": self.build_agent(input_data.get("name", ""))}
        return {"status": "error", "error": f"Unknown action: {action}"}

    # ═══════════════════════════════════════
    # تصميم الوكيل
    # ═══════════════════════════════════════

    def design_agent(
        self,
        name: str,
        purpose: str,
        tools_needed: list = None,
        triggers: list = None
    ) -> dict:
        """يصمّم مواصفات وكيل ويحفظها كـ JSON"""
        try:
            tools_needed = tools_needed or []
            triggers = triggers or []
            safe_name = name.replace(" ", "_").lower()

            # بناء class name
            class_name = "".join(w.capitalize() for w in safe_name.split("_")) + "Agent"

            spec = {
                "name": safe_name,
                "class_name": class_name,
                "description": purpose,
                "tools": tools_needed,
                "triggers": triggers,
                "methods": ["run", "on_trigger", "report"],
                "schedule": self._parse_triggers(triggers),
                "created_at": datetime.utcnow().isoformat(),
                "status": "DESIGNED",
            }

            # حفظ المواصفات
            spec_path = os.path.join(SPECS_DIR, f"{safe_name}.json")
            with open(spec_path, "w", encoding="utf-8") as f:
                json.dump(spec, f, ensure_ascii=False, indent=2)

            self.log(f"Agent designed: {safe_name}")
            return {"status": "success", "spec": spec, "path": spec_path}

        except Exception as e:
            self.log(f"Design failed: {e}", level="ERROR")
            return {"status": "error", "error": str(e)}

    # ═══════════════════════════════════════
    # بناء الوكيل
    # ═══════════════════════════════════════

    def build_agent(self, spec_or_name: str) -> str:
        """من spec JSON → ملف Python كامل"""
        try:
            # تحميل المواصفات
            if os.path.isfile(spec_or_name):
                spec_path = spec_or_name
            else:
                spec_path = os.path.join(SPECS_DIR, f"{spec_or_name}.json")

            if not os.path.exists(spec_path):
                return f"❌ لا يوجد spec لـ '{spec_or_name}'"

            with open(spec_path, "r", encoding="utf-8") as f:
                spec = json.load(f)

            # محاولة توليد بالـ LLM
            code = self._generate_with_llm(spec)
            if not code:
                code = self._generate_from_template(spec)

            # حفظ الملف
            filename = f"{spec['name']}_agent.py"
            filepath = os.path.join(GENERATED_DIR, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code)

            # تحديث المواصفات
            spec["status"] = "BUILT"
            spec["path"] = filepath
            with open(spec_path, "w", encoding="utf-8") as f:
                json.dump(spec, f, ensure_ascii=False, indent=2)

            self.log(f"Agent built: {filepath}")
            self.record_metric("agents_built", self.metrics.get("agents_built", 0) + 1)
            return filepath

        except Exception as e:
            self.log(f"Build failed: {e}", level="ERROR")
            return f"❌ فشل البناء: {e}"

    # ═══════════════════════════════════════
    # التسجيل والاختبار
    # ═══════════════════════════════════════

    def register_agent(self, name: str, auto_start: bool = False) -> bool:
        """يسجّل الوكيل في AgentRegistry"""
        try:
            from core.agent_registry import agent_registry
            filepath = os.path.join(GENERATED_DIR, f"{name}_agent.py")
            if not os.path.exists(filepath):
                return False
            agent_registry.register_from_file(name, filepath)
            self.log(f"Agent registered: {name}")
            return True
        except Exception as e:
            self.log(f"Register failed: {e}", level="ERROR")
            return False

    def test_agent(self, name: str, test_input: dict = None) -> dict:
        """يختبر الوكيل في بيئة معزولة"""
        try:
            import importlib.util
            filepath = os.path.join(GENERATED_DIR, f"{name}_agent.py")
            if not os.path.exists(filepath):
                return {"status": "error", "error": "ملف الوكيل غير موجود"}

            spec = importlib.util.spec_from_file_location(name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # البحث عن الكلاس
            agent_class = None
            for attr in dir(module):
                obj = getattr(module, attr)
                if isinstance(obj, type) and issubclass(obj, BaseAgent) and obj is not BaseAgent:
                    agent_class = obj
                    break

            if not agent_class:
                return {"status": "error", "error": "لم يتم العثور على كلاس يرث BaseAgent"}

            agent = agent_class()
            import time
            start = time.time()
            result = agent.start(test_input or {})
            elapsed = round(time.time() - start, 2)

            return {
                "status": "success",
                "output": result,
                "execution_time": elapsed,
                "agent_status": agent.get_status(),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def export_agent(self, name: str, format: str = "standalone") -> str:
        """يصدّر وكيلاً كملف ZIP"""
        try:
            filepath = os.path.join(GENERATED_DIR, f"{name}_agent.py")
            if not os.path.exists(filepath):
                return f"❌ وكيل '{name}' غير موجود"

            export_dir = os.path.join(BASE_DIR, "storage", "exports")
            os.makedirs(export_dir, exist_ok=True)
            zip_path = os.path.join(export_dir, f"{name}_agent.zip")

            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.write(filepath, f"{name}_agent.py")
                # README
                readme = f"# {name} Agent\nGenerated by NEXUM AgentSmith\n"
                zf.writestr("README.md", readme)
                # requirements
                zf.writestr("requirements.txt", "pyTelegramBotAPI\npython-dotenv\npsutil\n")
                # .env.example
                zf.writestr(".env.example", "TELEGRAM_TOKEN=your_token\nADMIN_ID=your_id\n")

            self.log(f"Agent exported: {zip_path}")
            return zip_path
        except Exception as e:
            return f"❌ فشل التصدير: {e}"

    def list_agents(self) -> list:
        """جميع الوكلاء: specs + built + generated"""
        agents = []
        # من المواصفات
        for f in os.listdir(SPECS_DIR):
            if f.endswith(".json"):
                try:
                    with open(os.path.join(SPECS_DIR, f), "r") as fh:
                        spec = json.load(fh)
                        agents.append({
                            "name": spec.get("name", f),
                            "status": spec.get("status", "UNKNOWN"),
                            "description": spec.get("description", "")[:60],
                            "source": "smith",
                        })
                except Exception:
                    pass
        return agents

    # ═══════════════════════════════════════
    # مولّدات داخلية
    # ═══════════════════════════════════════

    def _generate_with_llm(self, spec):
        """توليد كود الوكيل بالـ LLM"""
        try:
            from services.gemini_service import GeminiService
            svc = GeminiService(os.getenv("GOOGLE_API_KEY"))
            prompt = (
                f"أنشئ ملف Python كامل لوكيل ذكاء اصطناعي.\n\n"
                f"الاسم: {spec['name']}\nالكلاس: {spec['class_name']}\n"
                f"الهدف: {spec['description']}\n"
                f"الأدوات: {spec.get('tools', [])}\n"
                f"المشغّلات: {spec.get('triggers', [])}\n\n"
                "المتطلبات:\n"
                "1. from core.base_agent import BaseAgent\n"
                "2. class يرث BaseAgent مع __init__ و run()\n"
                "3. try/except في كل method مع self.log()\n"
                "4. أعد كود Python فقط بدون شرح — ابدأ بـ import\n"
            )
            res, _ = svc.ask(prompt)
            if res and ("class " in res and "BaseAgent" in res):
                import re
                res = re.sub(r'^```(?:python)?\s*', '', res.strip())
                res = re.sub(r'\s*```$', '', res.strip())
                return res
        except Exception as e:
            self.log(f"LLM generation failed: {e}", level="WARNING")
        return None

    def _generate_from_template(self, spec):
        """توليد من قالب ثابت"""
        name = spec["name"]
        cls = spec["class_name"]
        desc = spec.get("description", "وكيل مخصص")
        tools = spec.get("tools", [])

        tool_code = ""
        if "web_search" in tools:
            tool_code += "\n    def search(self, query):\n        self.log(f'Searching: {query}')\n        return {'results': []}\n"
        if "telegram_broadcast" in tools:
            tool_code += "\n    def broadcast(self, msg):\n        self.log(f'Broadcasting: {msg[:50]}')\n        return True\n"

        return f'''"""
🤖 {cls} — Generated by NEXUM AgentSmith
{desc}
"""
import os, sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(BASE_DIR))  # لاستيراد core

from core.base_agent import BaseAgent


class {cls}(BaseAgent):
    """{desc}"""

    def __init__(self):
        super().__init__(
            name="{name}",
            description="{desc}",
            version="1.0"
        )

    def run(self, input_data: dict) -> dict:
        """التنفيذ الرئيسي"""
        try:
            self.log("Agent running...")
            # TODO: implement main logic
            result = {{"status": "ok", "message": "Agent executed successfully"}}
            self.log(f"Result: {{result}}")
            return result
        except Exception as e:
            self.log(f"Run error: {{e}}", level="ERROR")
            return {{"status": "error", "error": str(e)}}
{tool_code}

# Singleton
agent = {cls}()
'''

    def _parse_triggers(self, triggers):
        """تحليل المشغّلات"""
        schedule = {}
        for t in triggers:
            lower = t.lower() if isinstance(t, str) else ""
            if "ساعة" in lower or "hour" in lower:
                schedule["interval"] = "hourly"
            elif "يوم" in lower or "daily" in lower:
                schedule["interval"] = "daily"
            elif "دقيقة" in lower or "minute" in lower:
                schedule["interval"] = "every_minute"
        return schedule


# Singleton
agent_smith = AgentSmith()
