# -*- coding: utf-8 -*-
# agents/protocol_bridge.py
"""
🔌 ProtocolBridgeAgent — وكيل الاندماج بالبروتوكولات الخارجية (v1.0.0)
======================================================================
- ربط وتكامل NEXUM مع خدمات Redis و Webhooks الخارجية.
- تسجيل الأدوات تلقائياً في الـ (Tool Registry) لتمكين مجلس الحكماء من استخدامها.
- الحفاظ على سلامة النظام باستخدام معالجة الاستثناءات والاتصال الآمن.
"""

import os
import sys
import json
import logging
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from core.tool_registry import tool_registry

logger = logging.getLogger(__name__)

class ProtocolBridgeAgent:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        self._init_redis()
        self._register_tools()

    def _init_redis(self):
        try:
            import redis
            self.redis_client = redis.from_url(self.redis_url, socket_timeout=3)
            # فحص الاتصال للتأكد من خلوه من الأخطاء
            self.redis_client.ping()
            logger.info("[Bridge] Redis connection successfully verified.")
        except Exception as e:
            logger.warning(f"[Bridge] Redis not active or not installed. Running in mock-fallback mode: {e}")
            self.redis_client = None

    def _register_tools(self):
        """تسجيل الأدوات لخدمات مجلس الحكماء"""
        tool_registry.register_local_tool("publish_event", self.publish_event)
        tool_registry.register_local_tool("call_webhook", self.call_webhook)
        logger.info("[Bridge] Registered 'publish_event' and 'call_webhook' to tool_registry.")

    def publish_event(self, channel: str, payload: dict) -> str:
        """نشر أحداث تفاعلية عبر قنوات Redis باستخدام عقد الوكيل الموحد"""
        from protocols.agent_contract import AgentEvent, AgentContractValidator
        
        try:
            # ترميز الحمولة كـ bytes
            payload_bytes = json.dumps(payload, ensure_ascii=False).encode('utf-8')
            
            event = AgentEvent(
                sender="ProtocolBridgeAgent",
                topic=channel,
                payload=payload_bytes
            )
            
            # التحقق من صحة مخطط الحدث
            if not AgentContractValidator.validate_event(event):
                logger.warning("[Bridge] Event failed contract validation, proceeding with caution.")
                
            data_str = event.serialize()
        except Exception as e:
            logger.error(f"[Bridge] Failed to construct AgentEvent contract: {e}")
            data_str = json.dumps(payload, ensure_ascii=False)

        if self.redis_client:
            try:
                self.redis_client.publish(channel, data_str)
                return f"✅ [Redis] Published event contract on channel '{channel}' successfully."
            except Exception as e:
                return f"❌ [Redis] Publish failed: {e}"
        else:
            logger.info(f"[Bridge Mock] Redis AgentEvent published on '{channel}': {data_str}")
            return f"⚠️ [Mock Bridge] Published event contract on channel '{channel}' (Redis Offline)."

    async def call_webhook(self, url: str, data: dict) -> str:
        """استدعاء webhook خارجي بنمط غير متزامن"""
        try:
            import aiohttp
            logger.info(f"[Bridge] Sending POST webhook request to {url}...")
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, timeout=5) as response:
                    text = await response.text()
                    return f"✅ [Webhook] Status: {response.status}, Response: {text[:500]}"
        except Exception as e:
            logger.error(f"[Bridge] Webhook call failed: {e}")
            return f"❌ [Webhook] Request failed: {e}"

# Singleton context initialized later
protocol_bridge = ProtocolBridgeAgent()
