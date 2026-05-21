"""
core/execution_engine.py
القلب الجديد — يستقبل هدفاً وينفذه بأدوات حقيقية مع تقرير حي
"""
import json
import re
from core.file_agent import file_agent
from core.shell_agent import shell_agent
from core.stream_reporter import StreamReporter
from core.verifier import verifier
from core.fs_control import fs_control
from core.fs_navigator import fs_navigator
from core.fs_search import fs_search
from core.fs_diff import fs_diff

PLAN_PROMPT_TEMPLATE = """
أنت مخطط تنفيذي دقيق. حوّل الطلب التالي لخطة JSON قابلة للتنفيذ فوراً.

الطلب: {goal}

قواعد صارمة:
1. أعد JSON فقط — لا شرح، لا نص إضافي
2. كل خطوة لها: id, type, description, params
3. الأنواع المتاحة: read_file, write_file, edit_file, run_shell, run_python, install_package, verify_file, list_workspace, fs_read, fs_write, fs_edit, fs_tree, fs_search_content
4. params يجب أن تكون كاملة وقابلة للتنفيذ مباشرة
5. أضف خطوة verify في النهاية دائماً

تنسيق الخطة:
{{
  "title": "عنوان الخطة",
  "steps": [
    {{
      "id": 1,
      "type": "fs_read",
      "description": "قراءة ملف الكود",
      "params": {{
        "path": "main.py"
      }}
    }},
    {{
      "id": 2,
      "type": "fs_edit",
      "description": "تعديل نص في الملف",
      "params": {{
        "path": "main.py",
        "old_text": "v7.4",
        "new_text": "v7.5"
      }}
    }}
  ]
}}
"""

class ExecutionEngine:
    def __init__(self, gemini_service=None):
        self._gemini = gemini_service

    def set_gemini(self, svc):
        self._gemini = svc

    def _get_plan(self, goal: str) -> dict:
        """يطلب من Gemini خطة تنفيذية JSON"""
        if not self._gemini:
            raise RuntimeError("Gemini غير متصل بـ ExecutionEngine")

        prompt = PLAN_PROMPT_TEMPLATE.format(goal=goal)
        response, _ = self._gemini.ask(prompt)

        # استخرج JSON من الرد
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if not json_match:
            raise ValueError(f"لم يعد Gemini خطة JSON صالحة. الرد: {response[:200]}")

        return json.loads(json_match.group())

    def _execute_step(self, step: dict, reporter: StreamReporter) -> dict:
        """ينفذ خطوة واحدة من الخطة"""
        stype = step.get("type")
        params = step.get("params", {})
        desc = step.get("description", stype)

        reporter.step("⚙️", f"تنفيذ: {desc}", "running")

        result = None

        if stype == "read_file":
            result = file_agent.read_file(params["path"])

        elif stype == "write_file":
            result = file_agent.write_file(params["path"], params["content"])

        elif stype == "edit_file":
            result = file_agent.edit_file(params["path"], params["old_text"], params["new_text"])

        elif stype == "create_python_module":
            result = file_agent.create_python_module(params["name"], params["content"])

        elif stype == "run_shell":
            def on_line(line):
                if line.strip():
                    reporter.step("📟", line[:100], "info")

            result = shell_agent.execute(
                params["cmd"],
                cwd=params.get("cwd"),
                timeout=params.get("timeout", 30),
                stream_callback=on_line
            )

        elif stype == "run_python":
            lines_collected = []
            def on_line(line):
                lines_collected.append(line)
                if line.strip():
                    reporter.step("🐍", f"→ {line[:80]}", "info")

            result = shell_agent.run_python(
                params["code"],
                filename=params.get("filename"),
                stream_callback=on_line
            )

        elif stype == "install_package":
            result = shell_agent.install_package(params["package"])

        elif stype == "verify_file":
            exists = verifier.file_exists(params["path"])
            result = {"success": exists, "verified": exists, "path": params["path"]}

        elif stype == "list_workspace":
            result = file_agent.list_workspace()

        # ─── أنواع جديدة لـ FileSystem Control ───

        elif stype == "fs_read":
            result = fs_control.read_file(
                params["path"],
                start_line=params.get("start_line"),
                end_line=params.get("end_line")
            )

        elif stype == "fs_write":
            result = fs_control.write_file(params["path"], params["content"])

        elif stype == "fs_edit":
            result = fs_control.replace_text(
                params["path"],
                params["old_text"],
                params["new_text"],
                params.get("all_occurrences", False)
            )

        elif stype == "fs_insert":
            result = fs_control.insert_lines(
                params["path"],
                params.get("after_line", -1),
                params["content"]
            )

        elif stype == "fs_delete_lines":
            result = fs_control.delete_lines(
                params["path"],
                params["start_line"],
                params["end_line"]
            )

        elif stype == "fs_move":
            result = fs_control.move(params["src"], params["dst"], params.get("overwrite", False))

        elif stype == "fs_copy":
            result = fs_control.copy(params["src"], params["dst"], params.get("overwrite", False))

        elif stype == "fs_rename":
            result = fs_control.rename(params["path"], params["new_name"])

        elif stype == "fs_delete":
            result = fs_control.delete(params["path"], params.get("force", False))

        elif stype == "fs_compress":
            result = fs_control.compress(params["path"], params.get("output_name"), params.get("format", "zip"))

        elif stype == "fs_extract":
            result = fs_control.extract(params["path"], params.get("destination"))

        elif stype == "fs_tree":
            res_tree = fs_navigator.tree(params.get("path"), params.get("max_depth", 3))
            result = {"success": True, "data": res_tree} if res_tree.get("success") else res_tree

        elif stype == "fs_search_name":
            res_search = fs_search.by_name(params["pattern"], params.get("root"))
            result = {"success": True, "data": res_search}

        elif stype == "fs_search_content":
            res_grep = fs_search.by_content(params["query"], params.get("root"))
            result = {"success": True, "data": res_grep}

        elif stype == "fs_diff":
            res_diff = fs_diff.diff_files(params["path_a"], params["path_b"])
            result = {"success": True, "data": res_diff} if res_diff.get("success") else res_diff

        elif stype == "fs_sync":
            res_sync = fs_diff.sync_dirs(params["src"], params["dst"], params.get("direction", "a_to_b"))
            result = {"success": res_sync.get("success"), "data": res_sync}

        else:
            result = {"success": False, "error": f"نوع غير معروف: {stype}"}

        # تحديث الخطوة بالنتيجة
        if result and result.get("success", result.get("status") == "success"):
            reporter.step("✅", f"اكتمل: {desc}", "done")
        else:
            error = result.get("error", result.get("output", "خطأ غير معروف")) if result else "لا نتيجة"
            reporter.step("❌", f"فشل: {desc} — {str(error)[:80]}", "error")

        return result or {}

    def execute_goal(self, goal: str, bot=None, chat_id: int = None) -> dict:
        """
        ينفذ هدفاً كاملاً:
        1. يطلب خطة من Gemini
        2. يُنشئ reporter
        3. ينفذ كل خطوة
        4. يُبلّغ بالنتيجة الكاملة
        """
        reporter = StreamReporter()
        if bot and chat_id:
            reporter.init(bot, chat_id)
            reporter.start(f"NEXUM — تنفيذ: {goal[:50]}")

        results = []
        plan = None

        try:
            reporter.step("🧠", "جاري التخطيط عبر Gemini...", "running")
            plan = self._get_plan(goal)
            title = plan.get("title", "خطة تنفيذية")
            steps = plan.get("steps", [])
            reporter.step("📋", f"الخطة: {title} ({len(steps)} خطوات)", "info")

            for step in steps:
                step_result = self._execute_step(step, reporter)
                results.append({
                    "step": step.get("id"),
                    "type": step.get("type"),
                    "desc": step.get("description"),
                    "result": step_result
                })

                # وقف عند فشل حرج
                if not step_result.get("success", step_result.get("status") == "success"):
                    if step.get("critical", False):
                        reporter.finish(
                            f"فشل في الخطوة {step['id']}: {step['description']}",
                            success=False
                        )
                        return {"status": "failed", "plan": plan, "results": results}

            # ملخص نهائي
            done = sum(1 for r in results if r["result"].get("success", r["result"].get("status") == "success"))
            total = len(results)
            reporter.finish(
                f"اكتملت {done}/{total} خطوة بنجاح",
                success=(done == total)
            )

            return {"status": "completed", "plan": plan, "results": results, "done": done, "total": total}

        except Exception as e:
            reporter.finish(f"خطأ غير متوقع: {str(e)}", success=False)
            return {"status": "error", "error": str(e), "plan": plan, "results": results}


execution_engine = ExecutionEngine()
