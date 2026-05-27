# -*- coding: utf-8 -*-
# core/agent_platform_engine.py
"""
🔱 AgentPlatformEngine — المحرك السيادي المركزي لمجلس الحكماء
==============================================================
يستخدم مفتاح Agent Platform API Key من Google لاستدعاء جميع
الموديلات (Gemini + Claude + GPT) عبر Model Garden مركزياً.

- المزود الأساسي (Primary): Agent Platform API Key عبر google.genai.Client
- المزود الثانوي (Fallback): OpenRouter / OpenAI المفاتيح المباشرة

الأفضلية:
  Agent Platform API → OpenRouter/OpenAI → Gemini Fallback Alternate
"""

import os
import logging
from typing import Tuple, Optional

logger = logging.getLogger("nexum.agent_platform")

# خريطة مطابقة الموديلات لمجلس الحكماء مع Model Garden (Vertex AI)
MODEL_MAPPING = {
    "anthropic/claude-opus-4.6": "publishers/anthropic/models/claude-3-opus",
    "claude-opus-4": "publishers/anthropic/models/claude-3-opus",
    "gpt-5.4-nano": "gemini-2.5-flash",  # كبديل ذكي سريع داخل Model Garden
    "gemini-3.5-flash": "gemini-3.5-flash",
}

class AgentPlatformEngine:
    """
    يوفر واجهة موحدة `ask(prompt, model)` لاستدعاء أي موديل
    عبر مفتاح Agent Platform API Key من Google Model Garden.
    """

    def __init__(self):
        # تحميل الإعدادات
        self.api_key = ""
        self.use_vertex = False
        self.project = ""
        self.location = "global"
        
        try:
            from nexum.config import config
            if config:
                self.api_key = getattr(config, "agent_platform_api_key", "")
                self.use_vertex = getattr(config, "google_genai_use_vertexai", False)
                self.project = getattr(config, "google_cloud_project", "")
                self.location = getattr(config, "google_cloud_location", "global")
        except ImportError:
            pass

        # الاحتياط لمتغيرات البيئة
        if not self.api_key:
            self.api_key = os.getenv("AGENT_PLATFORM_API_KEY", "").strip()
        if not self.project:
            self.project = os.getenv("GOOGLE_CLOUD_PROJECT", "")
        if not self.location:
            self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "global")

        self.client = None
        self._available = False

        if not self.api_key and not self.use_vertex:
            logger.warning(
                "[AgentPlatform] No AGENT_PLATFORM_API_KEY or Vertex AI config found. "
                "Engine will be disabled."
            )
            return

        try:
            from google import genai
            from google.genai.types import HttpOptions

            if self.use_vertex:
                # وضع Vertex AI مع ADC
                os.environ.setdefault("GOOGLE_CLOUD_PROJECT", self.project)
                os.environ.setdefault("GOOGLE_CLOUD_LOCATION", self.location)
                os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
                self.client = genai.Client(http_options=HttpOptions(api_version="v1"))
                self._available = True
                logger.info("[AgentPlatform] Engine initialized with Vertex AI/ADC.")
            else:
                # وضع API Key لـ Agent Platform
                self.client = genai.Client(api_key=self.api_key)
                self._available = True
                logger.info("[AgentPlatform] Engine initialized with Agent Platform API Key.")
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
        استدعاء موديل عبر Agent Platform API.

        Args:
            prompt: النص المطلوب إرساله
            model: اسم الموديل (e.g. gemini-3.5-flash, claude-opus-4, gpt-5.4-nano)

        Returns:
            Tuple[str, None]: (النص المولد, None)
        """
        if not self.is_available:
            return f"❌ [AgentPlatform] Engine not available (missing API key or client).", None

        # مطابقة الموديل المطلوب مع معرّف Model Garden
        target_model = MODEL_MAPPING.get(model, model)
        logger.info(f"[AgentPlatform] Routing model '{model}' -> '{target_model}' in Model Garden...")

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
            logger.error(f"[AgentPlatform] Model '{model}' (mapped to '{target_model}') call failed: {error_msg}")
            return f"❌ خطأ في Agent Platform ({model}): {error_msg}", None

    def get_status(self) -> dict:
        """تقرير حالة المحرك"""
        return {
            "engine": "AgentPlatformEngine",
            "available": self.is_available,
            "api_key_set": bool(self.api_key),
            "use_vertex": self.use_vertex,
            "client_ready": self.client is not None,
        }


# ═══════════════════════════════════════════════════════
# Singleton
# ═══════════════════════════════════════════════════════
agent_platform = AgentPlatformEngine()
