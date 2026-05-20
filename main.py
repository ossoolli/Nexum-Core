# -*- coding: utf-8 -*-
"""
🔱 NEXUM CORE OS v7.2.1 — Full Integration Mode
=============================================
إصدار الدمج الكامل - المحرك الجديد nexum package
"""
import os
import time
import logging

# 1. الإعدادات والـ Logging (أول شيء)
from nexum.config import config
from nexum.logger import logger
from nexum.security.audit import log_audit, AuditEvent
from nexum.security.rate_limiter import rate_limiter

# 2. استيراد المكونات المركزية (القديمة والجديدة)
import telebot
from core.router import callback_router
from core.orchestrator import orchestrator
from core.planner import AIPlanner
from services.gemini_service import gemini_service
from core.memory_local import context_memory
from core.cloud_storage import CloudStorageManager

# 3. استيراد الوكلاء
try:
    from agents.monitor import monitor_agent
    from agents.deploy import deploy_agent
    from handlers.dash_handler import get_main_menu_markup
    from agents.webforge_agent import webforge
    from agents.bot_builder_agent import bot_builder
    from agents.agent_smith import agent_smith
except Exception as e:
    logger.error(f"⚠️ Failed to load some agents: {e}")

# 4. استيراد طبقة الذكاء الجديدة
from nexum.intelligence.classifier import classifier, Intent
from nexum.memory.summarizer import summarizer
from nexum.interfaces.telegram.runner import TelegramRunner

# --- تهيئة البوت ---
bot = telebot.TeleBot(config.telegram_token)
cloud_manager = CloudStorageManager(bot=bot)

# --- تهيئة المخطط ---
planner = AIPlanner(gemini_service)
orchestrator.set_planner(planner)
orchestrator.set_bot(bot, config.admin_id, config.log_channel_id)

# --- نظام الردود الذكي ---
NEXUM_SYSTEM_PROMPT = """أنت NEXUM OS v7.2 — الوعي المركزي لهذا السيرفر.
لغة الرد: العربية الفصحى الرصينة.
المسارات: apps فى registry/apps، Bots فى registry/bots، Docs فى storage/docs."""

# --- معالجات الرسائل ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if message.from_user.id != config.admin_id: return
    
    log_audit(AuditEvent.COMMAND_EXECUTED, message.from_user.id, {"command": "start"})
    
    welcome_text = (
        f"🔱 **NEXUM OS v{config.log_level} | Active**\n"
        f"تم تفعيل المحرك الجديد بنجاح.\n\n"
        f"الحالة: `Sovereign` 🟢\n"
        f"الذاكرة: `Active` 🧠"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=get_main_menu_markup())

@bot.message_handler(content_types=['photo', 'document', 'text'])
def handle_universal(message):
    if message.from_user.id != config.admin_id: return

    # 🛑 Rate Limiting
    if not rate_limiter.is_allowed(message.from_user.id):
        bot.reply_to(message, "⚠️ حماية: معدل طلباتك مرتفع جداً. انتظر قليلاً.")
        return

    text = message.text or message.caption or ""
    
    # 🧠 التصنيف الذكي (Gemini Classifier)
    result = classifier.classify(text)
    intent = result.intent
    
    logger.info(f"Intent Classified: {intent} (Conf: {result.confidence})")

    if intent == Intent.MONITOR:
        bot.reply_to(message, monitor_agent.get_pulse_report(), parse_mode="HTML")

    elif intent == Intent.DEPLOY:
        bot.reply_to(message, "🚀 جاري مزامنة ورفع الكود...")
        res = deploy_agent.deploy_updates(f"🔱 Auto Sync v7.2")
        bot.send_message(message.chat.id, res, parse_mode="HTML")

    elif intent == Intent.EXECUTE:
        log_audit(AuditEvent.COMMAND_EXECUTED, message.from_user.id, {"goal": text})
        _handle_execute(message, text)

    elif intent == Intent.CHAT:
        _handle_chat(message, text)
        
    else:
        # التعامل مع النوايا التخصصية الأخرى
        bot.reply_to(message, f"🧩 تم التعرف على نية: `{intent}`\nجاري المعالجة...")
        # هنا يمكن إضافة تفريعات للوكلاء الآخرين

def _handle_chat(message, text):
    history = context_memory.get_context(message.from_user.id)
    
    # تفحص إذا كان يجب التلخيص (Summarization)
    if summarizer.should_summarize(history):
        summary = summarizer.summarize(history)
        # استبدال سياق قديم بملخص (افتراضاً)
        logger.info("Context summarized for user.")

    res, _ = gemini_service.ask(text, system_instruction=NEXUM_SYSTEM_PROMPT)
    bot.reply_to(message, res)
    
    context_memory.save_context(message.from_user.id, text, role='user')
    context_memory.save_context(message.from_user.id, res, role='assistant')

def _handle_execute(message, text):
    bot.reply_to(message, "🧠 جاري التخطيط والتنفيذ...")
    try:
        res = orchestrator.execute_goal(text)
        bot.send_message(message.chat.id, f"✅ تم تفعيل البروتوكول: `{res.get('protocol_id', 'unknown')}`")
    except Exception as e:
        logger.error(f"Execution Error: {e}")
        bot.reply_to(message, f"❌ خطأ تنفيذ: {e}")

# --- الإقلاع بالمحرك الجديد ---
if __name__ == "__main__":
    from nexum.kernel.bootstrap import bootstrap
    
    # تنفيذ فحص ما قبل الإقلاع
    if not bootstrap():
        logger.critical("🚨 Bootstrap failed. Exiting.")
        exit(1)

    runner = TelegramRunner(bot)
    logger.info("🔱 NEXUM Sovereign OS Started via New Runner")
    runner.run()
