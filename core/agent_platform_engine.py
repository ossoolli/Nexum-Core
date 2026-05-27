# -*- coding: utf-8 -*-
# core/agent_platform_engine.py
"""
🔱 AgentPlatformEngine — المحرك السيادي المركزي لمجلس الحكماء
==============================================================
يستخدم مفتاح Agent Platform API Key من Google لاستدعاء جميع
الموديلات (Gemini + Claude + GPT) عبر Vertex AI Model Garden مركزياً.

⚠️ هذا المفتاح يعمل حصرياً بوضع vertexai=True عبر Vertex AI endpoints
   وليس عبر generativelanguage.googleapis.com العادي.

- المزود الأساسي (Primary): Agent Platform API Key عبر Vertex AI
- المزود الثانوي (Fallback): OpenRouter / OpenAI / GeminiService المفاتيح المباشرة

الأفضلية:
  Agent Platform API (Vertex AI) → OpenRouter/OpenAI → Gemini API Key
"""

import os
import logging
from typing import Tuple, Optional

logger = logging.getLogger("nexum.agent_platform")

# خريطة مطابقة الموديلات لمجلس الحكماء مع Vertex AI Model Garden
# ⚠️ يجب استخدام أسماء الموديلات المتاحة فعلياً على المشروع
MODEL_MAPPING = {
    # Google Models — الموديلات المستقرة الحديثة
    "gemini-3.5-flash": "gemini-3.5-flash",
    "gemini-3.1-flash-lite": "gemini-3.1-flash-lite",
    "gemini-2.5-flash": "gemini-2.5-flash",
    "gemini-2.5-pro": "gemini-2.5-pro",
    "gemini-2.5-flash-lite": "gemini-2.5-flash-lite",
    # Third-party via Model Garden (Vertex AI publishers)
    # ⚠️ خرائط مطابقة مع النماذج الفعلية المتوفرة على منصة Google Cloud
    "anthropic/claude-3-5-sonnet": "publishers/anthropic/models/claude-3-5-sonnet",
    "anthropic/claude-3-5-sonnet-v2": "publishers/anthropic/models/claude-3-5-sonnet-v2",
    "anthropic/claude-3-5-haiku": "publishers/anthropic/models/claude-3-5-haiku",
    "anthropic/claude-3-opus": "publishers/anthropic/models/claude-3-opus",
    
    # تحويل الموديلات الافتراضية والاسمية إلى النماذج المستقرة المتوفرة
    "anthropic/claude-sonnet-4": "publishers/anthropic/models/claude-3-5-sonnet",
    "anthropic/claude-opus-4": "publishers/anthropic/models/claude-3-opus",
    "anthropic/claude-sonnet-4.5": "publishers/anthropic/models/claude-3-5-sonnet",
    "anthropic/claude-haiku-4": "publishers/anthropic/models/claude-3-5-haiku",
    
    # Legacy aliases
    "claude-opus-4": "publishers/anthropic/models/claude-3-opus",
    "claude-sonnet-4": "publishers/anthropic/models/claude-3-5-sonnet",
    "claude-3-5-sonnet": "publishers/anthropic/models/claude-3-5-sonnet",
    "claude-3-5-sonnet-v2": "publishers/anthropic/models/claude-3-5-sonnet-v2",
    
    # GPT — يُعالج عبر OpenAI مباشرة (غير متاح في Model Garden)
    # يُوجّه كاحتياطي إلى Gemini إن لم يتوفر مفتاح OpenAI
    "gpt-4o": "gemini-3.5-flash",
    "gpt-4o-mini": "gemini-3.5-flash",
    
    # Grok via Model Garden / Partner Publishers or Custom Endpoints
    "grok-beta": "publishers/xai/models/grok-beta",
    "grok-2": "publishers/xai/models/grok-2",
}


class AgentPlatformEngine:
    """
    يوفر واجهة موحدة `ask(prompt, model)` لاستدعاء أي موديل
    عبر مفتاح Agent Platform API Key عبر Vertex AI Model Garden.

    ⚠️ يعمل حصرياً بوضع vertexai=True
    """

    def __init__(self):
        # تحميل الإعدادات
        self.api_key = ""
        self.project = ""
        self.location = "us-central1"

        try:
            from nexum.config import config
            if config:
                self.api_key = getattr(config, "agent_platform_api_key", "")
                self.project = getattr(config, "google_cloud_project", "")
                self.location = getattr(config, "google_cloud_location", "us-central1")
        except ImportError:
            pass

        # الاحتياط لمتغيرات البيئة
        if not self.api_key:
            self.api_key = os.getenv("AGENT_PLATFORM_API_KEY", "").strip()
        if not self.project:
            self.project = os.getenv("GOOGLE_CLOUD_PROJECT", "")
        if not self.location or self.location == "global":
            self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

        self.client = None
        self._available = False

        if not self.api_key:
            logger.warning(
                "[AgentPlatform] No AGENT_PLATFORM_API_KEY found. "
                "Engine will be disabled."
            )
            return

        try:
            from google import genai

            # ⚠️ المفتاح يعمل حصرياً بوضع Vertex AI
            self.client = genai.Client(
                vertexai=True,
                api_key=self.api_key,
            )
            self._available = True
            logger.info(
                f"[AgentPlatform] Engine initialized with Vertex AI mode. "
                f"Location: {self.location}"
            )
        except ImportError:
            logger.error(
                "[AgentPlatform] google-genai package not installed. "
                "Install with: pip install google-genai"
            )
        except Exception as e:
            logger.error(f"[AgentPlatform] Failed to initialize client: {e}")

    @property
    def is_available(self) -> bool:
        """تحقق من جاهزية المحرك"""
        return self._available and self.client is not None

    def ask(self, prompt: str, model: str = "gemini-3.5-flash") -> Tuple[str, None]:
        """
        استدعاء موديل عبر Vertex AI Agent Platform.

        Args:
            prompt: النص المطلوب إرساله
            model: اسم الموديل (e.g. gemini-2.5-flash, claude-opus-4)

        Returns:
            Tuple[str, None]: (النص المولد, None)
        """
        if not self.is_available:
            return "❌ [AgentPlatform] Engine not available (missing API key or client).", None

        # مطابقة الموديل المطلوب مع معرّف Vertex AI
        target_model = MODEL_MAPPING.get(model, model)
        logger.info(f"[AgentPlatform] Routing '{model}' -> '{target_model}' via Vertex AI...")

        try:
            response = self.client.models.generate_content(
                model=target_model,
                contents=prompt,
            )

            if response and response.text:
                return response.text, None

            return "⚠️ [AgentPlatform] Empty response from model.", None

        except Exception as e:
            error_msg = str(e)
            logger.error(
                f"[AgentPlatform] Model '{model}' (-> '{target_model}') failed: {error_msg}"
            )
            return f"❌ خطأ في Agent Platform ({model}): {error_msg}", None

    def get_status(self) -> dict:
        """تقرير حالة المحرك"""
        return {
            "engine": "AgentPlatformEngine",
            "available": self.is_available,
            "api_key_set": bool(self.api_key),
            "mode": "Vertex AI",
            "location": self.location,
            "client_ready": self.client is not None,
        }


# ═══════════════════════════════════════════════════════
# Singleton
# ═══════════════════════════════════════════════════════
agent_platform = AgentPlatformEngine()
