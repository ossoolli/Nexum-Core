# -*- coding: utf-8 -*-
"""
core/memory_local.py
المستودع المركزي الآمن وبوابة الذاكرة الموحدة لنظام Nexum Pro (v7.2.5)
=========================================================================
- دمج ذاكرة سياق الدردشة الطويلة (LongTermMemory) وذاكرة مؤشرات النظام وتخزين التطبيقات.
- فرض بروتوكول الحفظ الذري (Atomic Writes) لتأمين سلامة ملفات الـ JSON ومنع التلف.
- تأمين تزامن الخيوط البرمجية المتعددة (Thread-Safe Context Management) باستخدام أقفال المزامنة.
- التوافقية الكاملة والرجعية مع الاستدعاءات القديمة للدوال البرمجية الحرة.
"""

import os
import json
import uuid
import threading
from datetime import datetime
from typing import Optional, List, Dict, Any

# تحديد مسار المشروع الأساسي بشكل تلقائي وآمن
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AtomicJSONStore:
    """مخزن بيانات ذري معزول يدير عمليات القراءة والكتابة للـ JSON مع حماية ضد تلف البيانات."""

    def __init__(self, filepath: str):
        self.filepath = os.path.realpath(filepath)
        self.lock = threading.Lock()
        self._ensure_directory()

    def _ensure_directory(self):
        directory = os.path.dirname(self.filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def load(self, default_factory) -> Any:
        """قراءة آمنة لملف الـ JSON مع معالجة الأخطاء والعودة لقيمة افتراضية عند التلف."""
        with self.lock:
            try:
                if os.path.exists(self.filepath):
                    with open(self.filepath, 'r', encoding='utf-8') as f:
                        return json.load(f)
            except Exception as e:
                print(f"[Secure Memory Error] Failed to read database from '{self.filepath}': {e}")
            return default_factory()

    def save(self, data: Any) -> bool:
        """حفظ البيانات برمجياً باستخدام آلية الكتابة المؤقتة والاستبدال الذري التام (Atomic Overwrite)."""
        with self.lock:
            temp_file = None
            try:
                os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
                # إنشاء ملف مؤقت فريد بجانب الملف الأصلي لمنع تداخل عمليات الحفظ
                temp_file = self.filepath + f".{uuid.uuid4().hex[:8]}.tmp"

                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)

                # استبدال الملف المؤقت بالملف الأصلي بشكل ذري على مستوى نظام التشغيل
                os.replace(temp_file, self.filepath)
                return True
            except Exception as e:
                print(f"[Secure Memory Error] Atomic database write failed on '{self.filepath}': {e}")
                # محاولة مسح الملف المؤقت إن وجد لمنع تراكم الملفات التالفة
                if temp_file and os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except OSError:
                        pass
                return False


class LongTermMemory:
    """إدارة ذاكرة سياق الحوار الطويل للمستخدمين لتمكين المعالج العصبي من التذكر المستمر."""

    def __init__(self, path: str):
        self.store = AtomicJSONStore(path)

    def save_context(self, user_id: int, content: str, role: str = "user") -> None:
        """حفظ سياق الحوار الحالي بشكل آمن ومزامنة وتحديد حجم الحوار لمنع استهلاك التوكنات."""
        data = self.store.load(dict)
        key = str(user_id)
        if key not in data:
            data[key] = []

        # قص الرسائل الطويلة لمنع تضخم الذاكرة
        content = content[:2000] if content else ""

        data[key].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

        # حصر سياق الحوار بأحدث 50 رسالة فقط لحماية أداء وقنوات الـ LLM
        data[key] = data[key][-50:]
        self.store.save(data)

    def get_context(self, user_id: int) -> list:
        """استعادة وتدقيق وتحويل سياق الحوار التاريخي للصيغة المطلوبة لمعالجات Gemini."""
        data = self.store.load(dict)
        history = []
        valid_roles = {"user", "model"}
        last_role = None

        for msg in data.get(str(user_id), []):
            role = msg.get("role", "user")
            # تحويل الدور assistant ديناميكياً لدور model المتوافق مع Gemini API
            if role == "assistant":
                role = "model"

            if role not in valid_roles:
                continue

            # تجنب تكرار نفس الدور متتالياً (متطلب Gemini API)
            if role == last_role and history:
                history[-1]["parts"][0]["text"] += "\n" + msg.get("content", "")
                continue

            history.append({
                "role": role,
                "parts": [{"text": msg.get("content", "")}]
            })
            last_role = role

        return history

    def clear_context(self, user_id: int) -> None:
        """تصفير ومسح سياق الحوار الطويل للمستخدم بالكامل."""
        data = self.store.load(dict)
        data.pop(str(user_id), None)
        self.store.save(data)


class SystemMemoryStore:
    """إدارة ذاكرة النظام والمؤشرات وقواعد بيانات التطبيقات والوكلاء المسجلين."""

    def __init__(self, path: str):
        self.store = AtomicJSONStore(path)

    def load(self) -> dict:
        """تحميل مؤشرات وحالات السيرفر والتطبيقات."""
        return self.store.load(lambda: {"indicators": {}, "apps": []})

    def save(self, data: dict) -> None:
        """حفظ وتحديث السجلات وحالات التطبيقات ذرياً."""
        self.store.save(data)


# ─── 1. تهيئة قنوات التخزين الفردية للمشروع (Sovereign Singletons) ───
context_memory = LongTermMemory(os.path.join(BASE_DIR, "storage", "memory", "context.json"))
system_memory = SystemMemoryStore(os.path.join(BASE_DIR, "registry", "system_memory.json"))


# ─── 2. دوال التوافق التام والرجعي لتسهيل عمل الأكواد القديمة ───
def save_memory(data: dict) -> None:
    """دالة حرة متوافقة رجعياً لحفظ مؤشرات النظام والـ Indicators."""
    system_memory.save(data)


def load_memory() -> dict:
    """دالة حرة متوافقة رجعياً لتحميل سجلات وحالات التطبيقات الفعالة بالنظام."""
    return system_memory.load()
