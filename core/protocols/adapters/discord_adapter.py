# -*- coding: utf-8 -*-
"""
🎧 DiscordAdapter — محول منصة ديسكورد (v1.0.0)
===========================================
- يربط NEXUM CORE بقنوات Discord.
- يدعم استقبال الأوامر وإرسال التنبيهات.
"""

import os
import logging
import requests
from typing import Dict, Any

logger = logging.getLogger("nexum.protocols.discord")

class DiscordAdapter:
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        self.bot_token = os.getenv("DISCORD_BOT_TOKEN")

    def send_message(self, channel_id: str, text: str) -> bool:
        """إرسال رسالة إلى قناة ديسكورد"""
        if self.webhook_url:
            # استخدام Webhook إذا توفر (سهل وسريع)
            payload = {"content": text}
            resp = requests.post(self.webhook_url, json=payload)
            return resp.status_code == 204
            
        if self.bot_token:
            # استخدام Bot API
            url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
            headers = {"Authorization": f"Bot {self.bot_token}", "Content-Type": "application/json"}
            payload = {"content": text}
            resp = requests.post(url, headers=headers, json=payload)
            return resp.status_code == 200
            
        return False

discord_adapter = DiscordAdapter()
