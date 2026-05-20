from telebot import TeleBot
from core.middlewares import rate_limit
from handlers import dash_handler, webforge_handler, agents_bots_handler

# خريطة توجيه النطاقات (Namespaces)
CALLBACK_ROUTES = {
    "menu": dash_handler.show_menu,
    "wf":   webforge_handler.route,
    "ag":   agents_bots_handler.route_agents,
    "bt":   agents_bots_handler.route_bots,
    # سيتم إضافة المعالجات الأخرى (mon, st, ch) تباعاً عند اكتمال ملفاتها
}

def setup_router(bot: TeleBot):
    """
    تهيئة الموجه المركزي وربطه بنسخة البوت.
    يعالج جميع ضغطات الأزرار (Callback Queries) بشكل نظامي.
    """
    
    @bot.callback_query_handler(func=lambda call: True)
    @rate_limit(cooldown=0.5)
    def central_router(call):
        try:
            # استخراج النطاق، مثال: "wf:main" -> "wf"
            if ":" not in call.data:
                # إذا كان الزر لا يتبع نظام النطاقات (مثل status القديم)
                from main import handle_callbacks
                return handle_callbacks(call)
                
            namespace = call.data.split(":")[0]
            handler = CALLBACK_ROUTES.get(namespace)
            
            if handler:
                handler(call, bot)
            else:
                # إذا كان المسار غير مسجل، نحاول توجيهه لـ main handler للملائمة
                from main import handle_callbacks
                handle_callbacks(call)
                
        except Exception as e:
            import logging
            logging.error(f"[Router Error] {e}")
            try:
                bot.answer_callback_query(call.id, "حدث خطأ في التوجيه ❌", show_alert=True)
            except: pass
        finally:
            try:
                bot.answer_callback_query(call.id)
            except: pass
