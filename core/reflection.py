import os
import json
import uuid
from datetime import datetime
from threading import Thread

class ReflectionEngine:
    """
    محرك التأمل المعرفي (Cognitive Reflection Engine)
    يحول الوكلاء من كائنات تنفيذية بردود فعل بسيطة (Reactive) إلى وكلاء واعين (Cognitive).
    يقوم بتحليل كل مهمة بعد تنفيذها واستخلاص الدروس في الذاكرة العرضية (Episodic Memory).
    """
    def __init__(self, llm_service=None):
        self.llm = llm_service
        self.memory_dir = os.path.join(os.path.dirname(__file__), "..", "storage", "episodic_memory")
        os.makedirs(self.memory_dir, exist_ok=True)
        
    def set_llm(self, llm_service):
        self.llm = llm_service
        
    def reflect_async(self, task_id, agent_id, action, params, result, error=None, duration=0):
        """تشغيل عملية التأمل في الخلفية لكي لا تتعطل سرعة الأوركستريتور"""
        t = Thread(target=self._deep_reflect, args=(task_id, agent_id, action, params, result, error, duration))
        t.daemon = True
        t.start()
        
    def _deep_reflect(self, task_id, agent_id, action, params, result, error, duration):
        memory_id = f"ep_{uuid.uuid4().hex[:8]}"
        state = "FAILED" if error else "SUCCESS"
        
        lesson = "تم التنفيذ بنجاح ضمن السياق المعطى."
        if error and self.llm:
            try:
                # التأمل الذكي باستخدام Gemini لمعرفة سبب الخطأ
                prompt = f"""
أنت نظام التأمل المعرفي. قام الوكيل {agent_id} بمحاولة تنفيذ الحدث {action}.
المدخلات: {params}
النتيجة: فشل.
الخطأ: {error}

لخص في جملة قصيرة: ما هو الدرس المستفاد لتجنب هذا الخطأ مستقبلاً؟
"""
                response, _ = self.llm.ask(prompt)
                lesson = response.strip()
            except:
                lesson = "حدث خطأ غير متوقع، يتطلب الفحص البشري أو تعديل الأداة."
        elif error:
            lesson = "استثناء أثناء التنفيذ. ابحث عن الأخطاء في المدخلات."
            
        episode = {
            "memory_id": memory_id,
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "task": {
                "id": task_id,
                "action": action,
                "context": params
            },
            "performance": {
                "outcome": state,
                "duration_seconds": round(duration, 2),
                "error_trace": str(error)[:500] if error else None
            },
            "cognition": {
                "lesson_learned": lesson
            }
        }
        
        file_path = os.path.join(self.memory_dir, f"{memory_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(episode, f, ensure_ascii=False, indent=2)
            
        print(f"🧠 [Reflection] Agent '{agent_id}' saved episode {memory_id} (Outcome: {state})")

# Singleton
reflection_engine = ReflectionEngine()
