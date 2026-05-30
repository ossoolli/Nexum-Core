# -*- coding: utf-8 -*-
"""
💬 SlackAdapter — محول منصة سلاك (v1.0.0)
========================================
- يربط NEXUM CORE بقنوات Slack.
- يدعم استقبال الأوامر وإرسال التنبيهات.
"""

import os
import logging
import requests
from typing import Dict, Any

logger = logging.getLogger("nexum.protocols.slack")

class SlackAdapter:
    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        self.bot_token = os.getenv("SLACK_BOT_TOKEN")

    def send_message(self, channel_id: str, text: str) -> bool:
        """إرسال رسالة إلى قناة سلاك"""
        if self.webhook_url:
            # استخدام Webhook إذا توفر
            payload = {"text": text}
            resp = requests.post(self.webhook_url, json=payload)
            return resp.status_code == 200
            
        if self.bot_token:
            # استخدام Web API
            url = "https://slack.com/api/chat.postMessage"
            headers = {
                "Authorization": f"Bearer {self.bot_token}",
                "Content-Type": "application/json; charset=utf-8"
            }
            payload = {
                "channel": channel_id,
                "text": text
            }
            resp = requests.post(url, headers=headers, json=payload)
            return resp.status_code == 200 and resp.json().get("ok", False)
            
        return False

slack_adapter = SlackAdapter()
