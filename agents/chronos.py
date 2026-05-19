"""
⏰ NEXUM Chronos Agent — وكيل الجدولة الزمنية
==============================================
يرسل تقارير دورية للقناة الحية ويراقب صحة النظام.
"""
import os
import sys
import time
import telebot
from datetime import datetime
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

TOKEN = os.getenv("TELEGRAM_TOKEN")
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID", "").strip("'\"")

bot = telebot.TeleBot(TOKEN) if TOKEN else None

# الفاصل الزمني بين التقارير (بالثواني)
REPORT_INTERVAL = 3600  # ساعة واحدة


def get_system_health():
    """جمع معلومات صحة النظام"""
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        return {
            "cpu": cpu,
            "ram": mem.percent,
            "disk": disk.percent,
            "ram_used": mem.used // (1024**2),
            "ram_total": mem.total // (1024**2),
        }
    except ImportError:
        return {"cpu": "N/A", "ram": "N/A", "disk": "N/A"}


def send_pulse():
    """إرسال نبض النظام للقناة"""
    if not bot or not LOG_CHANNEL_ID:
        print("[Chronos] Bot or Channel ID not configured.")
        return

    health = get_system_health()
    now = datetime.now()

    # تحديد حالة النظام
    status_icon = "🟢"
    if isinstance(health["cpu"], (int, float)):
        if health["cpu"] > 90 or health["ram"] > 90:
            status_icon = "🔴"
        elif health["cpu"] > 70 or health["ram"] > 70:
            status_icon = "🟡"

    report = (
        f"🔱 **NEXUM DAILY PULSE**\n"
        f"━━━━━━━━━━━━━━\n"
        f"📅 {now.strftime('%Y-%m-%d')}\n"
        f"⏰ {now.strftime('%H:%M:%S')}\n\n"
        f"{status_icon} **حالة النظام:**\n"
        f"🖥️ CPU: `{health['cpu']}%`\n"
        f"🧠 RAM: `{health['ram']}%`\n"
        f"💾 Disk: `{health['disk']}%`\n\n"
        f"✅ النواة مستقرة.\n"
        f"━━━━━━━━━━━━━━"
    )

    try:
        bot.send_message(LOG_CHANNEL_ID, report, parse_mode="Markdown")
        print(f"[Chronos] Pulse sent at {now.strftime('%H:%M')}")
    except Exception as e:
        print(f"[Chronos] Send failed: {e}")


if __name__ == "__main__":
    print(f"[Chronos] Starting with interval: {REPORT_INTERVAL}s")
    while True:
        send_pulse()
        time.sleep(REPORT_INTERVAL)
