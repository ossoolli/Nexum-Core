# -*- coding: utf-8 -*-
"""
🔱 NEXUM CORE OS v3.5.0 — The Sovereign Architect
================================================
إصدار الإصلاح الشامل (Audit & Clean):
- تنظيف شامل للمكتبات غير المستخدمة.
- دعم كامل للوسائط (رؤية Gemini 2.0).
- فك الارتباط المعماري وتفعيل الـ Router.
"""

import os
from datetime import datetime
import telebot
from telebot import types

# 1. ─── الطبقة المعمارية (Nexum Core) ───
from nexum.config import config
from nexum.logger import logger
from nexum.intelligence.classifier import classifier, Intent

# 2. ─── المحركات المركزية ───
from services.gemini_service import gemini_service
from core.memory_local import context_memory
from core.execution_engine import execution_engine
from core.file_agent import file_agent
from core.inter_bot_protocol import inter_bot_protocol
from core.keyboards import SovereignUIBuilder
from core.router import setup_router

# تهيئة البوت
if not config:
    print("❌ Critical: Config failed to load. Check credentials.txt")
    exit(1)

bot = telebot.TeleBot(config.telegram_token)
ui_builder = SovereignUIBuilder()
ADMIN_ID = config.admin_id

# ربط المحركات
execution_engine.set_gemini(gemini_service)
setup_router(bot)

# ╔══════════════════════════════════════════╗
# ║        1. معالجات الأوامر (Commanders)   ║
# ╚══════════════════════════════════════════╝

@bot.message_handler(commands=['start', 'dashboard'])
def send_welcome(message):
    markup = ui_builder.build_main_control_plane()
    bot.send_message(
        message.chat.id,
        "🔱 <b>NEXUM CORE OS v3.5</b>\n"
        "━━━━━━━━━━━━━━\n"
        "🧠 الحالة: 🟢 بكامل الوعي التشغيلي\n"
        "⚙️ العقل: <code>gemini-3.5-flash</code>\n"
        "🛡️ النمط: سيادي (Architect Mode)\n"
        "━━━━━━━━━━━━━━\n"
        "استخدم القائمة أدناه أو ابدأ بكتابة الأوامر مباشرة.",
        reply_markup=markup,
        parse_mode="HTML"
    )

@bot.message_handler(commands=['workspace'])
def show_workspace(message):
    if message.from_user.id != ADMIN_ID: return
    result = file_agent.list_workspace()
    lines = [f"📁 <b>Workspace</b> — {result['count']} ملف\n━━━━━━━━━━━━━━"]
    for f in result["files"][:20]:
        lines.append(f"• <code>{f['name']}</code> — {f['size_kb']}KB")
    bot.reply_to(message, "\n".join(lines), parse_mode="HTML")

@bot.message_handler(commands=['bots'])
def show_bots(message):
    if message.from_user.id != ADMIN_ID: return
    bots = inter_bot_protocol.list_bots()
    if not bots:
        bot.reply_to(message, "🤖 لا يوجد sub-bots مسجّلون حالياً.")
        return
    lines = [f"🤖 <b>Bot Registry</b>\n━━━━━━━━━━━━━━"]
    for b in bots:
        icon = "🟢" if b["status"] == "running" else "🔴"
        lines.append(f"{icon} <b>{b['name']}</b> (PID: {b.get('pid','?')})")
    bot.reply_to(message, "\n".join(lines), parse_mode="HTML")

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
    
    # تنفيذ (Execute)
    if text.startswith('!') or (intent_result and intent_result.intent == Intent.EXECUTE):
        goal = text[1:] if text.startswith('!') else text
        execution_engine.execute_goal(goal=goal, bot=bot, chat_id=chat_id)
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
    print(f"🔱 NEXUM CORE OS v7.5.1 is Online (Admin: {ADMIN_ID})")
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
