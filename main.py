import os
import re
import sys
import html
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

_EXEC_AR = ('انشئ', 'انشيء', 'أنشئ', 'اكتب', 'احذف', 'عدل', 'شغل', 'نفذ', 'برمج', 'اريد', 'بناء')

def _is_execution_request(text):
    if not text: return False
    tokens = text.split()
    return any(tok.strip('.,!؟?:') in _EXEC_AR for tok in tokens)

# --- معالج الملفات والمستندات ---
@bot.message_handler(content_types=['document', 'photo'])
def handle_multimodal(message):
    if message.from_user.id != ADMIN_ID: return
    bot.send_chat_action(message.chat.id, 'typing')
    
    file_id = message.photo[-1].file_id if message.content_type == 'photo' else message.document.file_id
    mime_type = 'image/jpeg' if message.content_type == 'photo' else message.document.mime_type
    
    try:
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        prompt = message.caption or "حلل هذا الملف واتخذ الإجراء المناسب."
        if message.content_type == 'document' and (mime_type and 'text' in mime_type):
            prompt += f"\n\nالمحتوى النصي للملف:\n{downloaded_file.decode('utf-8', errors='ignore')}"
            downloaded_file = None # تم تحويله لنص
            mime_type = None

        response, _ = _gemini_svc.ask(prompt, system_instruction="أنت نظام NEXUM OS. حلل المرفقات بدقة.", file_data=downloaded_file, mime_type=mime_type)
        bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ معالجة: {str(e)}")

# --- معالج النصوص والأوامر ---
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.from_user.id != ADMIN_ID: return
    text = message.text.strip()

    if _is_execution_request(text):
        bot.reply_to(message, "🧠 **NEXUM EXECUTION**\nجاري تحليل الطلب وتنفيذه...")
        try:
            result = orchestrator.execute_goal(text)
            bot.send_message(message.chat.id, f"✅ تم استلام الأمر: {result['protocol_id']}")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ خطأ: {str(e)}")
    else:
        res, _ = _gemini_svc.ask(text, system_instruction="تحدث باختصار كنظام تشغيل سيادي.")
        bot.reply_to(message, res)

if __name__ == "__main__":
    from core.system_tools import register_all_system_tools
    register_all_system_tools()
    print("🔱 NEXUM OS: FULL VISION & ACTION ENABLED")
    bot.infinity_polling()
