# -*- coding: utf-8 -*-
"""
🔱 NEXUM CORE OS v7.3.0 — The Sovereign Union
==============================================
إصدار التجميع السيادي: يدمج ذكاء v5.0، هيكلة v7.1، وحداثة v7.2.1.
الملف الوحيد الذي يربط "الجهاز العصبي" للنظام بالكامل.
"""

import os
import sys
import time
import logging
from datetime import datetime

# 1. ─── الطبقة المعمارية (Nexum Package) ───
from nexum.config import config
from nexum.logger import logger
from nexum.security.audit import log_audit, AuditEvent
from nexum.security.rate_limiter import rate_limiter
from nexum.intelligence.classifier import classifier, Intent
from nexum.memory.summarizer import summarizer
from nexum.interfaces.telegram.runner import TelegramRunner

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

# 3. ─── طبقة الوكلاء (Agents Fleet) ───
from agents.monitor import monitor_agent
from agents.deploy import deploy_agent
from agents.webforge_agent import webforge as _webforge
from agents.bot_builder_agent import bot_builder as _bot_builder
from agents.agent_smith import agent_smith as _agent_smith
from agents.channel_manager import channel_manager as _channel_manager
try:
    from core.bot_fleet import bot_fleet as _bot_fleet
except ImportError:
    # لتجنب الفشل إذا لم يتم إكمال ملفات الـ fleet بعد
    _bot_fleet = None

# --- تهيئة البوت المركزية (v7.2.1 style) ---
bot = telebot.TeleBot(config.telegram_token)
ADMIN_ID = config.admin_id
LOG_CHANNEL_ID = config.log_channel_id

# تهيئة المخطط
_planner = AIPlanner(gemini_service)
orchestrator.set_planner(_planner)
orchestrator.set_bot(bot, ADMIN_ID, LOG_CHANNEL_ID)

# متغيرات الحالة (v5.0 style)
pending_commands = {}
_last_analysis = {}  # {user_id: "آخر تحليل صورة/ملف"}

# ╔══════════════════════════════════════════╗
# ║         1. البث المباشر (Broadcast)      ║
# ╚══════════════════════════════════════════╝

def broadcast(msg, parse_mode="Markdown"):
    """البث المباشر لقناة العمليات (Log Channel)"""
    if LOG_CHANNEL_ID:
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            bot.send_message(LOG_CHANNEL_ID, f"📡 `[{timestamp}]` {msg}", parse_mode=parse_mode)
        except Exception as e:
            logger.error(f"[Broadcast Error] {e}")

# ╔══════════════════════════════════════════╗
# ║       2. لوحة التحكم (Dashboard UI)      ║
# ╚══════════════════════════════════════════╝

def get_dashboard_markup():
    """لوحة التحكم الكاملة بـ 7 أزرار (الأسلاك المفقودة)"""
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("📊 النبض", callback_data="status"),
        types.InlineKeyboardButton("🚀 نشر GitHub", callback_data="deploy")
    )
    markup.add(
        types.InlineKeyboardButton("🌐 المواقع", callback_data="list_projects"),
        types.InlineKeyboardButton("🤖 الوكلاء", callback_data="list_agents")
    )
    markup.add(
        types.InlineKeyboardButton("🤖 البوتات", callback_data="list_bots"),
        types.InlineKeyboardButton("📢 القنوات", callback_data="list_channels")
    )
    markup.add(
        types.InlineKeyboardButton("📡 قناة البث", callback_data="test_broadcast"),
        types.InlineKeyboardButton("⚙️ الإعدادات", callback_data="settings")
    )
    return markup

# ╔══════════════════════════════════════════╗
# ║        3. المعالجات (Handlers)           ║
# ╚══════════════════════════════════════════╝

@bot.message_handler(commands=['start', 'dashboard'])
def send_welcome(message):
    if message.from_user.id != ADMIN_ID: return
    
    log_audit(AuditEvent.COMMAND_EXECUTED, ADMIN_ID, {"cmd": "start"})
    broadcast("🔱 **NEXUM CORE UI:** تم طلب لوحة التحكم.")
    
    bot.send_message(
        message.chat.id,
        "🔱 <b>NEXUM CORE OS v7.3.0</b>\n"
        "━━━━━━━━━━━━━━\n"
        "📡 القناة الحية: 🟢 متصلة\n"
        "🧠 المصنف: Gemini 1.5 Pro\n"
        "🛡️ الحماية: نشطة (v7.2)\n"
        "━━━━━━━━━━━━━━\n"
        "جاهز لتوجيه الوكلاء وتنفيذ المهام السيادية.",
        reply_markup=get_dashboard_markup(),
        parse_mode="HTML"
    )

@bot.message_handler(commands=['run'])
def run_command(message):
    if message.from_user.id != ADMIN_ID: return
    cmd = message.text.replace('/run ', '', 1).strip()
    if not cmd:
        bot.reply_to(message, "الاستخدام: <code>/run <الأمر></code>", parse_mode="HTML")
        return

    result = executor.execute(cmd)
    if result['status'] == 'confirm':
        pending_commands[message.from_user.id] = cmd
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ نفّذ", callback_data="confirm_run"),
            types.InlineKeyboardButton("❌ إلغاء", callback_data="cancel_run")
        )
        bot.reply_to(message, f"⚠️ <b>أمر حساس، تأكيد مطلوب:</b>\n<pre>{cmd}</pre>", reply_markup=markup, parse_mode="HTML")
    else:
        bot.reply_to(message, f"<pre>{result['output'][:3500]}</pre>", parse_mode="HTML")

# ╔══════════════════════════════════════════╗
# ║      4. معالج الأزرار (Callbacks)        ║
# ╚══════════════════════════════════════════╝

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.from_user.id != ADMIN_ID: return
    bot.answer_callback_query(call.id, "🔱 تم...")

    if call.data == "status":
        bot.send_message(call.message.chat.id, monitor_agent.get_pulse_report(), parse_mode="HTML")
    elif call.data == "deploy":
        res = deploy_agent.deploy_updates("🔱 NEXUM Deploy")
        bot.send_message(call.message.chat.id, res, parse_mode="HTML")
    elif call.data == "test_broadcast":
        broadcast("📡 **Live Broadcast Probe:** حلقة الوصل تعمل بكفاءة.")
        bot.answer_callback_query(call.id, "✅ تم البث!")
    elif call.data == "list_projects":
        projects = _webforge.list_projects()
        bot.send_message(call.message.chat.id, f"🌐 **المواقع:** {len(projects)} مشاريع مكتشفة.")
    elif call.data == "list_agents":
        agents = _agent_smith.list_agents()
        bot.send_message(call.message.chat.id, f"🤖 **الوكلاء:** {len(agents)} وكلاء مسجلون.")
    elif call.data == "list_bots":
        if _bot_fleet:
            bots = _bot_fleet.list_bots()
            bot.send_message(call.message.chat.id, f"🤖 **بوتاتي:** {len(bots)} بوتات في الأسطول.")
    elif call.data == "list_channels":
        channels = _channel_manager.list_channels()
        bot.send_message(call.message.chat.id, f"📢 **القنوات:** {len(channels)} قنوات مربوطة.")
    elif call.data == "confirm_run":
        cmd = pending_commands.pop(call.from_user.id, None)
        if cmd:
            res = executor.execute(cmd, force=True)
            bot.send_message(call.message.chat.id, f"✅ <pre>{res['output'][:3500]}</pre>", parse_mode="HTML")

# ╔══════════════════════════════════════════╗
# ║    5. المعالج الشامل (Universal Engine)  ║
# ╚══════════════════════════════════════════╝

@bot.message_handler(content_types=['photo', 'document', 'text'])
def handle_universal(message):
    if message.from_user.id != ADMIN_ID: return

    # 🛑 أ. Rate Limiting (v7.2.1)
    if not rate_limiter.is_allowed(ADMIN_ID):
        bot.reply_to(message, "⚠️ حماية: عمليات متكررة جداً. انتظر قليلاً.")
        return

    text = message.text or message.caption or ""
    
    # 🔍 ب. التصنيف الذكي (Gemini Classifier v7.2.1)
    result = classifier.classify(text)
    intent = result.intent
    
    # 📝 ج. التسجيل الأمني (Audit Log)
    log_audit(AuditEvent.COMMAND_EXECUTED, ADMIN_ID, {"intent": intent, "text": text[:100]})
    
    # 📡 البث الحي للقناة
    broadcast(f"🔍 **Nexum Intelligence:** Intent `{intent}` context received.")

    # 🐍 د. منطق التوجيه للوكلاء (The nervous systemwires)
    
    # معالجة الصور/الملفات أولاً
    if message.content_type in ['photo', 'document']:
        _handle_media(message, text)
        return

    # التوجيه بناءً على النية (intent)
    if intent == Intent.MONITOR:
        bot.reply_to(message, monitor_agent.get_pulse_report(), parse_mode="HTML")

    elif intent == Intent.DEPLOY:
        bot.reply_to(message, "🚀 نشر وتحديث...")
        res = deploy_agent.deploy_updates(f"🔱 Auto Sync: {text[:20]}")
        bot.send_message(message.chat.id, res, parse_mode="HTML")

    elif intent == Intent.EXECUTE:
        # التوجيه لبناء الوكلاء أو المواقع بناءً على الكلمات المفتاحية لمزيد من الدقة
        lower_text = text.lower()
        if any(k in lower_text for k in ['ابني موقع', 'موقع', 'webforge']):
            _handle_webforge(message, text)
        elif any(k in lower_text for k in ['ابني وكيل', 'وكيل']):
            _handle_agent_smith(message, text)
        elif any(k in lower_text for k in ['ارسل للقناة', 'انشر']):
             _handle_broadcast_command(message, text)
        else:
            bot.reply_to(message, "🧠 جاري التخطيط والتنفيذ عبر Orchestrator...")
            orchestrator.execute_goal(text)

    elif intent == Intent.CHAT:
        _handle_chat(message, text)

    # 🧠 هـ. التلخيص (Memory Summarizer v7.2.1)
    # يتم استدعاؤه بعد المعالجة للحفاظ على نافذة السياق
    history = context_memory.get_context(ADMIN_ID)
    if summarizer.should_summarize(history):
        summarizer.summarize(history)

def _handle_media(message, text):
    bot.send_chat_action(message.chat.id, 'typing')
    try:
        if message.content_type == 'photo':
            file_info = bot.get_file(message.photo[-1].file_id)
            data = bot.download_file(file_info.file_path)
            res, _ = gemini_service.ask(text or "تحليل الصورة.", file_data=data, mime_type="image/jpeg")
        else:
            file_info = bot.get_file(message.document.file_id)
            data = bot.download_file(file_info.file_path)
            res, _ = gemini_service.ask(text or "تحليل الملف.", file_data=data, mime_type=message.document.mime_type)
        
        bot.reply_to(message, res)
        _last_analysis[ADMIN_ID] = res[:2000]
        context_memory.save_context(ADMIN_ID, f"[Media Analysis] {res[:200]}", role='assistant')
    except Exception as e:
        logger.error(f"Media analysis error: {e}")
        bot.reply_to(message, f"❌ فشل تحليل المحتوى: {e}")

def _handle_webforge(message, text):
    bot.send_message(message.chat.id, "🌐 **WebForge** جاري التحليل والبناء...")
    res = _webforge.start({"project_name": "auto_project", "description": text})
    bot.send_message(message.chat.id, f"✅ تم البناء: {res.get('project', 'Project')}")

def _handle_agent_smith(message, text):
    bot.send_message(message.chat.id, "🤖 **AgentSmith** جاري تصميم الوكيل...")
    res = _agent_smith.design_agent("custom_agent", text)
    bot.send_message(message.chat.id, f"✅ التصميم مكتمل.")

def _handle_broadcast_command(message, text):
    content = text.replace("ارسل للقناة", "").replace("انشر", "").strip()
    if not content:
        content = _last_analysis.get(ADMIN_ID, "📡 لا يوجد تحليل محفوظ.")
    broadcast(f"📢 **NEXUM BROADCAST**\n\n{content}")
    bot.reply_to(message, "✅ تم البث!")

def _handle_chat(message, text):
    res, _ = gemini_service.ask(text, system_instruction="NEXUM OS. Be concise.")
    bot.reply_to(message, res)
    context_memory.save_context(ADMIN_ID, text, role='user')
    context_memory.save_context(ADMIN_ID, res, role='assistant')

# ╔══════════════════════════════════════════╗
# ║        6. الإقلاع (Sovereign Boot)        ║
# ╚══════════════════════════════════════════╝

if __name__ == "__main__":
    from nexum.kernel.bootstrap import bootstrap
    if not bootstrap():
        sys.exit(1)

    print("🔱 NEXUM CORE OS v7.3.0 — Online and Sovereign.")
    broadcast("🔱 **NEXUM OS v7.3.0** استعاد كامل وعيه التشغيلي.\nجميع الوكلاء والأسلاك العصبية نشطة.")
    
    # درع استقرار Polling (Crash Recovery)
    while True:
        try:
            logger.info("🔱 NEXUM polling started")
            bot.infinity_polling(timeout=30, long_polling_timeout=25)
        except KeyboardInterrupt:
            logger.info("Shutdown requested")
            break
        except Exception as e:
            logger.error(f"Crash Recovery Triggered: {e}")
            time.sleep(10)
