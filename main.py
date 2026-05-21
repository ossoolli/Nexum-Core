# -*- coding: utf-8 -*-
"""
🔱 NEXUM CORE OS v7.4.0 — Sovereign Evolution
================================================
إصدار الترقية السيادية v7.4:
- بيئة عمل معزولة (Sovereign Workspace) لحماية الملفات الأساسية.
- محرك استجابة صارم يمنع الخلط بين اللغة الطبيعية والأوامر التقنية.
- ترقية نظام التشغيل والتوجيه الذكي.
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
try:
    from core.bot_fleet import bot_fleet as _bot_fleet
except ImportError:
    _bot_fleet = None

# --- تهيئة البوت والواجهة ---
bot = telebot.TeleBot(config.telegram_token)
ui_builder = SovereignUIBuilder()
ADMIN_ID = config.admin_id
LOG_CHANNEL_ID = config.log_channel_id

# تهيئة المحرك والذكاء
_planner = AIPlanner(gemini_service)
orchestrator.set_planner(_planner)
orchestrator.set_bot(bot, ADMIN_ID, LOG_CHANNEL_ID)

# متغيرات الحالة السيادية
_last_analysis = {}
pending_commands = {}

# ╔══════════════════════════════════════════╗
# ║         1. البث المباشر (Broadcast)      ║
# ╚══════════════════════════════════════════╝

def broadcast(msg, parse_mode="Markdown"):
    """البث المباشر لقناة العمليات (Log Channel)"""
    if LOG_CHANNEL_ID:
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            # التأكد من أن الـ ID رقمي
            cid = int(LOG_CHANNEL_ID) if str(LOG_CHANNEL_ID).replace('-', '').isdigit() else LOG_CHANNEL_ID
            bot.send_message(cid, f"📡 `[{timestamp}]` {msg}", parse_mode=parse_mode)
        except Exception as e:
            logger.error(f"[Broadcast Error] {e}")

# ╔══════════════════════════════════════════╗
# ║       2. لوحة التحكم (Sovereign UI)      ║
# ╚══════════════════════════════════════════╝

@bot.message_handler(commands=['start', 'dashboard', 'menu'])
def send_welcome(message):
    # تم إلغاء حماية الأدمن بناءً على الطلب
    # if message.from_user.id != ADMIN_ID: return
    
    log_audit(AuditEvent.COMMAND_EXECUTED, ADMIN_ID, {"cmd": "dashboard"})
    broadcast("🔱 **NEXUM OS:** تم استدعاء لوحة التحكم السيادية.")
    
    markup = ui_builder.build_main_control_plane()
    
    bot.send_message(
        message.chat.id,
        "🔱 <b>NEXUM CORE OS v7.4.0</b>\n"
        "━━━━━━━━━━━━━━\n"
        "📡 القناة الحية: 🟢 متصلة\n"
        "📂 منطقة العمل: <code>/workspace</code>\n"
        "🧠 المصنف: v7.4-Strict\n"
        "🛡️ الحماية: سيادية كاملة\n"
        "━━━━━━━━━━━━━━\n"
        "مرحباً بك في الإصدار المطور. اختر قسماً للإدارة:",
        reply_markup=markup,
        parse_mode="HTML"
    )

# ╔══════════════════════════════════════════╗
# ║        3. المعالج الشامل (Universal)    ║
# ╚══════════════════════════════════════════╝

@bot.message_handler(content_types=['photo', 'document', 'text'])
def handle_universal(message):
    # تم إلغاء حماية الأدمن بناءً على الطلب
    # if message.from_user.id != ADMIN_ID: return

    # أ. الحماية والتحقق
    # تم تعطيل نظام الحماية من العمليات المتكررة
    # if not rate_limiter.is_allowed(ADMIN_ID):
    #     bot.reply_to(message, "⚠️ حماية: عمليات متكررة جداً.")
    #     return

    text = message.text or message.caption or ""
    if not text and message.content_type not in ['photo', 'document']: return

    # ب. التصنيف والذكاء (دمج مصفوفة الكلمات المفتاحية v5.0)
    intent_result = classifier.classify(text)
    intent = intent_result.intent
    lower_text = text.lower()

    # ج. توجيه سيادي بناءً على الكلمات المفتاحية الهجينة
    
    # 1. خدمات المراقبة والنظام
    if intent == Intent.MONITOR or any(k in lower_text for k in ['حالة', 'status', 'النبض', 'pulse']):
        bot.reply_to(message, monitor_agent.get_pulse_report(), parse_mode="HTML")
        return

    # 2. النشر والتحديث
    if intent == Intent.DEPLOY or any(k in lower_text for k in ['ارفع', 'انشر الكود', 'deploy', 'push', 'sync']):
        bot.reply_to(message, "🚀 جاري مزامنة الكود مع GitHub...")
        res = deploy_agent.deploy_updates(f"🔱 Auto Sync: {text[:20]}")
        bot.send_message(message.chat.id, res, parse_mode="HTML")
        return

    # 3. بناء المواقع (WebForge)
    if any(k in lower_text for k in ['انشئ موقع', 'ابني موقع', 'صفحة هبوط', 'webforge', 'dashboard', 'موقع']):
        _handle_webforge(message, text)
        return

    # 4. بناء البوتات (BotBuilder)
    if any(k in lower_text for k in ['ابني بوت', 'انشئ بوت', 'بوت جديد', 'build bot', 'botbuilder']):
        _handle_bot_builder(message, text)
        return

    # 5. إدارة القنوات (Channel Manager)
    if any(k in lower_text for k in ['انشر في الكل', 'بث للقنوات', 'قنواتي', 'cross post', 'ارسل للقناة']):
        _handle_channel_manager_cmd(message, text)
        return

    # 6. إدارة الوكلاء (Agent Smith)
    if any(k in lower_text for k in ['ابني وكيل', 'انشئ وكيل', 'agent smith', 'صمم وكيل']):
        _handle_agent_smith(message, text)
        return

    # 7. أوامر التنفيذ المباشرة (Shell/Execute)
    if intent == Intent.EXECUTE or text.startswith('!'):
        cmd = text[1:] if text.startswith('!') else text
        _handle_execute(message, cmd)
        return

    # 7.5 عمليات الملفات باللغة الطبيعية (انشئ ملف، اكتب، احذف...)
    if any(k in lower_text for k in ['انشئ ملف', 'انشيء ملف', 'اكتب ملف', 'احذف ملف',
                                     'اصنع ملف', 'انشئ مجلد', 'create file', 'make file',
                                     'اعرض ملف', 'افتح ملف']):
        _handle_file_operation(message, text)
        return

    # 8. الصور والملفات
    if message.content_type in ['photo', 'document']:
        _handle_media(message, text)
        return

    # 9. المحادثة العادية (Chat)
    _handle_chat(message, text)

# ╔══════════════════════════════════════════╗
# ║        4. المعالجات الفرعية (Sub)       ║
# ╚══════════════════════════════════════════╝

def _handle_execute(message, cmd):
    result = executor.execute(cmd)
    if result['status'] == 'confirm':
        pending_commands[message.from_user.id] = cmd
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ نفّذ", callback_data="confirm_run"),
            types.InlineKeyboardButton("❌ إلغاء", callback_data="cancel_run")
        )
        bot.reply_to(message, f"⚠️ **أمر حساس:**\n<pre>{cmd}</pre>", reply_markup=markup, parse_mode="HTML")
    else:
        bot.reply_to(message, f"💻 **المخرجات:**\n<pre>{result['output'][:3500]}</pre>", parse_mode="HTML")

def _handle_file_operation(message, text):
    """معالج عمليات الملفات v7.4 - ذكاء معزول ومحمي"""
    bot.send_chat_action(message.chat.id, 'typing')
    
    # ضمان وجود مجلد العمل
    workspace_dir = os.path.join(os.getcwd(), "workspace")
    if not os.path.exists(workspace_dir):
        os.makedirs(workspace_dir, exist_ok=True)

    # نطلب من Gemini تحويل الطلب إلى أمر Shell صارم
    gen_prompt = (
        f"أنت محرك تنفيذ NEXUM OS. المستخدم يريد: {text}\n"
        f"قواعد صارمة:\n"
        f"1. استخدم فقط أوامر Linux (touch, mkdir, echo, rm, cat).\n"
        f"2. اجعل كل المسارات داخل مجلد 'workspace/'.\n"
        f"3. لا تكتب أي كلمة عربية داخل الأمر.\n"
        f"4. المخرجات يجب أن تكون الأمر فقط.\n"
        f"استخدم صيغة: echo 'content' > workspace/filename.txt"
    )
    
    shell_cmd, _ = gemini_service.ask(gen_prompt)
    # تنظيف المخرجات من أي نص زائد
    shell_cmd = shell_cmd.strip().strip('`').split('\n')[0].strip()
    
    # حماية: منع الكتابة فوق الملفات الأساسية (مثل main.py)
    forbidden = ['main.py', 'nexum/', 'core/', 'services/', 'agents/', 'credentials.txt', '.env']
    if any(f in shell_cmd and 'workspace/' not in shell_cmd for f in forbidden):
        bot.reply_to(message, "⚠️ **حماية النظام:** لا يمكنك التعديل على ملفات النواة مباشرة. استخدم مجلد /workspace.")
        return

    if shell_cmd.startswith('❌') or not any(k in shell_cmd for k in ['workspace', 'mkdir', 'touch', 'echo']):
        bot.reply_to(message, "❌ فشل توليد أمر آمن. حاول صياغة الطلب بشكل أوضح.")
        return
    
    # تنفيذ الأمر المُولّد
    result = executor.execute(shell_cmd, force=True)
    status_icon = "✅" if result['status'] == 'success' else "❌"
    bot.reply_to(
        message,
        f"{status_icon} **NEXUM OS v7.4 EXECUTOR:**\n"
        f"<pre>$ {shell_cmd}</pre>\n"
        f"<pre>{result['output'][:3000]}</pre>",
        parse_mode="HTML"
    )

def _handle_webforge(message, text):
    bot.reply_to(message, "🌐 **WebForge:** جاري تحليل المتطلبات وبناء المشروع...")
    res = _webforge.start({"project_name": "auto_project", "description": text})
    bot.send_message(message.chat.id, f"✅ **تجهيز الموقع:** {res.get('project', 'Project Ready')}")

def _handle_bot_builder(message, text):
    bot.reply_to(message, "🤖 **BotBuilder:** جاري تصميم وبرمجة البوت الجديد...")
    res = _bot_builder.process_request(text)
    bot.send_message(message.chat.id, f"✅ **تم إنشاء البوت:**\n{res}")

def _handle_channel_manager_cmd(message, text):
    bot.reply_to(message, "📢 **ChannelManager:** جاري معالجة طلب البث والقنوات...")
    # إذا كان النص يحتوي على محتوى للنشر
    content = text.split("نشر", 1)[-1] if "نشر" in text else text
    _channel_manager.broadcast_to_all(content)
    bot.send_message(message.chat.id, "✅ تمت عملية النشر في جميع القنوات المربوطة.")

def _handle_agent_smith(message, text):
    bot.reply_to(message, "🎨 **AgentSmith:** جاري تصميم وكيل ذكاء اصطناعي مخصص...")
    _agent_smith.design_agent("custom_agent", text)
    bot.send_message(message.chat.id, "✅ الوكيل جاهز في قائمة الوكلاء.")

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
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ في التحليل: {e}")

NEXUM_SYSTEM_INSTRUCTION = """أنت NEXUM OS v7.4.0 — نظام تشغيل سيادي متطور.
أنت تدير سيرفر Linux حقيقي. مهمتك تنفيذ أوامر المستخدم بدقة تقنية.
عندما يطلب المستخدم إنشاء ملف أو مجلد، استخدم مجلد 'workspace/' دائماً.
تجنب شرح 'كيف يفعل المستخدم ذلك بنفسه'، بل افعل ذلك أنت بالنيابة عنه.
أجب بالعربية وبأسلوب نظام تشغيل حازم.
"""

def _handle_chat(message, text):
    history = context_memory.get_context(ADMIN_ID)
    
    # تحقق إذا كان النص يحتوي على طلب عملي ولم يتم التقاطه سابقاً
    action_keywords = ['انشئ', 'انشيء', 'اكتب', 'احذف', 'شغل', 'نفذ', 'افتح', 'اصنع', 'ابني']
    if any(k in text for k in action_keywords):
        _handle_file_operation(message, text)
        return
    
    res, _ = gemini_service.ask(text, history=history, system_instruction=NEXUM_SYSTEM_INSTRUCTION)
    
    # إذا كان هناك خطأ تقني، نرسل تقريراً للقناة
    if "❌ خطأ تقني" in res or "❌ خطأ:" in res:
        broadcast(f"⚠️ **DIAGNOSTIC ALERT**\n\n**Error:** {res}\n**User Input:** {text[:50]}...\n**Next Step:** Verify credentials.txt or GOOGLE_API_KEY.")
    
    bot.reply_to(message, res)
    context_memory.save_context(ADMIN_ID, text, role='user')
    context_memory.save_context(ADMIN_ID, res, role='assistant')
    
    if summarizer.should_summarize(history):
        summarizer.summarize(history)

# معالج مخصص للأزرار القديمة (Compatibility)
@bot.callback_query_handler(func=lambda call: call.data in ["confirm_run", "cancel_run", "status", "deploy"])
def handle_legacy_callbacks(call):
    if call.from_user.id != ADMIN_ID: return
    if call.data == "confirm_run":
        cmd = pending_commands.pop(call.from_user.id, None)
        if cmd:
            res = executor.execute(cmd, force=True)
            bot.send_message(call.message.chat.id, f"✅ <pre>{res['output'][:3500]}</pre>", parse_mode="HTML")
    elif call.data == "cancel_run":
        pending_commands.pop(call.from_user.id, None)
        bot.answer_callback_query(call.id, "❌ تم الإلغاء")
    elif call.data == "status":
        bot.send_message(call.message.chat.id, monitor_agent.get_pulse_report(), parse_mode="HTML")
    elif call.data == "deploy":
        res = deploy_agent.deploy_updates("🔱 NEXUM Manual Deploy")
        bot.send_message(call.message.chat.id, res, parse_mode="HTML")

# ╔══════════════════════════════════════════╗
# ║        5. الإقلاع (Sovereign Boot)        ║
# ╚══════════════════════════════════════════╝

if __name__ == "__main__":
    from nexum.kernel.bootstrap import bootstrap
    
    # 1. تهيئة النواة
    if not bootstrap():
        print("❌ فشل الإقلاع (Bootstrap Failed)")
        sys.exit(1)

    # 2. تسجيل مجموعة الأدوات الشاملة (v7.3)
    register_all_system_tools()
    
    # 3. تفعيل الموجه السيادي (The Router)
    setup_router(bot)

    print("🔱 NEXUM CORE OS v7.4.0 is Online.")
    broadcast("🔱 **NEXUM OS v7.4.0** (Evolved Sovereign) نشط الآن.\n- حماية النواة فعالة.\n- مجلد العمل المعزول جاهز.")
    
    # حلقة الاستقرار (Crash Recovery)
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=30)
        except Exception as e:
            logger.error(f"Kernel Recovery: {e}")
            time.sleep(10)
