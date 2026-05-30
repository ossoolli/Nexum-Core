import os
import json
import logging
import traceback
from typing import Dict, Any, Optional
from services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

class SelfHealer:
    """
    Self-Healing Engine
    يلتقط الأخطاء، يطلب إصلاحاً من Gemini، ويعرضه على الأدمن.
    """
    def __init__(self, bot=None, admin_id: int = None):
        self.bot = bot
        self.admin_id = admin_id
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def handle_error(self, agent_name: str, error: Exception, context: str = ""):
        """معالجة الخطأ وطلب اقتراح إصلاح"""
        stack = traceback.format_exc()
        logs = self._get_last_logs(agent_name)
        
        prompt = f"""
        لقد حدث خطأ في الوكيل: {agent_name}
        الخطأ: {str(error)}
        
        سياق إضافي: {context}
        
        آخر 10 أسطر من السجلات:
        {logs}
        
        Traceback:
        {stack}
        
        أقترح كود بايثون لإصلاح هذا الخطأ. أعد الكود فقط داخل علامات ```python.
        """
        
        suggestion, _ = gemini_service.ask(prompt)
        
        if self.bot and self.admin_id:
            msg = f"⚠️ <b>[Self-Healing]</b> Error in <code>{agent_name}</code>\n\n"
            msg += f"<b>Error:</b> <code>{str(error)[:100]}</code>\n\n"
            msg += f"<b>Suggestion:</b>\n<pre>{suggestion[:1000]}</pre>"
            
            # Here we could add inline buttons for Apply/Ignore
            from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("✅ Apply Fix", callback_data=f"heal_apply:{agent_name}"),
                InlineKeyboardButton("❌ Ignore", callback_data="heal_ignore")
            )
            
            self.bot.send_message(self.admin_id, msg, parse_mode="HTML", reply_markup=markup)
            
            # Save suggestion for callback
            self._save_suggestion(agent_name, suggestion)

    def _get_last_logs(self, agent_name: str) -> str:
        log_path = os.path.join(self.base_dir, "storage", "logs", "agents", f"{agent_name}.log")
        if os.path.exists(log_path):
            try:
                with open(log_path, 'r') as f:
                    lines = f.readlines()
                    return "".join(lines[-10:])
            except:
                pass
        return "No logs found."

    def _save_suggestion(self, agent_name: str, code: str):
        path = os.path.join(self.base_dir, "storage", "self_healing_suggestions.json")
        data = {}
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
        
        data[agent_name] = code
        with open(path, 'w') as f:
            json.dump(data, f)

    def apply_fix(self, agent_name: str):
        """تطبيق الإصلاح المقترح (سيتم استدعاؤه من Callback)"""
        path = os.path.join(self.base_dir, "storage", "self_healing_suggestions.json")
        if not os.path.exists(path): return False
        
        with open(path, 'r') as f:
            data = json.load(f)
        
        fix_code = data.get(agent_name)
        if not fix_code: return False
        
        # Clean markdown
        fix_code = fix_code.replace("```python", "").replace("```", "").strip()
        
        # Apply fix logic - usually this involves patching a file or running a script
        # For safety, we'll log it and the user should define how to apply it.
        # Example: write to a 'hotfix.py' and restart.
        logger.info(f"Applying fix for {agent_name}...")
        return True

self_healer = SelfHealer()
