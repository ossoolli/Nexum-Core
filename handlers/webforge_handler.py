from telebot import types
from ui.components import breadcrumbs, create_btn

def get_webforge_markup() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        create_btn("🏠 صفحة هبوط", "wf:landing"),
        create_btn("📊 لوحة تحكم", "wf:dashboard")
    )
    markup.add(
        create_btn("⚡ FastAPI App", "wf:api"),
        create_btn("⚛️ React مبدئي", "wf:react")
    )
    markup.add(
        create_btn("📁 مشاريعي", "wf:list"),
        create_btn("◀️ رجوع", "menu:main")
    )
    return markup

def route(call, bot):
    """
    موجه فرعي داخلي لـ WebForge
    Namespace: "wf"
    """
    action = call.data.split(":")[1]
    
    if action == "main":
        text = (
            breadcrumbs("🏠 الرئيسية", "🌐 المواقع") +
            "🌐 *مدير المواقع والتطبيقات (WebForge)*\n\n"
            "يمكنك بناء مشاريع جديدة أو إدارة مشاريعك الحالية:"
        )
        bot.edit_message_text(
            text, 
            call.message.chat.id, 
            call.message.message_id, 
            parse_mode="Markdown", 
            reply_markup=get_webforge_markup()
        )
    elif action == "landing":
        bot.answer_callback_query(call.id, "سيتم بناء صفحة هبوط...", show_alert=False)
        # TODO: إطلاق الـ FSM لبداية الاستعلام عن تفاصيل الصفحة
    else:
        bot.answer_callback_query(call.id, "تحت التطوير 🚧", show_alert=True)
