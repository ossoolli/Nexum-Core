from telebot import types
from ui.components import breadcrumbs, create_btn

def get_agents_markup() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        create_btn("🎨 صمّم وكيل", "ag:design"),
        create_btn("📋 وكلائي", "ag:list")
    )
    markup.add(
        create_btn("▶️ تشغيل", "ag:run"),
        create_btn("⏸ إيقاف", "ag:pause")
    )
    markup.add(
        create_btn("◀️ رجوع", "menu:main")
    )
    return markup

def get_bots_markup() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        create_btn("➕ بوت جديد", "bt:new"),
        create_btn("📋 بوتاتي", "bt:list")
    )
    markup.add(
        create_btn("📡 البث للكل", "bt:broadcast"),
        create_btn("📊 إحصاءات", "bt:stats")
    )
    markup.add(
        create_btn("◀️ رجوع", "menu:main")
    )
    return markup

def route_agents(call, bot):
    """
    موجه فرعي للوكلاء
    Namespace: "ag"
    """
    action = call.data.split(":")[1]
    
    if action == "main":
        text = (
            breadcrumbs("🏠 الرئيسية", "🤖 الوكلاء") +
            "🤖 *إدارة وكلاء الذكاء الاصطناعي (Agents)*\n\n"
            "مساحة العمل الخاصة بوكلائك الشخصيين:"
        )
        bot.edit_message_text(
            text, 
            call.message.chat.id, 
            call.message.message_id, 
            parse_mode="Markdown", 
            reply_markup=get_agents_markup()
        )
    else:
        bot.answer_callback_query(call.id, "تحت التطوير 🚧", show_alert=True)

def route_bots(call, bot):
    """
    موجه فرعي لأطول البوتات
    Namespace: "bt"
    """
    action = call.data.split(":")[1]
    
    if action == "main":
        text = (
            breadcrumbs("🏠 الرئيسية", "🤖 البوتات") +
            "🤖 *أسطول البوتات (Bot Fleet)*\n\n"
            "تحكم في جميع بوتات التيليجرام الخاصة بك المشغلة حالياً:"
        )
        bot.edit_message_text(
            text, 
            call.message.chat.id, 
            call.message.message_id, 
            parse_mode="Markdown", 
            reply_markup=get_bots_markup()
        )
    else:
        bot.answer_callback_query(call.id, "تحت التطوير 🚧", show_alert=True)
