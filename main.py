"""
🔱 NEXUM CORE OS — البوابة السيادية الرئيسية
==============================================
يجمع بين: الأوامر المباشرة، التنفيذ الذاتي، تحليل الملفات، البث الحي.
"""
import os
import sys

# ضمان مسار العمل الصحيح
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import telebot
from telebot import types
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

# ─── المتغيرات الأساسية ───
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID", "").strip("'\"")

# ─── تهيئة المحركات ───
from services.gemini_service import GeminiService
from core.memory_local import LongTermMemory
from core.executor import executor

_gemini_svc = GeminiService(os.getenv("GOOGLE_API_KEY"))
_memory = LongTermMemory(os.path.join(BASE_DIR, 'storage', 'memory.json'))

# ─── تهيئة الـ Orchestrator ───
from core.orchestrator import orchestrator
from core.planner import AIPlanner

_planner = AIPlanner(_gemini_svc)
orchestrator.set_planner(_planner)
orchestrator.set_bot(bot, ADMIN_ID, LOG_CHANNEL_ID)

# ─── تهيئة الوكلاء ───
from agents.monitor import monitor_agent
from agents.deploy import deploy_agent

# ─── الأوامر المعلقة (للتأكيد الأمني) ───
pending_commands = {}


# ╔══════════════════════════════════════════╗
# ║         البث المباشر للقناة              ║
# ╚══════════════════════════════════════════╝

def broadcast(msg, parse_mode="Markdown"):
    """إرسال رسالة للقناة الحية"""
    if LOG_CHANNEL_ID:
        try:
            bot.send_message(LOG_CHANNEL_ID, msg, parse_mode=parse_mode)
        except Exception as e:
            print(f"[Broadcast Error] {e}")


# ╔══════════════════════════════════════════╗
# ║         المترجم الذكي (Interpreter)      ║
# ╚══════════════════════════════════════════╝

class NexumInterpreter:
    """يحلل نوع الطلب ويوجهه للأداة أو الوكيل المناسب"""

    # كلمات تدل على طلب تنفيذي (يحتاج Orchestrator)
    EXEC_KEYWORDS = [
        'انشئ', 'اكتب', 'احذف', 'عدل', 'شغل', 'نفذ', 'ابحث',
        'بناء', 'برمج', 'صنع', 'حمل', 'ثبت', 'install',
        'create', 'build', 'run', 'deploy', 'search'
    ]

    # كلمات تدل على طلب مراقبة
    MONITOR_KEYWORDS = ['حالة النظام', 'status', 'النبض', 'pulse', 'موارد']

    # كلمات تدل على طلب نشر
    DEPLOY_KEYWORDS = ['ارفع الكود', 'deploy', 'push', 'جيت هب', 'github', 'sync']

    # كلمات تدل على البث للقناة
    BROADCAST_KEYWORDS = ['ارسل للقناة', 'ارسل الى القناة', 'انشر في القناة']

    def classify(self, text: str) -> str:
        """تصنيف نوع الطلب"""
        lower = text.lower().strip()

        if any(k in lower for k in self.BROADCAST_KEYWORDS):
            return "broadcast"
        if any(k in lower for k in self.MONITOR_KEYWORDS):
            return "monitor"
        if any(k in lower for k in self.DEPLOY_KEYWORDS):
            return "deploy"
        if any(k in lower for k in self.EXEC_KEYWORDS):
            return "execute"
        return "chat"


interpreter = NexumInterpreter()


# ╔══════════════════════════════════════════╗
# ║       أوامر البوت (/start, /run, /plan)  ║
# ╚══════════════════════════════════════════╝

def get_dashboard_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("📊 حالة النظام", callback_data="status"),
        types.InlineKeyboardButton("🚀 نشر GitHub", callback_data="deploy")
    )
    markup.add(
        types.InlineKeyboardButton("📡 بث تجريبي", callback_data="test_broadcast")
    )
    return markup


@bot.message_handler(commands=['start', 'dashboard'])
def send_dashboard(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(
        message.chat.id,
        "🔱 <b>NEXUM CORE OS v5.0</b>\n"
        "━━━━━━━━━━━━━━\n"
        "📡 القناة الحية: متصلة\n"
        "🧠 المحرك: Gemini + OpenRouter\n"
        "🛡️ الأمان: نشط\n"
        "━━━━━━━━━━━━━━\n"
        "جاهز لتلقي الأوامر.",
        reply_markup=get_dashboard_markup(),
        parse_mode="HTML"
    )


@bot.message_handler(commands=['run'])
def run_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    cmd = message.text.replace('/run ', '', 1).strip()
    if not cmd:
        bot.reply_to(message, "الاستخدام: <code>/run <الأمر></code>", parse_mode="HTML")
        return

    result = executor.execute(cmd)

    if result['status'] == 'blocked':
        bot.reply_to(message, result['output'])
    elif result['status'] == 'confirm':
        pending_commands[message.from_user.id] = cmd
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ نفّذ", callback_data="confirm_run"),
            types.InlineKeyboardButton("❌ إلغاء", callback_data="cancel_run")
        )
        bot.reply_to(
            message,
            f"⚠️ <b>أمر حساس، تأكيد مطلوب:</b>\n<pre>{cmd}</pre>",
            reply_markup=markup, parse_mode="HTML"
        )
    else:
        bot.reply_to(message, f"<pre>{result['output'][:3500]}</pre>", parse_mode="HTML")


# ╔══════════════════════════════════════════╗
# ║       معالج الأزرار (Callbacks)          ║
# ╚══════════════════════════════════════════╝

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.from_user.id != ADMIN_ID:
        return
    bot.answer_callback_query(call.id, "جاري التنفيذ...")

    if call.data == "status":
        report = monitor_agent.get_pulse_report()
        bot.send_message(call.message.chat.id, report, parse_mode="HTML")

    elif call.data == "deploy":
        result = deploy_agent.deploy_updates("🔱 NEXUM Manual Deploy")
        bot.send_message(call.message.chat.id, result, parse_mode="HTML")

    elif call.data == "test_broadcast":
        broadcast("📡 **NEXUM OS:** اختبار البث الحي — النظام متصل ويعمل بكفاءة.")
        bot.send_message(call.message.chat.id, "✅ تم البث في القناة بنجاح!")

    elif call.data == "confirm_run":
        cmd = pending_commands.pop(call.from_user.id, None)
        if cmd:
            result = executor.execute(cmd, force=True)
            bot.send_message(
                call.message.chat.id,
                f"✅ <pre>{result['output'][:3500]}</pre>",
                parse_mode="HTML"
            )

    elif call.data == "cancel_run":
        pending_commands.pop(call.from_user.id, None)
        bot.answer_callback_query(call.id, "تم الإلغاء.")


# ╔══════════════════════════════════════════╗
# ║       المعالج الشامل (Universal Handler)  ║
# ╚══════════════════════════════════════════╝

@bot.message_handler(content_types=['photo', 'document', 'text'])
def handle_universal(message):
    if message.from_user.id != ADMIN_ID:
        return

    text = message.text or message.caption or ""
    category = interpreter.classify(text)

    # ─── البث للقناة ───
    if category == "broadcast":
        content = text
        for kw in interpreter.BROADCAST_KEYWORDS:
            content = content.replace(kw, "").strip()
        if not content:
            content = "📡 إشعار تلقائي من NEXUM OS"
        broadcast(f"📢 **NEXUM BROADCAST**\n\n{content}")
        bot.reply_to(message, "✅ تم النشر في القناة بنجاح!")
        return

    # ─── تحليل الصور ───
    if message.content_type == 'photo':
        bot.send_chat_action(message.chat.id, 'typing')
        try:
            file_info = bot.get_file(message.photo[-1].file_id)
            data = bot.download_file(file_info.file_path)
            prompt = text or "حلل هذه الصورة بدقة واستخرج كل المعلومات المهمة منها."
            res, _ = _gemini_svc.ask(prompt, file_data=data, mime_type="image/jpeg")
            bot.reply_to(message, res)
            _memory.save_context(message.from_user.id, f"[تحليل صورة] {res[:200]}", role='assistant')
        except Exception as e:
            bot.reply_to(message, f"❌ فشل تحليل الصورة: {e}")
        return

    # ─── تحليل المستندات (PDF, TXT, etc.) ───
    if message.content_type == 'document':
        bot.send_chat_action(message.chat.id, 'typing')
        try:
            file_info = bot.get_file(message.document.file_id)
            data = bot.download_file(file_info.file_path)
            mime = message.document.mime_type or "application/octet-stream"
            prompt = text or "قم بتحليل هذا الملف بالكامل واستخرج أهم النقاط والمعلومات."
            res, _ = _gemini_svc.ask(prompt, file_data=data, mime_type=mime)
            bot.reply_to(message, res)
            bot.send_message(message.chat.id, "💡 هل تود إرسال هذا التحليل للقناة؟ اكتب: <b>ارسل للقناة</b>", parse_mode="HTML")
            _memory.save_context(message.from_user.id, f"[تحليل ملف: {message.document.file_name}] {res[:200]}", role='assistant')
        except Exception as e:
            bot.reply_to(message, f"❌ فشل تحليل الملف: {e}")
        return

    # ─── مراقبة النظام ───
    if category == "monitor":
        report = monitor_agent.get_pulse_report()
        bot.reply_to(message, report, parse_mode="HTML")
        return

    # ─── نشر GitHub ───
    if category == "deploy":
        bot.reply_to(message, "🚀 جاري رفع الكود...")
        result = deploy_agent.deploy_updates(f"🔱 {text[:30]}")
        bot.send_message(message.chat.id, result, parse_mode="HTML")
        broadcast(f"🚀 **Git Deploy:**\n{text[:100]}")
        return

    # ─── التنفيذ عبر الـ Orchestrator ───
    if category == "execute":
        bot.reply_to(message, "🧠 **NEXUM OS**\nجاري التخطيط والتنفيذ...", parse_mode="Markdown")
        try:
            res = orchestrator.execute_goal(text)
            pid = res.get('protocol_id', 'unknown')
            bot.send_message(message.chat.id, f"✅ تم الاستلام: `{pid}`", parse_mode="Markdown")
            _memory.save_context(message.from_user.id, f"[تنفيذ: {pid}] {text}", role='user')
        except Exception as e:
            bot.reply_to(message, f"❌ خطأ في التنفيذ: {e}")
        return

    # ─── الدردشة العامة (Chat Mode) ───
    bot.send_chat_action(message.chat.id, 'typing')
    _memory.save_context(message.from_user.id, text, role='user')
    try:
        # جلب السياق من الذاكرة لجعل الردود أذكى
        context = _memory.get_context(message.from_user.id)
        history_prompt = ""
        if context:
            last_5 = context[-5:]
            history_prompt = "\n".join([f"{c['role']}: {c['content']}" for c in last_5])
            history_prompt = f"سياق المحادثة السابقة:\n{history_prompt}\n\n"

        full_prompt = f"{history_prompt}الرسالة الحالية: {text}"
        res, _ = _gemini_svc.ask(
            full_prompt,
            system_instruction="أنت NEXUM OS نظام تشغيل ذكاء اصطناعي سيادي. تحدث بالعربية. ردودك عملية ودقيقة."
        )
        bot.reply_to(message, res)
        _memory.save_context(message.from_user.id, res[:500], role='assistant')
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {e}")


# ╔══════════════════════════════════════════╗
# ║            نقطة البداية                  ║
# ╚══════════════════════════════════════════╝

if __name__ == "__main__":
    # تسجيل أدوات النظام
    from core.system_tools import register_all_system_tools
    register_all_system_tools()

    print("🔱 NEXUM CORE OS v5.0 — Online and Sovereign.")
    broadcast("🔱 **NEXUM OS v5.0** بدأ العمل بنجاح.\nجميع الأنظمة نشطة.")
    bot.infinity_polling()
