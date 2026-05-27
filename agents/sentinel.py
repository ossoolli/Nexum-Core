# -*- coding: utf-8 -*-
# agents/sentinel.py
"""
🛡️ SentinelAgent — الحارس الأمني والرقابي المستمر (v1.0.0)
===========================================================
- يعمل في الخلفية لمراقبة الموارد المادية (CPU, RAM, Disk).
- فحص العمليات النشطة ومطابقتها مع القائمة البيضاء لرصد العمليات المشبوهة.
- البث التلقائي للتنبيهات الفورية عبر التليجرام للمطور في حالة الخطر.
"""

import os
import sys
import time
import asyncio
import logging
import psutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

logger = logging.getLogger(__name__)

class SentinelAgent:
    THRESHOLDS = {"cpu": 85, "ram": 90, "disk": 95}
    WHITELIST = {"python", "python3", "pm2", "redis-server", "node", "systemd", "bash", "sh", "sshd"}

    def __init__(self):
        self.active = True

    async def watch(self, bot, channel_id: int, interval: int = 60):
        """حلقة رقابية دائرية مستمرة لرصد شذوذ النظام"""
        logger.info(f"🛡️ [Sentinel] Starting security watchdog loop on channel {channel_id}...")
        while self.active:
            try:
                alerts = []
                
                # 1. فحص المعالج
                cpu = psutil.cpu_percent(interval=1)
                if cpu > self.THRESHOLDS["cpu"]:
                    alerts.append(f"⚠️ استهلاك المعالج حرج: {cpu}%")

                # 2. فحص الذاكرة العشوائية
                ram = psutil.virtual_memory().percent
                if ram > self.THRESHOLDS["ram"]:
                    alerts.append(f"⚠️ استهلاك الذاكرة حرج: {ram}%")

                # 3. فحص القرص
                disk = psutil.disk_usage("/").percent
                if disk > self.THRESHOLDS["disk"]:
                    alerts.append(f"⚠️ مساحة القرص حرجة: {disk}%")

                # 4. فحص العمليات غير المصرح بها
                suspicious = self._scan_processes()
                if suspicious:
                    alerts.append(f"🚨 عمليات مجهولة أو مستهلكة خارج القائمة البيضاء: {', '.join(suspicious)}")

                # 5. بث التنبيهات فوراً
                if alerts:
                    alert_msg = (
                        f"🛡️ <b>[SENTINEL ALERT SYSTEM]</b>\n"
                        f"----------------------------------------\n"
                        + "\n".join(alerts) + "\n"
                        f"----------------------------------------\n"
                        f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    try:
                        bot.send_message(channel_id, alert_msg, parse_mode="HTML")
                        logger.warning(f"[Sentinel] Alerts broadcasted to {channel_id}!")
                    except Exception as e:
                        logger.error(f"[Sentinel] Failed to send Telegram alert: {e}")

            except Exception as e:
                logger.error(f"[Sentinel] Watch loop encountered error: {e}")

            await asyncio.sleep(interval)

    def _scan_processes(self) -> list:
        """مسح ومطابقة العمليات ضد القائمة البيضاء"""
        suspicious = []
        try:
            for proc in psutil.process_iter(['name', 'cpu_percent']):
                try:
                    name = proc.info['name']
                    cpu = proc.info['cpu_percent']
                    # رصد العمليات المجهولة التي تستهلك المعالج أو غير مسجلة
                    if name and name not in self.WHITELIST:
                        if cpu and cpu > 45.0:
                            suspicious.append(f"{name} ({cpu}%)")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            logger.error(f"[Sentinel] Process scan failed: {e}")
        return suspicious

# Singleton
sentinel_agent = SentinelAgent()
