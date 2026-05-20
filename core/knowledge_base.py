"""
Knowledge Base & Skill Manager 🧠
=================================
يسمح للوكلاء باكتساب مهارات جديدة ومعارف وحفظها في التخزين الخارجي
بشكل دائم حتى بعد إعادة التشغيل.
يعتمد حالياً على التخزين الخارجي (JSON/Redis) ويمكن توسيعه بقاعدة بيانات متجهية (Vector DB).
"""
import os
import json
import threading
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class KnowledgeBase:
    def __init__(self, storage_path: str = "storage/knowledge"):
        if not os.path.isabs(storage_path):
            storage_path = os.path.join(BASE_DIR, storage_path)
        self.storage_path = storage_path
        self._lock = threading.Lock()
        
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
            
        self.knowledge_file = os.path.join(self.storage_path, "global_knowledge.json")
        self.skills_file = os.path.join(self.storage_path, "acquired_skills.json")
        
        self._knowledge = self._load(self.knowledge_file)
        self._skills = self._load(self.skills_file)

    def _load(self, path: str) -> dict:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save(self, path: str, data: dict):
        with self._lock:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    # --- إدارة المعرفة (Knowledge / Facts) ---
    def add_fact(self, domain: str, key: str, value: str):
        """إضافة معلومة أو قاعدة في مجال معين"""
        if domain not in self._knowledge:
            self._knowledge[domain] = {}
        self._knowledge[domain][key] = {
            "value": value,
            "learned_at": datetime.now().isoformat()
        }
        self._save(self.knowledge_file, self._knowledge)

    def get_facts(self, domain: str) -> dict:
        """جلب جميع الحقائق في مجال معين لإرسالها للوكيل كسياق"""
        return self._knowledge.get(domain, {})

    # --- إدارة المهارات (Skills / Protocols) ---
    def save_skill(self, skill_name: str, description: str, procedures: list):
        """حفظ مهارة/طريقة تنفيذ جديدة (مثلاً: كيفية نشر الكود على AWS)"""
        self._skills[skill_name] = {
            "description": description,
            "procedures": procedures,  # قائمة بخطوات العمل
            "updated_at": datetime.now().isoformat()
        }
        self._save(self.skills_file, self._skills)

    def get_skill(self, skill_name: str) -> dict:
        return self._skills.get(skill_name, {})

    def list_skills(self) -> list:
        return list(self._skills.keys())

# Singleton
knowledge_base = KnowledgeBase()
