import os, telebot
from dotenv import load_dotenv
load_dotenv()
from services.gemini_service import GeminiService

bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
_gemini_svc = GeminiService(os.getenv("GOOGLE_API_KEY"))

@bot.message_handler(content_types=['photo', 'document', 'text'])
def handle_universal(message):
    if message.from_user.id != ADMIN_ID: return
    
    # 🔔 إشعار للمستخدم بالبدء
    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    caption = message.caption or message.text or "حلل هذا المحتوى بدقة."
    data = None
    m_type = None

    # 1. إذا كانت صورة
    if message.content_type == 'photo':
        file_info = bot.get_file(message.photo[-1].file_id)
        data = bot.download_file(file_info.file_path)
        m_type = "image/jpeg"
    
    # 2. إذا كان ملفاً
    elif message.content_type == 'document':
        file_info = bot.get_file(message.document.file_id)
        data = bot.download_file(file_info.file_path)
        m_type = message.document.mime_type or "application/pdf"

    # التنفيذ عبر Gemini فوراً
    try:
        res, _ = _gemini_svc.ask(caption, file_data=data, mime_type=m_type)
        bot.reply_to(message, res)
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ: {str(e)}")

if __name__ == "__main__":
    bot.infinity_polling()
