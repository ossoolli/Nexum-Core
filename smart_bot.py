import logging
import subprocess
import html
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from services.gemini_service import GeminiService
from telegram_agent import agent

load_dotenv(dotenv_path="/home/madarmutaz/Mutaz-dev/.env")

TELEGRAM_TOKEN     = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY     = os.getenv("GOOGLE_API_KEY")
AUTHORIZED_USER_ID = int(os.getenv("ADMIN_ID", "0"))

logging.basicConfig(level=logging.INFO)
gemini = GeminiService(GEMINI_API_KEY)

async def run_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID: return
    command = " ".join(context.args)
    if not command:
        await update.message.reply_text("الاستخدام: <code>/cmd الأمر</code>", parse_mode='HTML')
        return
    try:
        process = subprocess.run(
            command, shell=True, capture_output=True,
            text=True, timeout=30
        )
        safe_output = html.escape(process.stdout + process.stderr)
        await update.message.reply_text(
            f"🖥️ <b>Terminal:</b>\n<pre>{safe_output[:3500] if safe_output else 'Done.'}</pre>",
            parse_mode='HTML'
        )
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {html.escape(str(e))}", parse_mode='HTML')

async def handle_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID: return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    # يمر عبر الوكيل الذكي (تنفيذ أو شات)
    response = agent.handle(update.effective_user.id, update.message.text)
    try:
        await update.message.reply_text(response, parse_mode='HTML')
    except Exception:
        await update.message.reply_text(response)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID: return
    await update.message.reply_text(
        "🔱 <b>NEXUM CORE — Smart Mode</b>\n\n"
        "<code>/cmd df -h</code> — تنفيذ مباشر\n"
        "أو اكتب هدفك مباشرة:\n"
        "<i>ثبت docker / شغل nginx / ارفع الكود</i>",
        parse_mode='HTML'
    )

if __name__ == '__main__':
    # تثبيت python-telegram-bot إن لم يكن موجوداً
    import importlib
    if not importlib.util.find_spec("telegram"):
        import subprocess
        subprocess.run(["pip", "install", "python-telegram-bot", "-q"])

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cmd", run_cmd))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_chat))

    print("🚀 Smart Bot — gemini-3.1-flash-lite — Online")
    app.run_polling()
