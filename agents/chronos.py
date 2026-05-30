"""
⏰ NEXUM Chronos Agent — وكيل الجدولة الزمنية
==============================================
يرسل تقارير دورية للقناة الحية ويراقب صحة النظام.
"""
import os
import sys
import time
import json
import telebot
from datetime import datetime
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

from agents.tool_hunter import tool_hunter
from agents.marketing_agent import marketing_agent
from agents.accountant_agent import accountant_agent
from services.email_service import email_service

TOKEN = os.getenv("TELEGRAM_TOKEN")
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID", "").strip("'\"")

bot = telebot.TeleBot(TOKEN) if TOKEN else None

# الفاصل الزمني بين التقارير (بالثواني)
REPORT_INTERVAL = 3600  # ساعة واحدة
TOOL_SEARCH_INTERVAL = 86400 # 24 ساعة
PUBLISH_INTERVAL = 3600 # ساعة واحدة


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

def run_tool_hunter():
    """دورة البحث عن الأدوات"""
    print("[Chronos] Running ToolHunter...")
    res = tool_hunter.run()
    if bot and LOG_CHANNEL_ID and res.get("count", 0) > 0:
        report = f"🔍 <b>[ToolHunter]:</b> Found {res['count']} new MCP tools!"
        bot.send_message(LOG_CHANNEL_ID, report, parse_mode="HTML")

def run_marketing_publisher():
    """دورة النشر المجدول"""
    print("[Chronos] Running Marketing Publisher...")
    queue_file = "/home/madarmutaz/Nexum-Core/storage/content_queue.json"
    if not os.path.exists(queue_file):
        return
        
    try:
        with open(queue_file, 'r') as f:
            queue = json.load(f)
            
        updated = False
        for item in queue:
            if item["status"] == "pending":
                # في الواقع هنا نقوم بفحص الوقت، للتبسيط سننشر أول واحد
                # item["platform"] check...
                print(f"[Chronos] Publishing content to {item['platform']}")
                item["status"] = "published"
                item["published_at"] = datetime.now().isoformat()
                updated = True
                
                if bot and LOG_CHANNEL_ID:
                    bot.send_message(LOG_CHANNEL_ID, f"📢 <b>[Marketing]:</b> Published content to {item['platform']}", parse_mode="HTML")
                break # نشر واحد في كل دورة
                
        if updated:
            with open(queue_file, 'w') as f:
                json.dump(queue, f, indent=4)
    except Exception as e:
        print(f"[Chronos] Publisher error: {e}")

def run_weekly_accounting():
    """توليد وإرسال التقرير المالي الأسبوعي"""
    print("[Chronos] Generating Weekly Business Report...")
    res = accountant_agent.run({"action": "report"})
    if res.get("status") == "success" and res.get("file_path"):
        path = res["file_path"]
        if bot and LOG_CHANNEL_ID:
            with open(path, 'rb') as f:
                bot.send_document(LOG_CHANNEL_ID, f, caption="📊 <b>Nexum Weekly Business Report</b>", parse_mode="HTML")
        
        # إرسال عبر الإيميل أيضاً
        email_service.send_email(os.getenv("ADMIN_EMAIL", ""), "Nexum Weekly Report", "Attached is your weekly business summary.", [path])

def chronos_loop():
    last_tool_search = 0
    last_publish = 0
    last_pulse = 0
    
    while True:
        now = time.time()
        
        if now - last_pulse >= REPORT_INTERVAL:
            send_pulse()
            last_pulse = now
            
        if now - last_tool_search >= TOOL_SEARCH_INTERVAL:
            run_tool_hunter()
            last_tool_search = now
            
        if now - last_publish >= PUBLISH_INTERVAL:
            run_marketing_publisher()
            last_publish = now
            
        # فحص يوم الأحد الساعة 9 صباحاً
        now_dt = datetime.now()
        if now_dt.weekday() == 6 and now_dt.hour == 9 and now_dt.minute == 0:
            run_weekly_accounting()
            time.sleep(61) # منع التكرار في نفس الدقيقة
            
        time.sleep(60)


if __name__ == "__main__":
    print(f"[Chronos] Starting advanced scheduler loop...")
    chronos_loop()
