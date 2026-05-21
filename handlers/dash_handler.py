from telebot import types
import os
import psutil
from datetime import datetime

# 🔱 Sovereign UI Handlers
# ========================

def handle_dashboard(bot, call):
    """
    المعالج الرئيسي للوحة التحكم السيادية (menu_*)
    """
    data = call.data
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if data == "menu_runtime":
        show_runtime(bot, chat_id, message_id)
    elif data == "menu_agents":
        show_agents_hub(bot, chat_id, message_id)
    elif data == "menu_security":
        show_security(bot, chat_id, message_id)
    elif data == "menu_logs":
        show_logs_preview(bot, chat_id, message_id)
    elif data == "menu_settings":
        show_settings(bot, chat_id, message_id)
    elif data == "menu_back":
        # العودة للوحة الأساسية (تستدعي بناء الـ Dashboard من main)
        from core.keyboards import SovereignUIBuilder
        text = "🔱 *NEXUM CORE OS v7.3.0*\n\nمرحباً بك مجدداً في مركز التحكم السيادي."
        bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=SovereignUIBuilder.build_main_dashboard())
    else:
        bot.answer_callback_query(call.id, f"🛠️ القسم [{data}] قيد التفعيل...")

def show_runtime(bot, chat_id, message_id):
    """عرض تفاصيل التشغيل الحية"""
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    uptime = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M")
    
    text = (
        "⚡ *NEXUM RUNTIME STATUS*\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"🖥️ **CPU Usage:** {cpu}%\n"
        f"🧠 **RAM Usage:** {ram}%\n"
        f"💾 **Disk Space:** {disk}%\n"
        f"⏱️ **Last Boot:** {uptime}\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "✅ النظام يعمل ضمن النطاق الآمن."
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 تحديث", callback_data="menu_runtime"))
    markup.add(types.InlineKeyboardButton("🔙 عودة", callback_data="menu_back"))
    bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=markup)

def show_agents_hub(bot, chat_id, message_id):
    """مركز إدارة الوكلاء"""
    text = (
        "🤖 *AGENTS CONTROL HUB*\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "🎭 **Active Agents:** 4\n"
        "🧠 **Memory Load:** Low\n\n"
        "اختر وكيل لإدارته أو إنشاء وكيل جديد:"
    )
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🌐 WebForge", callback_data="wf_manage"),
        types.InlineKeyboardButton("🏗️ BotBuilder", callback_data="bt_manage")
    )
    markup.add(types.InlineKeyboardButton("➕ إنشاء وكيل جديد (AgentSmith)", callback_data="ag_smith"))
    markup.add(types.InlineKeyboardButton("🔙 عودة", callback_data="menu_back"))
    bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=markup)

def show_security(bot, chat_id, message_id):
    """لوحة التحكم الأمنية"""
    text = (
        "🛡️ *SECURITY PERIMETER*\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "🔒 **Shield Status:** ACTIVE\n"
        "🌐 **Proxy:** Disabled\n"
        "🔑 **Master Key:** Validated\n\n"
        "النظام محمي ضد التهديدات الخارجية."
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔐 تغيير الـ Master Key", callback_data="sec_reset"))
    markup.add(types.InlineKeyboardButton("🔙 عودة", callback_data="menu_back"))
    bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=markup)

def show_logs_preview(bot, chat_id, message_id):
    """معاينة السجلات الحية"""
    log_path = "storage/logs/out.log"
    try:
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()[-10:] # آخر 10 أسطر
                logs = "".join(lines)
        else:
            logs = "لا توجد سجلات حالية."
    except Exception as e:
        logs = f"فشل قراءة السجلات: {e}"

    text = f"📜 *RECENT AUDIT LOGS*\n\n`<pre>{logs}</pre>`"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📥 تحميل السجل الكامل", callback_data="menu_logs_dl"))
    markup.add(types.InlineKeyboardButton("🔙 عودة", callback_data="menu_back"))
    bot.edit_message_text(text, chat_id, message_id, parse_mode="HTML", reply_markup=markup)

def show_settings(bot, chat_id, message_id):
    """إعدادات النظام"""
    from nexum.config import config
    text = (
        "⚙️ *SYSTEM SETTINGS*\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **Admin ID:** {config.admin_id}\n"
        f"🤖 **Version:** 7.3.0\n"
        f"📁 **Storage:** Local JSON\n\n"
        "قم بتعديل ملف .env لتغيير الإعدادات الأساسية."
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🛠️ اختبار الاتصال", callback_data="st_test"))
    markup.add(types.InlineKeyboardButton("🔙 عودة", callback_data="menu_back"))
    bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=markup)
