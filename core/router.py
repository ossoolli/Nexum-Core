import sys
from telebot import TeleBot
from core.middlewares import rate_limit

from handlers import dash_handler, webforge_handler, agents_bots_handler

CALLBACK_ROUTES = {
    "menu": dash_handler.show_menu,
    "wf": webforge_handler.route,
    "ag": agents_bots_handler.route_agents,
    "bt": agents_bots_handler.route_bots,
}

def setup_router(bot: TeleBot):
    """
    تهيئة الموجه المركزي وربطه بنسخة البوت
    """
    @bot.callback_query_handler(func=lambda call: True)
    @rate_limit(cooldown=1.0)
    def central_router(call):
        try:
            # استخراج النطاق (namespace)، مثال: "menu:main" -> "menu"
            namespace = call.data.split(":")[0]
            handler = CALLBACK_ROUTES.get(namespace)
            
            if handler:
                handler(call, bot)
            else:
                # إذا لم يكن هناك handler
                bot.answer_callback_query(call.id, "المسار غير مدعوم حالياً 🚧", show_alert=True)
                
        except Exception as e:
            # معالجة الأخطاء بشكل صامت وتنبيه المستخدم
            print(f"[Router Error] {e}")
            bot.answer_callback_query(call.id, "حدث خطأ غير متوقع ❌", show_alert=True)
        finally:
            # تأكيد استلام الحدث لمنع تعليق واجهة تيليجرام
            try:
                bot.answer_callback_query(call.id)
            except Exception:
                pass
