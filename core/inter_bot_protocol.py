"""
core/inter_bot_protocol.py
بروتوكول التواصل بين NEXUM والـ sub-bots
"""
import json
import os
import subprocess
import requests
from typing import Optional
from core.env_config import REGISTRY_DIR, PYTHON_BIN

class BotManifest:
    """يصف sub-bot: اسمه، مساره، طريقة الاتصال، قدراته"""
    def __init__(self, data: dict):
        self.name = data.get("name", "unknown")
        self.path = data.get("path", "")
        self.port = data.get("port")
        self.token = data.get("telegram_token")
        self.capabilities = data.get("capabilities", [])
        self.status = data.get("status", "stopped")
        self.pid = data.get("pid")

    def to_dict(self) -> dict:
        return {
            "name": self.name, "path": self.path, "port": self.port,
            "telegram_token": self.token, "capabilities": self.capabilities,
            "status": self.status, "pid": self.pid
        }


class InterBotProtocol:
    """
    بروتوكول التواصل:
    1. NEXUM يُنشئ sub-bot (كود + manifest)
    2. NEXUM يُشغّل sub-bot كعملية منفصلة
    3. NEXUM يُرسل أوامر لـ sub-bot عبر HTTP أو Telegram
    4. sub-bot يُبلّغ NEXUM بالنتيجة
    """

    def __init__(self):
        self.registry_path = os.path.join(REGISTRY_DIR, "registry.json")
        self._load_registry()

    def _load_registry(self):
        if os.path.exists(self.registry_path):
            with open(self.registry_path, "r") as f:
                self._registry = json.load(f)
        else:
            self._registry = {}

    def _save_registry(self):
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        with open(self.registry_path, "w") as f:
            json.dump(self._registry, f, ensure_ascii=False, indent=2)

    def register_bot(self, manifest: dict) -> dict:
        """يسجّل sub-bot جديد في الـ registry"""
        name = manifest.get("name")
        if not name:
            return {"success": False, "error": "يجب أن يكون للـ bot اسم"}
        self._registry[name] = manifest
        self._save_registry()
        return {"success": True, "registered": name, "total": len(self._registry)}

    def start_bot(self, name: str) -> dict:
        """يُشغّل sub-bot كعملية منفصلة"""
        if name not in self._registry:
            return {"success": False, "error": f"Bot '{name}' غير مسجّل"}
        manifest = self._registry[name]
        bot_path = manifest.get("path")
        if not os.path.exists(bot_path):
            return {"success": False, "error": f"ملف البوت غير موجود: {bot_path}"}

        try:
            proc = subprocess.Popen(
                [PYTHON_BIN, bot_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            self._registry[name]["status"] = "running"
            self._registry[name]["pid"] = proc.pid
            self._save_registry()
            return {"success": True, "started": name, "pid": proc.pid}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def stop_bot(self, name: str) -> dict:
        """يوقف sub-bot"""
        if name not in self._registry:
            return {"success": False, "error": f"Bot '{name}' غير مسجّل"}
        pid = self._registry[name].get("pid")
        if pid:
            try:
                os.kill(pid, 9)
            except ProcessLookupError:
                pass
        self._registry[name]["status"] = "stopped"
        self._registry[name]["pid"] = None
        self._save_registry()
        return {"success": True, "stopped": name}

    def send_command(self, bot_name: str, command: str, data: dict = None) -> dict:
        """
        يُرسل أمراً لـ sub-bot عبر HTTP (إذا كان له port)
        البروتوكول: POST /nexum/command
        Body: {"command": "...", "data": {...}, "from": "nexum_core"}
        """
        if bot_name not in self._registry:
            return {"success": False, "error": f"Bot '{bot_name}' غير مسجّل"}
        port = self._registry[bot_name].get("port")
        if not port:
            return {"success": False, "error": "Bot ليس له HTTP port مُعرَّف"}
        try:
            resp = requests.post(
                f"http://localhost:{port}/nexum/command",
                json={"command": command, "data": data or {}, "from": "nexum_core"},
                timeout=10
            )
            return {"success": True, "response": resp.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_bots(self) -> list:
        """يعرض كل الـ sub-bots المسجّلين"""
        bots = []
        for name, manifest in self._registry.items():
            # تحقق من أن الـ process لا يزال يعمل
            pid = manifest.get("pid")
            if pid:
                try:
                    os.kill(pid, 0)
                    manifest["status"] = "running"
                except ProcessLookupError:
                    manifest["status"] = "stopped"
                    manifest["pid"] = None
            bots.append({"name": name, "status": manifest.get("status"), "pid": manifest.get("pid"),
                         "capabilities": manifest.get("capabilities", [])})
        self._save_registry()
        return bots

    def create_minimal_bot_template(self, bot_name: str, port: int, capabilities: list) -> str:
        """
        يولّد كود Python لـ sub-bot بسيط جاهز لاستقبال أوامر NEXUM.
        الـ sub-bot يحتوي على:
        - Telegram polling
        - HTTP endpoint لاستقبال أوامر NEXUM على /nexum/command
        """
        return f'''"""
{bot_name} — Sub-Bot مُدار بواسطة NEXUM CORE OS
تم إنشاؤه تلقائياً. القدرات: {", ".join(capabilities)}
"""
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import telebot
from dotenv import load_dotenv

load_dotenv()
bot = telebot.TeleBot(os.getenv("{bot_name.upper()}_TOKEN", ""), "0.0.0.0")
PORT = {port}

class NexumCommandHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/nexum/command":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            command = body.get("command", "")
            data = body.get("data", {{}})

            # معالجة الأوامر من NEXUM
            result = {{"status": "received", "command": command, "bot": "{bot_name}"}}
            # TODO: أضف منطق الأوامر هنا

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *args):
        pass  # كتم logs الـ HTTP

def start_http():
    server = HTTPServer(("localhost", PORT), NexumCommandHandler)
    server.serve_forever()

@bot.message_handler(commands=["start"])
def start(msg):
    bot.reply_to(msg, "🤖 {bot_name} — يعمل تحت إشراف NEXUM CORE OS")

if __name__ == "__main__":
    threading.Thread(target=start_http, daemon=True).start()
    print(f"🤖 {bot_name} online | HTTP:{PORT}")
    bot.infinity_polling()
'''


    def broadcast_to_platforms(self, message: str, platforms: list = None):
        """إرسال رسالة عبر منصات متعددة (Pillar 2)"""
        platforms = platforms or ["telegram"]
        results = {}

        if "discord" in platforms:
            try:
                from core.protocols.adapters.discord_adapter import discord_adapter
                results["discord"] = discord_adapter.send_message(os.getenv("DISCORD_CHANNEL_ID", ""), message)
            except Exception as e:
                results["discord_error"] = str(e)

        if "slack" in platforms:
            try:
                from core.protocols.adapters.slack_adapter import slack_adapter
                results["slack"] = slack_adapter.send_message(os.getenv("SLACK_CHANNEL_ID", ""), message)
            except Exception as e:
                results["slack_error"] = str(e)

        # التليجرام هو الأساسي دائماً
        if "telegram" in platforms:
            # افتراضياً يتم الإرسال عبر البوت الرئيسي أو sub-bots
            pass

        return results

inter_bot_protocol = InterBotProtocol()
