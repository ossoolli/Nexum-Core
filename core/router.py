import sys
import logging
from telebot import TeleBot
from core.middlewares import rate_limit

logger = logging.getLogger("nexum.router")

def setup_router(bot: TeleBot):
    """
    تهيئة الموجه المركزي وربطه بنسخة البوت.
    هذا يجمع الحبال المفقودة في v7.2.1.
    """
    
    @bot.callback_query_handler(func=lambda call: True)
    @rate_limit(cooldown=1.0)
    def central_router(call):
        try:
            # هنا يتم الاستيراد بشكل متأخر لتجنب Circular Imports
            from main import handle_callbacks
            handle_callbacks(call)
        except Exception as e:
            logger.error(f"[Router Error] {e}")
            try:
                bot.answer_callback_query(call.id, "حدث خطأ في الموجه ❌", show_alert=True)
            except: pass
