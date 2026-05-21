from telebot import types
import os
import psutil
from datetime import datetime

# 🔱 Sovereign Dashboard Controller v7.3.0
# =========================================

def handle_dashboard(bot, call):
    data = call.data
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    from core.keyboards import ui_builder

    try:
        # --- القوائم الرئيسية ---
        if data == "menu_runtime" or data == "hw_status":
            show_runtime(bot, chat_id, message_id)
        elif data == "menu_agents" or data == "list_agents":
            show_agents_hub(bot, chat_id, message_id)
        elif data == "menu_protocols":
            show_protocols(bot, chat_id, message_id)
        elif data == "menu_deploy":
            show_deploy(bot, chat_id, message_id)
        elif data == "menu_ai":
            show_ai_brain(bot, chat_id, message_id)
        elif data == "menu_security":
            show_security(bot, chat_id, message_id)
        elif data == "menu_memory":
            show_memory(bot, chat_id, message_id)
        elif data == "menu_docker":
            show_docker(bot, chat_id, message_id)
        elif data == "menu_settings":
            show_settings(bot, chat_id, message_id)
        elif data == "audit_logs" or data == "menu_logs":
            show_logs_preview(bot, chat_id, message_id)
            
        # --- العودة للميكانيكا الأساسية ---
        elif data in ["menu_back", "back_main"]:
            text = "🔱 *NEXUM CORE OS v7.3.0*\n\nمركز التحكم السيادي جاهز."
            bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=ui_builder.build_main_control_plane())
        
        else:
            bot.answer_callback_query(call.id, f"🛠️ القسم [{data}] تحت التجهيز السيادي...")
            
    except Exception as e:
        bot.answer_callback_query(call.id, "❌ خطأ في المعالجة.")
        print(f"Dashboard Error: {e}")

def show_runtime(bot, chat_id, message_id):
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    text = (
        "⚡ *SYSTEM RUNTIME ANALYSIS*\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        f"🖥️ **CPU:** {cpu}% | 🧠 **RAM:** {ram}%\n"
        f"💾 **Disk:** {disk}% | 📡 **Net:** Active\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "✅ جميع العمليات الحيوية تعمل بكفاءة."
    )
    from core.keyboards import ui_builder
    bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=ui_builder.build_runtime_menu())

def show_agents_hub(bot, chat_id, message_id):
    text = "🤖 *AGENTS CONTROL HUB*\n\nإدارة الوكلاء النشطين وتحديد المهام السيادية."
    from core.keyboards import ui_builder
    bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=ui_builder.build_agents_menu())

def show_protocols(bot, chat_id, message_id):
    text = "🧬 *SOVEREIGN PROTOCOLS*\n\nتحميل وتشغيل بروتوكولات الأتمتة المتقدمة."
    from core.keyboards import ui_builder
    bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=ui_builder.build_protocols_menu())

def show_deploy(bot, chat_id, message_id):
    text = "🚀 *DEPLOYMENT GATEWAY*\n\nمزامنة الكود مع GitHub والنشر على السحابة."
    from core.keyboards import ui_builder
    bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=ui_builder.build_deploy_menu())

def show_ai_brain(bot, chat_id, message_id):
    text = "🧠 *AI BRAIN CONSOLE*\n\nالتحكم في أنماط التفكير (Gemini/OpenAI) وتحليل البيانات."
    from core.keyboards import ui_builder
    bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=ui_builder.build_ai_menu())

def show_security(bot, chat_id, message_id):
    text = "🛡️ *SECURITY COMMAND*\n\nمراقبة حواجز الحماية وإدارة مفاتيح الوصول."
    from core.keyboards import ui_builder
    bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=ui_builder.build_security_menu())

def show_memory(bot, chat_id, message_id):
    text = "💾 *CORE MEMORY*\n\nإدارة الذاكرة السياقية وقواعد البيانات المحلية."
    from core.keyboards import ui_builder
    bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=ui_builder.build_memory_menu())

def show_docker(bot, chat_id, message_id):
    text = "🐳 *DOCKER ORCHESTRATION*\n\nإدارة الحاويات والبيئات المعزولة."
    from core.keyboards import ui_builder
    bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=ui_builder.build_docker_menu())

def show_settings(bot, chat_id, message_id):
    text = "⚙️ *SYSTEM SETTINGS*\n\nتعديل بارامترات التشغيل للـ Nexum Core."
    from core.keyboards import ui_builder
    bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=ui_builder.build_settings_menu())

def show_logs_preview(bot, chat_id, message_id):
    log_path = "storage/logs/out.log"
    logs = "لا توجد سجلات حالية."
    try:
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                logs = "".join(f.readlines()[-10:])
    except: pass
    text = f"📜 *AUDIT LOGS*\n\n`<pre>{logs}</pre>`"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_main"))
    bot.edit_message_text(text, chat_id, message_id, parse_mode="HTML", reply_markup=markup)
