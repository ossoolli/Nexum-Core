# -*- coding: utf-8 -*-
"""
🔱 NEXUM CORE OS v7.4.2 — Total Sovereign Control
================================================
نسخة الإصلاح الشامل للوظائف:
- تفعيل الرؤية (Vision Enabled) بالكامل.
- ربط الوكلاء بالتنفيذ الفعلي للمشاريع (Build & Create).
- تمكين بناء المواقع والتطبيقات داخل السيرفر.
"""

import os
import sys
import time
import logging
import re
from datetime import datetime

# 1. ─── الطبقة المعمارية (Nexum Package) ───
from nexum.config import config
from nexum.logger import logger
from nexum.security.audit import log_audit, AuditEvent
from nexum.security.rate_limiter import rate_limiter
from nexum.intelligence.classifier import classifier, Intent
from nexum.memory.summarizer import summarizer

# 2. ─── طبقة الخدمات والمهمات الأصلية (Core) ───
import telebot
from telebot import types
from services.gemini_service import gemini_service
from core.memory_local import context_memory
from core.executor import executor
from core.orchestrator import orchestrator
from core.planner import AIPlanner
from core.fsm_manager import fsm_manager
from core.router import setup_router
from core.keyboards import SovereignUIBuilder
from core.system_tools import register_all_system_tools

# 3. ─── طبقة الوكلاء (Agents Fleet) ───
from agents.monitor import monitor_agent
from agents.deploy import deploy_agent
from agents.webforge_agent import webforge as _webforge
from agents.bot_builder_agent import bot_builder as _bot_builder
from agents.agent_smith import agent_smith as _agent_smith
from agents.channel_manager import channel_manager as _channel_manager

# --- تهيئة البوت والواجهة ---
bot = telebot.TeleBot(config.telegram_token)
ui_builder = SovereignUIBuilder()
ADMIN_ID = config.admin_id
LOG_CHANNEL_ID = config.log_channel_id

# تهيئة المحرك والذكاء بشكله الإنتاجي
_planner = AIPlanner(gemini_service)
orchestrator.set_planner(_planner)
orchestrator.set_bot(bot, ADMIN_ID, LOG_CHANNEL_ID)

# متغيرات الحالة السيادية
pending_commands = {}

def broadcast(msg, parse_mode="Markdown"):
    if LOG_CHANNEL_ID:
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            cid = int(LOG_CHANNEL_ID) if str(LOG_CHANNEL_ID).replace('-', '').isdigit() else LOG_CHANNEL_ID
            bot.send_message(cid, f"📡 `[{timestamp}]` {msg}", parse_mode=parse_mode)
        except Exception as e:
            logger.error(f"[Broadcast Error] {e}")

@bot.message_handler(commands=['start', 'dashboard', 'menu'])
def send_welcome(message):
    log_audit(AuditEvent.COMMAND_EXECUTED, message.from_user.id, {"cmd": "dashboard"})
    markup = ui_builder.build_main_control_plane()
    bot.send_message(
        message.chat.id,
        "🔱 <b>NEXUM CORE OS v7.4.2</b>\n"
        "━━━━━━━━━━━━━━\n"
        "📡 القناة الحية: 🟢 متصلة\n"
        "🛠️ الإنتاجية: نشطة (Full Mode)\n"
        "👁️ الرؤية: مفعلة ومستقرة\n"
        "━━━━━━━━━━━━━━\n"
        "أهلاً بك في نظام التشغيل السيادي. أنا جاهز للبناء والتنفيذ فوراً.",
        reply_markup=markup,
        parse_mode="HTML"
    )

@bot.message_handler(content_types=['photo', 'document', 'text'])
def handle_universal(message):
    text = message.text or message.caption or ""
    
    # تحويل الوسائط للرؤية مباشرة
    if message.content_type in ['photo', 'document']:
        _handle_media(message, text)
        return

    # التصنيف الذكي
    intent_result = classifier.classify(text)
    intent = intent_result.intent
    lower_text = text.lower()

    # التوجيه للوكلاء الإنتاجيين
    if any(k in lower_text for k in ['حالة', 'status', 'النبض']):
        bot.reply_to(message, monitor_agent.get_pulse_report(), parse_mode="HTML")
        return

    if any(k in lower_text for k in ['ارفع', 'انشر', 'deploy', 'push']):
        bot.reply_to(message, "🚀 جاري مزامنة الكود مع GitHub...")
        res = deploy_agent.deploy_updates(f"🔱 Production Update: {text[:20]}")
        bot.send_message(message.chat.id, res, parse_mode="HTML")
        return

    # الربط الحقيقي بالبناء والإنتاج
    if any(k in lower_text for k in ['موقع', 'ويب', 'webforge', 'صفحة', 'dashboard']):
        _handle_webforge(message, text)
        return

    if any(k in lower_text for k in ['بوت', 'botbuilder', 'تلجرام', 'telegram']):
        _handle_bot_builder(message, text)
        return

    if any(k in lower_text for k in ['وكيل', 'agent', 'smith', 'صمم']):
        _handle_agent_smith(message, text)
        return

    # التنفيذ المباشر
    if intent == Intent.EXECUTE or text.startswith('!'):
        cmd = text[1:] if text.startswith('!') else text
        _handle_execute(message, cmd)
        return

    # عمليات الملفات (The Doer Engine)
    action_keywords = ['انشئ', 'انشيء', 'اكتب', 'احذف', 'شغل', 'نفذ', 'افتح', 'اصنع', 'ابني']
    if any(k in text for k in action_keywords):
        _handle_file_operation(message, text)
        return

    # المحادثة العادية (الذكية)
    _handle_chat(message, text)

# ─── معالجات الإنتاج (The Engines) ───

def _handle_execute(message, cmd):
    result = executor.execute(cmd)
    bot.reply_to(message, f"💻 **مخرجات التنفيذ:**\n<pre>{result['output'][:3500]}</pre>", parse_mode="HTML")

def _handle_file_operation(message, text):
    bot.send_chat_action(message.chat.id, 'typing')
    os.makedirs("workspace", exist_ok=True)
    prompt = (f"كـ NEXUM OS، حوّل هذا الطلب إلى أوامر Linux Bash (أوامر فقط): {text}\n"
             f"يجب أن تكون المسارات داخل workspace/")
    shell_cmd, _ = gemini_service.ask(prompt)
    cmd = shell_cmd.strip().strip('`').split('\n')[0].strip()
    
    # حماية النواة
    if any(f in cmd and 'workspace/' not in cmd for f in ['main.py', 'nexum/', 'core/']):
        bot.reply_to(message, "⚠️ حماية: لا يمكن التعديل على ملفات النواة.")
        return

    res = executor.execute(cmd, force=True)
    bot.reply_to(message, f"✅ **تفيذ تقني:**\n`$ {cmd}`\n\n{res['output'][:2000]}")

def _handle_webforge(message, text):
    bot.reply_to(message, "🌐 **WebForge:** جاري إنشاء محرك الويب البرمجي...")
    # جعل الوكيل يعمل فعلياً في مجلدworkspace
    project_path = os.path.join("workspace", "new_site")
    os.makedirs(project_path, exist_ok=True)
    
    prompt = f"اكتب كود HTML5/CSS3 حديث جداً لهذه المتطلبات: {text}. أخرج الكود فقط."
    code, _ = gemini_service.ask(prompt)
    
    with open(os.path.join(project_path, "index.html"), "w", encoding="utf-8") as f:
        f.write(code)
    
    bot.send_message(message.chat.id, f"✅ **تم بناء الموقع بنجاح!**\nالمسار: `{project_path}/index.html`\nيمكنك معاينته الآن.")

def _handle_bot_builder(message, text):
    bot.reply_to(message, "🤖 **BotBuilder:** جاري توليد كود البوت ومعالجة البروتوكولات...")
    prompt = f"اكتب كود بايثون كامل لبوت تلجرام باستخدام telebot ينفذ الآتي: {text}. أخرج الكود فقط."
    code, _ = gemini_service.ask(prompt)
    
    path = os.path.join("workspace", "custom_bot.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    
    bot.send_message(message.chat.id, f"✅ **تم برمجة البوت وحفظه:**\nالمسار: `{path}`\nشغله باستخدام: `!python3 {path}`")

def _handle_media(message, text):
    bot.send_chat_action(message.chat.id, 'upload_photo')
    try:
        fid = message.photo[-1].file_id if message.content_type == 'photo' else message.document.file_id
        file_info = bot.get_file(fid)
        data = bot.download_file(file_info.file_path)
        mime = "image/jpeg" if message.content_type == 'photo' else message.document.mime_type
        
        res, _ = gemini_service.ask(text or "حلل هذا المستند/الصورة بدقة تقنية.", file_data=data, mime_type=mime)
        bot.reply_to(message, res)
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ رؤية: {e}")

NEXUM_SYSTEM_INSTRUCTION = """أنت NEXUM OS v7.4.2 — نظام تشغيل سيادي.
أنت تمتلك القدرة على التحليل البصري والبرمجة والتنفيذ.
عندما يطلب المستخدم بناء شيء، افعله برمجياً فوراً داخل workspace/ ولا تكتفِ بالكلام.
"""

def _handle_chat(message, text):
    history = context_memory.get_context(ADMIN_ID)
    res, _ = gemini_service.ask(text, history=history, system_instruction=NEXUM_SYSTEM_INSTRUCTION)
    bot.reply_to(message, res)
    context_memory.save_context(ADMIN_ID, text, role='user')
    context_memory.save_context(ADMIN_ID, res, role='assistant')

if __name__ == "__main__":
    from nexum.kernel.bootstrap import bootstrap
    if bootstrap():
        register_all_system_tools()
        setup_router(bot)
        print("🔱 NEXUM CORE OS v7.4.2 is Production Ready.")
        broadcast("🔱 **PRODUCTION MODE ENABLED**\n- الرؤية مفعلة.\n- محركات البناء والبرمجة نشطة.\n- جاهز للتنفيذ الفوري.")
        bot.infinity_polling(timeout=60, long_polling_timeout=30)
