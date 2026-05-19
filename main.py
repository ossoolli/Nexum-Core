import os
import re
import sys
import telebot
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

from core.planner import AIPlanner
from core.orchestrator import orchestrator
from services.gemini_service import GeminiService

bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

_gemini_svc = GeminiService(os.getenv("GOOGLE_API_KEY"))
_planner = AIPlanner(_gemini_svc)
orchestrator.set_planner(_planner)

# كلمات تفعيل "الواقع" - أي كلمة هنا تجبره على التنفيذ الحقيقي
_EXEC_AR = ('انشئ', 'انشيء', 'أنشئ', 'أنشئ', 'اكتب', 'احذف', 'عدل', 'شغل', 'نفذ', 'برمج', 'اريد', 'بناء')

def _is_execution_request(text):
    tokens = text.split()
    return any(tok.strip('.,!؟?:') in _EXEC_AR for tok in tokens)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.from_user.id != ADMIN_ID: return
    text = message.text.strip()

    if _is_execution_request(text):
        bot.reply_to(message, "🧠 **NEXUM REAL-TIME EXECUTION**\nجاري تشغيل المحرك الحقيقي...")
        try:
            result = orchestrator.execute_goal(text)
            bot.send_message(message.chat.id, f"✅ تم استلام الأمر: {result['protocol_id']}\nانتظر رسالة التأكيد بعد ثوانٍ...")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ خطأ في التخطيط: {str(e)}")
    else:
        # هنا المحادثة العادية (الدردشة)
        res, _ = _gemini_svc.ask(text, system_instruction="تحدث باختصار كنظام تشغيل.")
        bot.reply_to(message, res)

if __name__ == "__main__":
    from core.system_tools import register_all_system_tools
    register_all_system_tools()
    print("🔱 NEXUM OS IS LIVE AND TANGIBLE")
    bot.infinity_polling()
