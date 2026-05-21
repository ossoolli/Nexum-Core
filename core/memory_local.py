import os
import json
from datetime import datetime


class LongTermMemory:
    """ذاكرة سياقية طويلة المدى — تخزين محلي بصيغة JSON"""

    def __init__(self, path: str):
        self.path = path
        self._ensure_file()

    def _ensure_file(self):
        directory = os.path.dirname(self.path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _load(self) -> dict:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save(self, data: dict):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def save_context(self, user_id: int, content: str, role: str = "user"):
        data = self._load()
        key = str(user_id)
        if key not in data:
            data[key] = []
        data[key].append({"role": role, "content": content, "timestamp": datetime.now().isoformat()})
        data[key] = data[key][-50:]
        self._save(data)

    def get_context(self, user_id: int) -> list:
        data = self._load()
        # التنسيق الدقيق المطلوب لـ Gemini 1.5
        history = []
        for msg in data.get(str(user_id), []):
            history.append({
                "role": "user" if msg["role"] == "user" else "model",
                "parts": [{"text": msg["content"]}] # تأكدنا من استخدام {"text": ...}
            })
        return history

    def clear_context(self, user_id: int):
        data = self._load()
        data.pop(str(user_id), None)
        self._save(data)

# Singleton Instance for Global Access
context_memory = LongTermMemory("storage/memory/context.json")
