# -*- coding: utf-8 -*-
import os
import telebot
from nexum.config import config
from core.executive_agent import executive_agent

# 2. ─── المحركات المركزية ───
from services.gemini_service import gemini_service
from core.memory_local import context_memory
from core.execution_engine import execution_engine
from core.file_agent import file_agent
from core.inter_bot_protocol import inter_bot_protocol
from core.keyboards import SovereignUIBuilder
from core.router import setup_router
from nexum.cloud.cloud_agent import cloud_agent

# تهيئة البوت
if not config:
    print("❌ Critical: Config failed to load. Check credentials.txt")
    exit(1)

bot = telebot.TeleBot(config.telegram_token)
ui_builder = SovereignUIBuilder()
ADMIN_ID = config.admin_id

@bot.message_handler(func=lambda msg: msg.from_user.id == ADMIN_ID and (msg.text.startswith('$ ') or msg.text.startswith('cmd ')))
def remote_terminal_executor(msg):
    try:
        cmd = msg.text.split(' ', 1)[1]
        import subprocess
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=45)
        output = result.stdout if result.stdout else result.stderr
        bot.send_message(msg.chat.id, f"💻 <b>[Terminal Output]:</b>\n<pre>{output if output else 'Executed.'}</pre>", parse_mode="HTML")
    except Exception as e:
        bot.send_message(msg.chat.id, f"❌ <b>[Shell_Error]:</b>\n<code>{str(e)}</code>", parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == 'invoke_swarm')
def interactive_swarm_trigger(call):
    msg = bot.send_message(call.message.chat.id, "📥 <b>[Swarm_Ready]:</b> اكتب مأموريتك المخصصة لمجلس الحكماء:", parse_mode="HTML")
    bot.register_next_step_handler(msg, process_custom_swarm_mission)

def process_custom_swarm_mission(msg):
    user_prompt = msg.text
    status_msg = bot.send_message(msg.chat.id, "⚙️ <b>[Swarm_Processing]:</b> جاري تشغيل مأموريتك المخصصة...", parse_mode="HTML")
    report = executive_agent.execute_mission(user_prompt)
    bot.send_message(msg.chat.id, report, parse_mode="HTML")

@bot.message_handler(commands=['status', 'dashboard'])
def handle_status_commands(msg):
    import subprocess
    res = subprocess.run("pm2 status", shell=True, capture_output=True, text=True)
    bot.send_message(msg.chat.id, f"📊 <b>[PM2 Status]:</b>\n<pre>{res.stdout}</pre>", parse_mode="HTML")

@bot.message_handler(func=lambda msg: msg.from_user.id == ADMIN_ID)
def master_ceo_orchestrator(msg):
    raw_text = msg.text
    status_msg = bot.send_message(msg.chat.id, "👔 <b>[Executive_Agent]:</b> جاري المعالجة الحصينة...", parse_mode="HTML")
    report = executive_agent.execute_mission(raw_text)
    bot.send_message(msg.chat.id, report, parse_mode="HTML")

@bot.message_handler(commands=['ls', 'tree', 'cat', 'find', 'stat'])
def fs_commands_proxy(message):
    """تحويل الأوامر إلى المحرك المناسب (تم دمجها لتقليل التكرار)"""
    if message.from_user.id != ADMIN_ID: return
    cmd = message.text.split()[0][1:]
    
    if cmd == 'ls':
        from core.fs_navigator import fs_navigator
        path = message.text.replace('/ls', '').strip() or None
        r = fs_navigator.ls(path)
        if r['success']:
            bot.reply_to(message, f"📁 <b>{r['relative']}</b>\n" + "\n".join([f"• {f['name']}" for f in r['files'][:20]]), parse_mode="HTML")
        else: bot.reply_to(message, f"❌ {r['error']}")
    
    elif cmd == 'tree':
        from core.fs_navigator import fs_navigator
        r = fs_navigator.tree(max_depth=2)
        bot.reply_to(message, f"<pre>{r['tree'][:3500]}</pre>", parse_mode="HTML")
    
    # ... بقية الأوامر تعمل عبر ExecutionEngine الآن بشكل أذكى

# ─── Callback Queries Handling (UI Navigation) ───
@bot.callback_query_handler(func=lambda call: call.data.startswith('menu_') or call.data == 'back_main' or call.data.startswith('cloud_'))
def handle_menu_navigation(call):
    if call.from_user.id != ADMIN_ID: return
    
    if call.data == 'back_main':
        markup = ui_builder.build_main_control_plane()
        bot.edit_message_text("🔱 <b>NEXUM Main Interface</b>", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")
    
    elif call.data == 'menu_cloud':
        markup = ui_builder.build_cloud_menu()
        bot.edit_message_text("☁️ <b>Google Cloud Command Center</b>\nتحكم كامل في موارد GCP السيادية.", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")
    
    elif call.data.startswith('cloud_'):
        service_map = {
            "cloud_storage": "أهلاً بك في GCS. ماذا تريد أن نفعل بالملفات؟",
            "cloud_bq": "محرك BigQuery جاهز. اكتب استعلامك.",
            "cloud_vms": "جارِ جلب حالة أجهزة الـ VM...",
            "cloud_logs": "سأعرض لك آخر سجلات النظام من GCP.",
            "cloud_ai": "Vertex AI في وضع الانتظار. ما المهمة المطلوبة؟"
        }
        msg = service_map.get(call.data, "نظام GCP جاهز للأوامر.")
        bot.answer_callback_query(call.id, "☁️ Cloud Mode Active")
        bot.send_message(call.message.chat.id, f"⚡ {msg}")

# ╔══════════════════════════════════════════╗
# ║        2. المعالج الشامل (The Processor) ║
# ╚══════════════════════════════════════════╝

@bot.message_handler(content_types=['photo', 'document', 'text'])
def handle_universal(message):
    if message.from_user.id != ADMIN_ID: return
    
    chat_id = message.chat.id
    text = message.text or message.caption or ""
    
    # معالجة الملفات والوسائط
    file_data = None
    mime_type = None
    
    if message.photo:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file_data = bot.download_file(file_info.file_path)
        mime_type = "image/jpeg"
    elif message.document:
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        file_data = bot.download_file(file_info.file_path)
        mime_type = message.document.mime_type

    # تصنيف النية
    intent_result = classifier.classify(text) if text else None
    
    # ─── Google Cloud Commands 🔱 ───
    if intent_result and intent_result.intent in [
        Intent.CLOUD_STORAGE, Intent.CLOUD_BIGQUERY, Intent.CLOUD_COMPUTE,
        Intent.CLOUD_MONITOR, Intent.CLOUD_AI, Intent.CLOUD_GENERAL
    ]:
        bot.reply_to(message, "☁️ **NEXUM Cloud** جاري التنفيذ السيادي...", parse_mode="Markdown")
        try:
            res = cloud_agent.run({"text": text})
            if res["status"] == "success":
                output = res["output"][:3500]
                bot.send_message(chat_id, f"✅ <b>GCP Result:</b>\n{output}", parse_mode="HTML")
            else:
                bot.reply_to(message, f"❌ <b>Cloud Error:</b>\n<code>{res['error']}</code>", parse_mode="HTML")
        except Exception as e:
            bot.reply_to(message, f"❌ خطأ غير متوقع في Cloud: {e}")
        return

    # محادثة (Chat/Vision)
    _handle_chat(message, text, file_data, mime_type)

def _handle_chat(message, text, file_data=None, mime_type=None):
    history = context_memory.get_context(ADMIN_ID)
    system_instruction = (
            "أنت NEXUM CORE OS v3.5.0. نظام تشغيل سيادي متكامل. "
        "تمتلك القدرة على رؤية الصور وتحليل الملفات عبر Gemini 2.0. "
        "تحدث بلهجة تقنية، واثقة، ومباشرة. أنت تبني الأنظمة ولا تكتفي بالشرح."
    )
    
    res, _ = gemini_service.ask(
        prompt=text, 
        history=history, 
        system_instruction=system_instruction,
        file_data=file_data,
        mime_type=mime_type
    )
    
    bot.reply_to(message, res)
    context_memory.save_context(ADMIN_ID, text if text else "[Media/File]", role='user')
    context_memory.save_context(ADMIN_ID, res, role='assistant')
if __name__ == "__main__":
    print(f"🔱 NEXUM CORE OS v3.6.0 [Cloud Edition] is Online (Admin: {ADMIN_ID})")
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
