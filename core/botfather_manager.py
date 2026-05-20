import httpx
import logging

NEXUM_COMMANDS = [
    ("start",    "🚀 تشغيل NEXUM والقائمة الرئيسية"),
    ("menu",     "📋 عرض القائمة الرئيسية"),
    ("status",   "📊 حالة النظام الآن"),
    ("webforge", "🌐 بناء موقع أو تطبيق"),
    ("agents",   "🤖 إدارة الوكلاء"),
    ("bots",     "🤖 إدارة أسطول البوتات"),
    ("channels", "📢 إدارة القنوات"),
    ("monitor",  "📈 مراقبة النظام"),
    ("settings", "⚙️ الإعدادات"),
    ("broadcast","📣 بث رسالة لجميع القنوات"),
    ("build",    "🔨 بناء مشروع جديد بوصف"),
    ("cancel",   "❌ إلغاء العملية الحالية"),
]

class BotFatherManager:
    def __init__(self, token: str):
        self.token = token
        self.api_base = f"https://api.telegram.org/bot{token}"
    
    async def set_my_commands(self, commands=None, language_code="ar"):
        """يسجّل الأوامر في BotFather"""
        cmds = commands or NEXUM_COMMANDS
        payload = {
            "commands": [{"command": c, "description": d} for c, d in cmds],
            "language_code": language_code
        }
        async with httpx.AsyncClient() as client:
            try:
                res = await client.post(f"{self.api_base}/setMyCommands", json=payload)
                return res.json()
            except Exception as e:
                logging.error(f"BotFather Error: {e}")
                return {"ok": False, "error": str(e)}
    
    async def set_chat_menu_button(self, web_app_url: str, button_text: str = "🔱 NEXUM"):
        """يضبط زر القائمة ليفتح Mini App"""
        payload = {
            "menu_button": {
                "type": "web_app",
                "text": button_text,
                "web_app": {"url": web_app_url}
            }
        }
        async with httpx.AsyncClient() as client:
            try:
                res = await client.post(f"{self.api_base}/setChatMenuButton", json=payload)
                return res.json()
            except Exception as e:
                logging.error(f"BotFather MenuButton Error: {e}")
                return {"ok": False, "error": str(e)}

    async def set_my_description(self, description: str, language_code: str = "ar"):
        payload = {"description": description, "language_code": language_code}
        async with httpx.AsyncClient() as client:
            await client.post(f"{self.api_base}/setMyDescription", json=payload)

    async def sync_all_settings(self, webapp_url: str):
        """مزامنة كل شيء عند الإقلاع"""
        await self.set_my_commands(language_code="ar")
        await self.set_my_commands(language_code="en")
        if webapp_url:
            await self.set_chat_menu_button(webapp_url)
        print("✅ NEXUM: BotFather settings synced.")
