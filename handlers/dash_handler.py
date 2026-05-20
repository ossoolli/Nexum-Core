from telebot import types
from ui.components import breadcrumbs, create_btn
from ui.messages import UIMessage

def get_main_menu_markup() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # الصف 1
    markup.add(
        create_btn("🌐 المواقع", "wf:main"),
        create_btn("🤖 الوكلاء", "ag:main")
    )
    # الصف 2
    markup.add(
        create_btn("🤖 البوتات", "bt:main"),
        create_btn("📢 القنوات", "ch:main")
    )
    # الصف 3
    markup.add(
        create_btn("📊 المراقبة", "mon:main"),
        create_btn("⚙️ الإعدادات", "st:main")
    )
    return markup

def show_menu(call, bot):
    """
    تحديث رسالة التيليجرام الحالية لتصبح هي القائمة الرئيسية
    المسار: menu:main
    """
    text = (
        breadcrumbs("🏠 الرئيسية") +
        "🔱 *NEXUM CORE OS* جاهز\n\nاختر من القائمة للتحكم بالنظام:"
    )
    bot.edit_message_text(
        text, 
        call.message.chat.id, 
        call.message.message_id, 
        parse_mode="Markdown", 
        reply_markup=get_main_menu_markup()
    )
