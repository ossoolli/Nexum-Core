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

    def get_system_data(self) -> dict:
        """جلب البيانات الخام لتنسيقها خارجياً"""
        cpu_usage = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net = psutil.net_io_counters()

        uptime_result = executor.execute("uptime")
        uptime = uptime_result.get('output', 'N/A').strip()

        return {
            "hostname": self.hostname,
            "cpu": cpu_usage,
            "ram": {
                "percent": mem.percent,
                "used": mem.used // (1024**2),
                "total": mem.total // (1024**2),
                "available": mem.available // (1024**2),
            },
            "disk": {
                "percent": disk.percent,
                "used": disk.used // (1024**3),
                "free": disk.free // (1024**3),
                "total": disk.total // (1024**3),
            },
            "net": {
                "sent": net.bytes_sent // (1024**2),
                "recv": net.bytes_recv // (1024**2),
                "packets_sent": net.packets_sent,
                "packets_recv": net.packets_recv
            },
            "uptime": uptime
        }

    def get_cpu_details(self) -> dict:
        return {
            "percent": psutil.cpu_percent(interval=1),
            "count": psutil.cpu_count(logical=True),
            "freq": psutil.cpu_freq().current if hasattr(psutil.cpu_freq(), 'current') else None,
            "per_cpu": psutil.cpu_percent(interval=1, percpu=True)
        }

    def get_pulse_report(self) -> str:
        # نبقي هذه الدالة للتوافق العكسي
        data = self.get_system_data()
        
        report = (
            f"📊 <b>تقرير حالة السيرفر: {html.escape(data['hostname'])}</b>\n"
            f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"➖➖➖➖➖➖➖➖➖➖\n"
            f"🖥️ <b>CPU:</b> <code>{data['cpu']}%</code>\n"
            f"🧠 <b>RAM:</b> <code>{data['ram']['percent']}%</code> "
            f"(مستخدم: {data['ram']['used']} MB / {data['ram']['total']} MB)\n"
            f"💾 <b>Disk:</b> <code>{data['disk']['percent']}%</code> "
            f"(متبقي: {data['disk']['free']} GB)\n"
            f"🌐 <b>Network:</b> ⬆️ {data['net']['sent']}MB "
            f"| ⬇️ {data['net']['recv']}MB\n"
            f"⏱️ <b>Uptime:</b> <code>{data['uptime']}</code>\n"
        )

        warnings = []
        if data['cpu'] > 80: warnings.append("⚠️ ضغط عالٍ على المعالج!")
        if data['ram']['percent'] > 90: warnings.append("⚠️ الذاكرة ممتلئة تقريباً!")
        if data['disk']['percent'] > 95: warnings.append("⚠️ مساحة القرص حرجة!")

        if warnings:
            report += "\n<b>🚨 تنبيهات عاجلة:</b>\n" + "\n".join(warnings)
        else:
            report += "\n🟢 <b>جميع المؤشرات ضمن النطاق الآمن.</b>"

        return report

monitor_agent = MonitorAgent()
