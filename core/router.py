import logging
from telebot import types

logger = logging.getLogger("nexum.router")

def setup_router(bot):
    """
    موجه مركزي شامل (v7.5.1) - النسخة المفتوحة
    تم فك الارتباط بـ main.py لمنع الـ circular imports
    """
    
    @bot.callback_query_handler(func=lambda call: True)
    def universal_callback_router(call):
        data = call.data
        
        try:
            from handlers.dash_handler import handle_dashboard
            
            # معالجة واجهات التحكم الرئيسية
            if any(data.startswith(prefix) for prefix in ['menu_', 'rt_', 'ag_', 'pr_', 'dp_', 'ai_', 'sec_', 'mem_', 'dk_', 'set_', 'hw_', 'back_', 'cloud_', 'setmod_', 'settheme_', 'confirm_', 'agent_']):
                handle_dashboard(bot, call)
                
            elif data.startswith('agctl_'):
                bot.answer_callback_query(call.id, "🎭 جاري التحكم بالوكيل...")
                
            elif data == "audit_logs":
                handle_dashboard(bot, call)
            
            else:
                bot.answer_callback_query(call.id, f"📡 Callback: {data}")
                
        except Exception as e:
            logger.error(f"Routing Error for {data}: {e}")
            bot.answer_callback_query(call.id, "❌ خطأ توجيه.")
            bot.send_message(call.message.chat.id, f"⚠️ **خطأ راوتر:**\n`<pre>{str(e)}</pre>`", parse_mode="HTML")

def register_legacy_handler(bot, handler_func):
    """يسمح لـ main.py بتسجيل معالج خاص للـ callbacks القديمة دون استيراد متبادل"""
    @bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_') or call.data.startswith('cancel_'))
    def legacy_wrapper(call):
        handler_func(call)
