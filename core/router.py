import logging
from telebot import types

logger = logging.getLogger("nexum.router")

def setup_router(bot):
    """
    موجه مركزي شامل (v7.3.0) - النسخة المفتوحة
    تم إلغاء قيود الأدمن بناءً على طلب المستخدم.
    """
    
    @bot.callback_query_handler(func=lambda call: True)
    def universal_callback_router(call):
        data = call.data
        user_id = call.from_user.id
        
        # تم إلغاء حماية الأدمن للسماح للجميع بالتحكم
        # from nexum.config import config
        # if user_id != config.admin_id:
        #     bot.answer_callback_query(call.id, "🚫 غير مصرح لك.")
        #     return

        try:
            from handlers.dash_handler import handle_dashboard
            
            if any(data.startswith(prefix) for prefix in ['menu_', 'rt_', 'ag_', 'pr_', 'dp_', 'ai_', 'sec_', 'mem_', 'dk_', 'set_', 'hw_', 'back_']):
                handle_dashboard(bot, call)
                
            elif data.startswith('agctl_'):
                bot.answer_callback_query(call.id, "🎭 جاري التحكم بالوكيل...")
                
            elif data.startswith('confirm_') or data.startswith('cancel_'):
                from main import handle_legacy_callbacks
                handle_legacy_callbacks(call)

            elif data == "audit_logs":
                handle_dashboard(bot, call)
            
            else:
                bot.answer_callback_query(call.id, f"📡 Callback: {data}")
                
        except Exception as e:
            logger.error(f"Routing Error for {data}: {e}")
            bot.answer_callback_query(call.id, "❌ خطأ توجيه.")
            bot.send_message(call.message.chat.id, f"⚠️ **خطأ راوتر:**\n`<pre>{str(e)}</pre>`", parse_mode="HTML")
