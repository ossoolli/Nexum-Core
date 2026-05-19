import os
import telebot
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHANNEL_ID = "-1003969021809" # الـ ID الذي أعطيته لي

bot = telebot.TeleBot(TOKEN)

try:
    print(f"🚀 [Test] Trying to send to channel {CHANNEL_ID}...")
    bot.send_message(CHANNEL_ID, "⚠️ **NEXUM OS: اختبار بث قناة العمليات**\nالاتصال مستقر.")
    print("✅ [Success] The message should appear in your channel now!")
except Exception as e:
    print(f"❌ [Failed] Error: {e}")
