import logging
from telebot import types

logger = logging.getLogger("nexum.router")

def setup_router(bot):
    """
    موجه مركز لجميع الـ Callbacks في النظام.
    يوزع المهام على المعالجات المتخصصة بناءً على الـ Namespace.
    """
    
    @bot.callback_query_handler(func=lambda call: True)
    def universal_callback_router(call):
        data = call.data
        user_id = call.from_user.id
        
        # حماية: التحقق من الأدمن
        from nexum.config import config
        if user_id != config.admin_id:
            bot.answer_callback_query(call.id, "🚫 غير مصرح لك.")
            return

        try:
            # 1. توجيه لوحة التحكم (menu_...)
            if data.startswith('menu_'):
                from handlers.dash_handler import handle_dashboard
                handle_dashboard(bot, call)
                
            # 2. توجيه WebForge (wf_...)
            elif data.startswith('wf_'):
                # سيتم معالجتها داخل wf_handler لاحقاً أو هنا
                bot.answer_callback_query(call.id, "🌐 WebForge: قيد التطوير...")
                
            # 3. توجيه الوكلاء (ag_...)
            elif data.startswith('ag_'):
                bot.answer_callback_query(call.id, "🤖 Agents: جاري التحميل...")
                
            # 4. توجيه البوتات (bt_...)
            elif data.startswith('bt_'):
                bot.answer_callback_query(call.id, "🤖 Bot Fleet: جاري الفحص...")

            # 5. التوجيهات القديمة/المباشرة
            elif data == "status":
                from agents.monitor import monitor_agent
                bot.send_message(call.message.chat.id, monitor_agent.get_pulse_report(), parse_mode="HTML")
                bot.answer_callback_query(call.id)
            
            else:
                bot.answer_callback_query(call.id, f"📡 Callback: {data}")
                
        except Exception as e:
            logger.error(f"Routing Error for {data}: {e}")
            bot.answer_callback_query(call.id, "❌ حدث خطأ في التوجيه الداخلي.")
            bot.send_message(call.message.chat.id, f"⚠️ **خطأ راوتر:**\n`<pre>{str(e)}</pre>`", parse_mode="HTML")
