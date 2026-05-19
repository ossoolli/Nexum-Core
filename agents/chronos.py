import os, time, telebot
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
LOG_CHANNEL_ID = "-1003969021809"
bot = telebot.TeleBot(TOKEN)

def send_daily_report():
    report = f"🔱 **NEXUM DAILY PULSE**\n━━━━━━━━━━━━━━\n📅 {time.strftime('%Y-%m-%d')}\n✅ النظام مستقر ويعمل في الخلفية.\n━━━━━━━━━━━━━━"
    try:
        bot.send_message(LOG_CHANNEL_ID, report, parse_mode="Markdown")
        print("Report sent.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    while True:
        send_daily_report()
        # النوم لمدة 24 ساعة (60 ثانية * 60 دقيقة * 24 ساعة)
        # سنجعلها كل ساعة مؤقتاً (3600 ثانية) لكي تتأكد من عملها
        time.sleep(3600) 
