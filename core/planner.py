"""
AI Planner – المخطط الذكي
=======================
يستقبل هدف المستخدم، ويستخدم النماذج اللغوية (LLMs) لتحليل الهدف
إلى مخطط تنفيذ حقيقي (Execution Graph - DAG).
"""
import os
import json
import uuid
from typing import Dict, Any, List
from core.execution_graph import ExecutionGraph, TaskNode


class AIPlanner:
    """يحول الأوامر اللغوية إلى شبكات مهام ذات اعتماديات دقيقة"""
    def __init__(self, gemini_service):
        self.llm = gemini_service

        # قائمة الوكلاء المتاحين لكي يعرف الذكاء الاصطناعي من يستطيع تنفيذ المهام
        self.AVAILABLE_AGENTS = """
        المتاحون:
        1. agent_frontend: مناسب لبناء واجهات React، HTML، CSS وتنسيق الأكواد.
        2. agent_docker: مناسب לבناء حاويات، تشغيل أوامر النظام، إدارة السيرفر.
        3. agent_github: مناسب لإنشاء المستودعات، رفع الكود، والنشر الآلي.
        4. agent_monitor: مناسب لفحص حالة النظام والصحة.
        """

    def generate_execution_graph(self, goal: str, protocol_id: str) -> ExecutionGraph:
        """يولد مسار تنفيذ (Graph) من خلال الذكاء الاصطناعي بناءً على الهدف والأدوات المتاحة"""
        
        from core.tool_registry import tool_registry
        tools_schema = tool_registry.get_all_tools_schema()
        
        prompt = f"""
أنت "العقل المدبر" (Mastermind) لنظام التشغيل السيادي NEXUM OS. 
مهمتك هي العمل باستقلالية كاملة (Full Autonomy) مثل وكلاء Antigravity و Devin.

تنبيه معماري حرج: أنت تعمل على سيرفر حقيقي، والمسار الفعلي الجذري للملفات الحالية هو: {os.path.dirname(os.path.dirname(__file__))}
ممنوع اختراع مسارات وهمية. استخدم الأدوات للبحث والتعديل في هذا المسار الفعلي حصراً.

الهدف المطلوب: {goal}

معلومات الوكلاء المتاحين للقوة الضاربة:
{self.AVAILABLE_AGENTS}

الأدوات المتاحة (Tools Schema):
{json.dumps(tools_schema, ensure_ascii=False, indent=2)}

تعليمات السيادة التنفيذية:
1. فكك الهدف إلى مهام تقنية دقيقة مترابطة (Dependencies).
2. استخدم `run_host_terminal` لتثبيت المكتبات، فحص الملفات، وتشغيل العمليات.
3. استخدم `write_file` لبناء الهياكل البرمجية الكاملة.
4. إذا واجهت خطأ، اعتمد على نظام الـ (Self-Correction) من خلال الـ Retries.

أعد الرد بصيغة JSON فقط:
{{
  "tasks": [
    {{
      "task_id": "step_1",
      "agent_id": "agent_docker",
      "action": "run_host_terminal",
      "params": {{"command": "الأمر الفعلي"}},
      "retries": 3,
      "dependencies": []
    }}
  ]
}}
"""
        
        # استدعاء خدمة Gemini (يجب أن ترجع نص الـ JSON)
        print("🧠 [Planner] Generating Execution Graph for goal...")
        response_text, _ = self.llm.ask(prompt)
        
        # استخراج كتلة الـ JSON باستخدام التعابير النمطية لتجاهل أي نص حواري يسبقه
        import re
        match = re.search(r'(\{.*\})', response_text, re.DOTALL)
        if match:
            cleaned_text = match.group(1)
        else:
            cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
        
        try:
            plan_data = json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            raise Exception(f"فشل المخطط في توليد JSON صالح: {cleaned_text}") from e

        # تحويل الـ JSON إلى Execution Graph فعلي
        graph = ExecutionGraph(protocol_id=protocol_id)
        
        tasks_config = plan_data.get("tasks", [])
        if not tasks_config:
            raise Exception("لم يتم توليد أي مهام للهدف المذكور.")
            
        for task_conf in tasks_config:
            node = TaskNode(
                task_id=task_conf["task_id"],
                agent_id=task_conf["agent_id"],
                action=task_conf["action"],
                params=task_conf.get("params", {}),
                retries=task_conf.get("retries", 2)
            )
            
            for dep in task_conf.get("dependencies", []):
                node.add_dependency(dep)
                
            graph.add_node(node)
            
        from core.yaml_compiler import compile_graph_to_yaml
        print(f"📄 [Protocol Compiler] Compiling Blueprint {protocol_id}.yaml ...")
        compile_graph_to_yaml(graph, "latest_execution")
            
        return graph
