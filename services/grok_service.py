# -*- coding: utf-8 -*-
"""
services/grok_service.py
خدمة Grok (xAI) الاحتياطية المباشرة -- Nexum Pro (v7.2.5)
"""

import os
import logging
import httpx
from typing import Tuple, Optional

logger = logging.getLogger("nexum.grok")


class GrokService:
    """
    خدمة Grok من xAI المباشرة للاتصال بـ API عند تعطل المنصة السحابية.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("XAI_API_KEY", "").strip()
        self.api_url = "https://api.x.ai/v1/chat/completions"
        self._available = bool(self.api_key)
        
        if not self.api_key:
            logger.warning("[GrokService] No XAI_API_KEY found. Direct Grok service will be disabled.")

    @property
    def is_available(self) -> bool:
        return self._available

    def ask(self, prompt: str, model: str = "grok-beta") -> Tuple[str, None]:
        """
        الاستعلام المباشر من Grok (xAI).
        """
        if not self.is_available:
            return "❌ [GrokService] xAI API Key is missing. Service not available.", None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are Grok, a member of the sovereign Council of Sages of NEXUM PRO. Answer in a direct, technical, and precise manner."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(self.api_url, json=payload, headers=headers)
                
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return content, None
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"[GrokService] Request failed: {error_msg}")
                return f"❌ [GrokService] Error: {error_msg}", None
                
        except Exception as e:
            logger.error(f"[GrokService] Connection error: {e}")
            return f"❌ [GrokService] Connection Exception: {str(e)}", None


# Singleton
grok_service = GrokService()
