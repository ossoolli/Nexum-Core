import logging
from nexum.gateway.base_adapter import PlatformAdapter

logger = logging.getLogger(__name__)

class DiscordAdapter(PlatformAdapter):
    def __init__(self, token: str):
        self.token = token
        logger.info("Discord Adapter initialized (Skeleton)")

    def listen(self):
        logger.info("Discord Adapter: Listening (Skeleton)...")

    def send_message(self, chat_id: str, text: str):
        logger.info(f"Discord Adapter: Sending to {chat_id}: {text}")

    def format_message(self, message: str) -> str:
        return f"**{message}**"
