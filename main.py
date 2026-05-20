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

# ─── الوكلاء والأنظمة الأساسية ───
from agents.webforge_agent import webforge as _webforge
from agents.bot_builder_agent import bot_builder as _bot_builder
from agents.agent_smith import agent_smith as _agent_smith
from agents.channel_manager import channel_manager as _channel_manager
from core.bot_fleet import bot_fleet as _bot_fleet
from core.bot_network import bot_network as _bot_network

def broadcast(msg, parse_mode="Markdown"):
    """إرسال رسالة للقناة الحية"""
    if LOG_CHANNEL_ID:
        try:
            bot.send_message(LOG_CHANNEL_ID, msg, parse_mode=parse_mode)
        except Exception as e:
            print(f"[Broadcast Error] {e}")

# ─── المترجم الذكي (Interpreter) ───
class NexumInterpreter:
    """يحلل نوع الطلب ويوجهه للأداة أو الوكيل المناسب"""
    WEBFORGE_KEYWORDS = ['انشئ موقع', 'ابني موقع', 'صفحة هبوط', 'landing page', 'لوحة تحكم', 'dashboard', 'تطبيق ويب', 'web app']
    AGENT_BUILD_KEYWORDS = ['ابني وكيل', 'انشئ وكيل', 'صمم وكيل', 'build agent']
    BOT_BUILD_KEYWORDS = ['ابني بوت', 'انشئ بوت', 'build bot', 'telegram bot']
    MONITOR_KEYWORDS = ['حالة النظام', 'status', 'النبض', 'pulse', 'موارد']
    EXECUTE_KEYWORDS = [
        'انشئ', 'انشي', 'اكتب', 'نفذ', 'شغل', 'build', 'create', 
        'ملف', 'فولدر', 'مجعد', 'directory', 'file', 'touch'
    ]

    def classify(self, text: str) -> str:
        text_lower = text.lower()
        # إذا كانت الرسالة تحتوي على أمر لملف أو تنفيذ، نوجهها للمخطط
        if any(w in text_lower for w in self.EXECUTE_KEYWORDS): 
            return "execute"
        
        if any(w in text_lower for w in self.MONITOR_KEYWORDS): 
            return "monitor"
            
        return "chat"

interpreter = NexumInterpreter()

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    if message.from_user.id != ADMIN_ID: return
    from handlers.dash_handler import show_menu
    # محاكاة كولباك بسيط لعرض القائمة
    class MockCall:
        def __init__(self, msg):
            self.message = msg
            self.from_user = msg.from_user
    
    from handlers.dash_handler import get_main_menu_markup
    bot.send_message(
        message.chat.id,
        "🔱 *NEXUM CORE OS v7.1* جاهز\n\nاختر من القائمة للتحكم بالنظام:",
        reply_markup=get_main_menu_markup(),
        parse_mode="Markdown"
    )

@bot.message_handler(content_types=['photo', 'document', 'text'])
def handle_universal(message):
    if message.from_user.id != ADMIN_ID: return
    
    text = message.text or message.caption or ""
    category = interpreter.classify(text)

    if category == "monitor":
        bot.reply_to(message, monitor_agent.get_pulse_report(), parse_mode="HTML")
        return

    if category == "execute":
        bot.reply_to(message, "🧠 **NEXUM OS**\nجاري التخطيط والتنفيذ...", parse_mode="Markdown")
        try:
            res = orchestrator.execute_goal(text)
            pid = res.get('protocol_id', 'unknown')
            bot.send_message(message.chat.id, f"✅ تم الاستلام: `{pid}`", parse_mode="Markdown")
        except Exception as e:
            bot.reply_to(message, f"❌ خطأ في التنفيذ: {e}")
        return

    # الدردشة العامة
    bot.send_chat_action(message.chat.id, 'typing')
    _memory.save_context(message.from_user.id, text, role='user')
    try:
        context = _memory.get_context(message.from_user.id)
        history_prompt = ""
        if context:
            last_5 = context[-5:]
            history_prompt = "\n".join([f"{c['role']}: {c['content']}" for c in last_5])
            history_prompt = f"سياق المحادثة السابقة:\n{history_prompt}\n\n"

        full_prompt = f"{history_prompt}الرسالة الحالية: {text}"
        res, _ = _gemini_svc.ask(
            full_prompt,
            system_instruction=(
                "أنت NEXUM OS نظام تشغيل ذكاء اصطناعي سيادي. "
                "تحدث بالعربية دائماً وباختصار. "
                "تحذير هام: لا تتظاهر أبداً بأنك نفذت أمراً تقنياً (مثل إنشاء ملف أو تشغيل كود) إذا لم يتم تزويدك بنتائج حقيقية من النظام. "
                "إذا طلب المستخدم إنشاء ملف، أخبره أنك ستقوم بذاريك عبر المنسق (Orchestrator)."
            )
        )
        bot.reply_to(message, res)
        _memory.save_context(message.from_user.id, res[:500], role='assistant')
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {e}")

if __name__ == "__main__":
    # تسجيل أدوات النظام
    from core.system_tools import register_all_system_tools
    register_all_system_tools()

    # تهيئة الروتر المركزي (Callback Query Router)
    from core.router import setup_router
    setup_router(bot)

    # مزامنة BotFather (اختياري)
    try:
        from core.botfather_manager import BotFatherManager
        import asyncio
        manager = BotFatherManager(os.getenv("TELEGRAM_TOKEN"))
        # يمكنك تفعيل هذا السطر عند الحاجة لمزامنة الأوامر
        # asyncio.run(manager.sync_all_settings(webapp_url=f"https://{os.getenv('DOMAIN', 'nexum.dev')}/mini-app"))
    except Exception as e:
        print(f"⚠️ BotFather Sync Failed: {e}")

    print("🔱 NEXUM CORE OS v7.1 — Online and Sovereign.")
    broadcast("🔱 **NEXUM OS v7.1** بدأ العمل بنجاح.\nجميع الأنظمة نشطة.")
    bot.infinity_polling()
