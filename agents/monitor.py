import os
import psutil
import platform
import html
from datetime import datetime
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from core.executor import executor

class MonitorAgent:
    def __init__(self):
        self.hostname = platform.node()

    def get_pulse_report(self) -> str:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory    = psutil.virtual_memory()
        disk      = psutil.disk_usage('/')
        net       = psutil.net_io_counters()

        uptime_result = executor.execute("uptime")
        uptime = uptime_result.get('output', 'N/A').strip()

        report = (
            f"📊 <b>تقرير حالة السيرفر: {html.escape(self.hostname)}</b>\n"
            f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"➖➖➖➖➖➖➖➖➖➖\n"
            f"🖥️ <b>CPU:</b> <code>{cpu_usage}%</code>\n"
            f"🧠 <b>RAM:</b> <code>{memory.percent}%</code> "
            f"(مستخدم: {memory.used // (1024**2)} MB / {memory.total // (1024**2)} MB)\n"
            f"💾 <b>Disk:</b> <code>{disk.percent}%</code> "
            f"(متبقي: {disk.free // (1024**3)} GB)\n"
            f"🌐 <b>Network:</b> ⬆️ {net.bytes_sent // (1024**2)}MB "
            f"| ⬇️ {net.bytes_recv // (1024**2)}MB\n"
            f"⏱️ <b>Uptime:</b> <code>{uptime}</code>\n"
        )

        # تحذيرات ذكية
        warnings = []
        if cpu_usage > 80:        warnings.append("⚠️ ضغط عالٍ على المعالج!")
        if memory.percent > 90:   warnings.append("⚠️ الذاكرة ممتلئة تقريباً!")
        if disk.percent > 95:     warnings.append("⚠️ مساحة القرص حرجة!")

        if warnings:
            report += "\n<b>🚨 تنبيهات عاجلة:</b>\n" + "\n".join(warnings)
        else:
            report += "\n🟢 <b>جميع المؤشرات ضمن النطاق الآمن.</b>"

        return report

    # توافق مع الاستدعاء القديم
    def get_system_status(self) -> str:
        return self.get_pulse_report()

monitor_agent = MonitorAgent()
