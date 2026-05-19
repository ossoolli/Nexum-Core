import os, telebot
from dotenv import load_dotenv
load_dotenv()
from services.gemini_service import GeminiService

bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CH_ID = "-1003969021809" # حقن مباشر للـ ID
_gemini_svc = GeminiService(os.getenv("GOOGLE_API_KEY"))

@bot.message_handler(func=lambda m: True, content_types=['text', 'document'])
def handle_all(message):
    if message.from_user.id != ADMIN_ID: return
    text = message.text or message.caption or ""
    
    # محرك البث المباشر للقناة
    if "ارسل للقناة" in text:
        content_to_send = text.replace("ارسل للقناة", "").strip()
        if not content_to_send: content_to_send = "إشعار تلقائي من NEXUM OS"
        
        try:
            bot.send_message(CH_ID, f"📢 **NEXUM LIVE BROADCAST**\n\n{content_to_send}", parse_mode="Markdown")
            bot.reply_to(message, "✅ تم النشر في القناة بنجاح!")
        except Exception as e:
            bot.reply_to(message, f"❌ خطأ فني أثناء البث: {e}")
        return

    # معالجة الملفات
    if message.content_type == 'document':
        bot.reply_to(message, "⚙️ جاري معالجة الملف...")
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded = bot.download_file(file_info.file_path)
            res, _ = _gemini_svc.ask("قم بتحليل هذا الملف.", file_data=downloaded, mime_type=message.document.mime_type)
            bot.reply_to(message, res)
        except Exception as e: bot.reply_to(message, f"❌ فشل المعالجة: {e}")
        return

    # الرد العادي
    res, _ = _gemini_svc.ask(text)
    bot.reply_to(message, res)

if __name__ == "__main__":
    bot.infinity_polling()
