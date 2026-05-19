import os, sys, telebot
from dotenv import load_dotenv
load_dotenv()
from core.planner import AIPlanner
from core.orchestrator import orchestrator
from services.gemini_service import GeminiService
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
_gemini_svc = GeminiService(os.getenv("GOOGLE_API_KEY"))
orchestrator.set_planner(AIPlanner(_gemini_svc))

@bot.message_handler(content_types=['text', 'document', 'photo'])
def handle_all(message):
    if message.from_user.id != ADMIN_ID: return
    text = message.text or message.caption or ""
    if any(k in text for k in ['انشئ', 'اكتب', 'احذف', 'عدل', 'شغل', 'نفذ', 'ابحث']):
        bot.reply_to(message, "🧠 **NEXUM OS**\nجاري التنفيذ...")
        try:
            res = orchestrator.execute_goal(text)
            bot.send_message(message.chat.id, f"✅ تم الاستلام: {res.get('protocol_id')}")
        except Exception as e: bot.reply_to(message, f"❌ خطأ: {e}")
    else:
        res, _ = _gemini_svc.ask(text, system_instruction="تحدث كنظام تشغيل.")
        bot.reply_to(message, res)

if __name__ == "__main__":
    from core.system_tools import register_all_system_tools
    register_all_system_tools()
    bot.infinity_polling()
