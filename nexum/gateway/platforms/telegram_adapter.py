import logging
from nexum.gateway.base_adapter import PlatformAdapter

logger = logging.getLogger(__name__)

class TelegramAdapter(PlatformAdapter):
    def __init__(self, bot, runner):
        self.bot = bot
        self.runner = runner

    def listen(self):
        logger.info("🔱 Telegram Adapter: Listening...")
        self.runner.run()

    def send_message(self, chat_id: str, text: str):
        # Implementation depends on the bot library
        self.bot.send_message(chat_id=chat_id, text=text)

    def format_message(self, message: str) -> str:
        # Simple telegram formatting
        return message
