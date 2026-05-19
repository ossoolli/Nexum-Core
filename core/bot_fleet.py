"""
🤖 BotFleet — أسطول البوتات الموزّع
====================================
ينشئ ويدير بوتات Telegram مستقلة كعمليات PM2.
"""
import os
import sys
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

BOTS_DIR = os.path.join(BASE_DIR, "registry", "bots")
REGISTRY_PATH = os.path.join(BASE_DIR, "storage", "bots_registry.json")

os.makedirs(BOTS_DIR, exist_ok=True)
os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)


class BotFleet:
    """مدير أسطول البوتات — ينشئ ويشغّل ويوقف بوتات Telegram"""

    def __init__(self):
        self._registry = self._load_registry()

    # ═══════════════════════════════════════
    # السجل (Registry)
    # ═══════════════════════════════════════

    def _load_registry(self) -> dict:
        try:
            if os.path.exists(REGISTRY_PATH):
                with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
        return {"bots": {}}

    def _save_registry(self):
        try:
            with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
                json.dump(self._registry, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"[BotFleet] Registry save error: {e}")

    # ═══════════════════════════════════════
    # إنشاء بوت جديد
    # ═══════════════════════════════════════

    def spawn_bot(
        self,
        name: str,
        token: str,
        personality: str,
        capabilities: list = None,
        admin_id: int = 0
    ) -> dict:
        """
        ينشئ بوت Telegram كامل ويشغّله كعملية PM2.
        1. يولّد ملف bot.py من القالب
        2. يحفظ في registry/bots/{name}/
        3. يشغّل عبر PM2
        4. يسجّل في bots_registry.json
        """
        try:
            capabilities = capabilities or ["chat"]
            safe_name = name.replace(" ", "_").lower()
            bot_dir = os.path.join(BOTS_DIR, safe_name)
            os.makedirs(bot_dir, exist_ok=True)

            # توليد الكود
            bot_code = self._generate_bot_code(safe_name, token, personality, capabilities, admin_id)
            bot_path = os.path.join(bot_dir, "bot.py")
            with open(bot_path, "w", encoding="utf-8") as f:
                f.write(bot_code)

            # إنشاء .env للبوت
            env_path = os.path.join(bot_dir, ".env")
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(f"BOT_TOKEN={token}\nADMIN_ID={admin_id}\n")

            # تشغيل عبر PM2
            pm2_name = f"nexum-bot-{safe_name}"
            try:
                subprocess.run(
                    ["pm2", "start", bot_path, "--name", pm2_name,
                     "--interpreter", "python3"],
                    capture_output=True, text=True, timeout=15
                )
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                print(f"[BotFleet] PM2 start warning: {e}")

            # تسجيل في السجل
            masked_token = token[:10] + "***" + token[-5:]
            self._registry["bots"][safe_name] = {
                "token": masked_token,
                "pm2_name": pm2_name,
                "status": "RUNNING",
                "personality": personality,
                "capabilities": capabilities,
                "admin_id": admin_id,
                "created_at": datetime.utcnow().isoformat(),
                "path": bot_path,
            }
            self._save_registry()

            return {
                "status": "success",
                "name": safe_name,
                "pm2_name": pm2_name,
                "path": bot_path,
                "message": f"✅ بوت '{safe_name}' تم إنشاؤه وتشغيله بنجاح."
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    # ═══════════════════════════════════════
    # إدارة البوتات
    # ═══════════════════════════════════════

    def kill_bot(self, name: str) -> str:
        """إيقاف بوت"""
        try:
            pm2_name = f"nexum-bot-{name}"
            subprocess.run(["pm2", "stop", pm2_name], capture_output=True, timeout=10)
            if name in self._registry["bots"]:
                self._registry["bots"][name]["status"] = "STOPPED"
                self._save_registry()
            return f"⏹️ تم إيقاف بوت '{name}'."
        except Exception as e:
            return f"❌ فشل إيقاف '{name}': {e}"

    def restart_bot(self, name: str) -> str:
        """إعادة تشغيل بوت"""
        try:
            pm2_name = f"nexum-bot-{name}"
            subprocess.run(["pm2", "restart", pm2_name], capture_output=True, timeout=10)
            if name in self._registry["bots"]:
                self._registry["bots"][name]["status"] = "RUNNING"
                self._save_registry()
            return f"🔄 تم إعادة تشغيل '{name}'."
        except Exception as e:
            return f"❌ فشل إعادة تشغيل '{name}': {e}"

    def update_bot(self, name: str, new_code: str) -> str:
        """تحديث كود بوت وإعادة تشغيله"""
        try:
            bot_info = self._registry["bots"].get(name)
            if not bot_info:
                return f"❌ بوت '{name}' غير موجود."
            with open(bot_info["path"], "w", encoding="utf-8") as f:
                f.write(new_code)
            return self.restart_bot(name)
        except Exception as e:
            return f"❌ فشل تحديث '{name}': {e}"

    def list_bots(self) -> list:
        """قائمة جميع البوتات"""
        self._registry = self._load_registry()
        result = []
        for name, info in self._registry.get("bots", {}).items():
            result.append({
                "name": name,
                "status": info.get("status", "UNKNOWN"),
                "personality": info.get("personality", "")[:50],
                "pm2_name": info.get("pm2_name", ""),
                "created_at": info.get("created_at", ""),
            })
        return result

    def get_bot_stats(self, name: str) -> dict:
        """إحصاءات PM2 للبوت"""
        try:
            pm2_name = f"nexum-bot-{name}"
            result = subprocess.run(
                ["pm2", "jlist"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                procs = json.loads(result.stdout)
                for p in procs:
                    if p.get("name") == pm2_name:
                        mon = p.get("monit", {})
                        return {
                            "name": name,
                            "status": p.get("pm2_env", {}).get("status", "unknown"),
                            "cpu": mon.get("cpu", 0),
                            "memory_mb": round(mon.get("memory", 0) / (1024 * 1024), 1),
                            "restarts": p.get("pm2_env", {}).get("restart_time", 0),
                            "uptime": p.get("pm2_env", {}).get("pm_uptime", 0),
                        }
            return {"name": name, "status": "not_found"}
        except Exception as e:
            return {"name": name, "status": "error", "error": str(e)}

    # ═══════════════════════════════════════
    # توليد الكود
    # ═══════════════════════════════════════

    def _generate_bot_code(self, name, token, personality, capabilities, admin_id):
        """توليد كود بوت Telegram كامل من القالب"""
        caps_code = self._build_capabilities_code(capabilities)

        return f'''"""
🤖 {name} — Generated by NEXUM BotFleet
Personality: {personality[:80]}
"""
import os
import telebot
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

bot = telebot.TeleBot(os.getenv("BOT_TOKEN", "{token}"))
ADMIN_ID = int(os.getenv("ADMIN_ID", "{admin_id}"))

SYSTEM_PERSONA = """{personality}"""

@bot.message_handler(commands=["start"])
def cmd_start(message):
    bot.send_message(
        message.chat.id,
        f"مرحباً! أنا **{name}**.\\n{{SYSTEM_PERSONA[:100]}}\\n\\nكيف أقدر أساعدك؟",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    try:
{caps_code}
    except Exception as e:
        bot.reply_to(message, f"❌ خطأ: {{e}}")

if __name__ == "__main__":
    print("🤖 {name} — Online.")
    bot.infinity_polling()
'''

    def _build_capabilities_code(self, capabilities):
        """بناء كود القدرات"""
        lines = []
        if "chat" in capabilities:
            lines.append('        bot.reply_to(message, f"تلقيت: {message.text}")')
        if "web_search" in capabilities:
            lines.append('        # TODO: integrate web search')
        if "broadcast" in capabilities:
            lines.append('        # TODO: integrate channel broadcast')
        if not lines:
            lines.append('        bot.reply_to(message, "مرحباً!")')
        return "\n".join(lines)


# Singleton
bot_fleet = BotFleet()
