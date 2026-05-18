"""
AI Planner – المخطط الذكي
=======================
يستقبل هدف المستخدم، ويستخدم النماذج اللغوية (LLMs) لتحليل الهدف
إلى مخطط تنفيذ حقيقي (Execution Graph - DAG).
"""
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
        """يولد مسار تنفيذ (Graph) من خلال الذكاء الاصطناعي بناءً على الهدف"""
        
        prompt = f"""
أنت مهندس أنظمة موزع لـ منصة NEXUM PRIME (نظام تشغيل وكلاء سيادي).
وظيفتك تفكيك الهدف التالي إلى مجموعة مهام متسلسلة (DAG) ليقوم الوكلاء بتنفيذها.

الهدف: {goal}

معلومات الوكلاء:
{self.AVAILABLE_AGENTS}

قم بإرجاع مسار التنفيذ بصيغة JSON حصراً، ويجب أن تتوافق تماماً مع هذا الهيكل:
{{
  "tasks": [
    {{
      "task_id": "string (unique)",
      "agent_id": "string (اختر من الوكلاء المتاحين)",
      "action": "string (اسم الفعل, مثلا: init_project, build_image, deploy)",
      "params": {{}}, // أي بيانات إضافية
      "retries": 2, // عدد محاولات الإعادة المسموح بها في حال الفشل
      "dependencies": [] // قائمة بـ task_ids التي يجب أن تنتهي قبل أن تبدأ هذه المهمة
    }}
  ]
}}

ملاحظة هامة جداً:
- أعد JSON فقط دون أي نصوص إضافية، دون علامات Markdown (```json).
- تأكد أن الـ dependencies لا تحتوي على دورات مغلقة (No Circular Definitions).
"""
        
        # استدعاء خدمة Gemini (يجب أن ترجع نص الـ JSON)
        print("🧠 [Planner] Generating Execution Graph for goal...")
        response_text = self.llm.ask(prompt)
        
        # تنظيف الرد تحسباً لأي زوائد Markdown
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
            
        return graph
