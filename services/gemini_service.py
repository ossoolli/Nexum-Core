# -*- coding: utf-8 -*-
"""
services/gemini_service.py
خدمة Gemini الموحدة -- Nexum Pro (v7.2.5)
==========================================
- دعم مزدوج: API Key (تطوير) + ADC/Vertex AI Agent Platform (إنتاج)
- توليد نصوص + فهم صور + توليد صور + تنفيذ أكواد
- إدارة التاريخ والسياق مع حماية ضد التضخم
- HttpOptions(api_version="v1") لـ Agent Platform
"""

import os
import re
import logging
from typing import Optional, List, Tuple, Any

from google import genai
from google.genai import types
from google.genai.types import HttpOptions

_logger = logging.getLogger("nexum.gemini")


class GeminiService:
    """
    خدمة Gemini الموحدة مع دعم Agent Platform (Vertex AI).
    
    أوضاع المصادقة:
    1. API Key: للتطوير والاختبار السريع
    2. ADC (Application Default Credentials): للإنتاج عبر Agent Platform
    
    يتم تحديد الوضع تلقائيا من الإعدادات أو متغيرات البيئة.
    """

    def __init__(self, api_key: str = None, model: str = None,
                 image_model: str = None, use_vertex: bool = None,
                 project: str = None, location: str = None):
        
        # ─── تحميل الإعدادات من Config أو البيئة ───
        _config = None
        try:
            from nexum.config import config as _cfg
            _config = _cfg
        except ImportError:
            pass

        # مفتاح API - نفضل دائماً مفتاح Agent Platform للاستفادة القصوى من الرصيد المجاني
        agent_platform_key = ""
        if _config:
            agent_platform_key = getattr(_config, "agent_platform_api_key", "")
        if not agent_platform_key:
            agent_platform_key = os.getenv("AGENT_PLATFORM_API_KEY", "")

        raw_key = api_key
        # إذا تم تمرير مفتاح عادي أو كان فارغاً ولدينا مفتاح المنصة، نستخدم مفتاح المنصة
        if agent_platform_key and (not raw_key or raw_key == os.getenv("GOOGLE_API_KEY", "")):
            raw_key = agent_platform_key
        else:
            if not raw_key and _config:
                raw_key = _config.google_api_key
            if not raw_key:
                raw_key = os.getenv("GOOGLE_API_KEY", "")
        self.api_key = raw_key.strip() if raw_key else ""

        # وضع Agent Platform (Vertex AI / ADC)
        if use_vertex is not None:
            self.use_vertex = use_vertex
        elif _config and hasattr(_config, 'google_genai_use_vertexai'):
            self.use_vertex = _config.google_genai_use_vertexai
        else:
            self.use_vertex = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true"

        # مشروع GCP والموقع
        self.project = project or (
            _config.google_cloud_project if _config and hasattr(_config, 'google_cloud_project') else ""
        ) or os.getenv("GOOGLE_CLOUD_PROJECT", "")
        self.location = location or (
            _config.google_cloud_location if _config and hasattr(_config, 'google_cloud_location') else "global"
        ) or os.getenv("GOOGLE_CLOUD_LOCATION", "global")

        # النماذج
        self.model = model or (
            _config.gemini_model if _config and hasattr(_config, 'gemini_model') else None
        ) or os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

        self.image_model = image_model or (
            _config.gemini_image_model if _config and hasattr(_config, 'gemini_image_model') else None
        ) or os.getenv("GEMINI_IMAGE_MODEL", "gemini-3.5-flash")

        # ─── إنشاء العميل ───
        self.client = self._create_client()
        self._auth_mode = "ADC/AgentPlatform" if self.use_vertex else (
            "API_Key" if self.api_key else "None"
        )

        if self.client:
            _logger.info(
                f"GeminiService initialized: mode={self._auth_mode}, "
                f"model={self.model}"
            )
        else:
            _logger.warning("GeminiService: No client created (no credentials).")

    def _create_client(self) -> Optional[genai.Client]:
        """إنشاء العميل بناء على وضع المصادقة."""
        try:
            if self.use_vertex:
                # وضع Agent Platform — ADC + HttpOptions v1
                # يجب تعيين متغيرات البيئة للمشروع
                os.environ.setdefault("GOOGLE_CLOUD_PROJECT", self.project)
                os.environ.setdefault("GOOGLE_CLOUD_LOCATION", self.location)
                os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

                return genai.Client(
                    http_options=HttpOptions(api_version="v1")
                )

            elif self.api_key:
                # وضع API Key التقليدي
                return genai.Client(api_key=self.api_key)

            return None
        except Exception as e:
            _logger.error(f"Failed to create Gemini client: {e}")
            return None

    # ═══════════════════════════════════════════════════════
    # ║  1. توليد النصوص (Text Generation)                  ║
    # ═══════════════════════════════════════════════════════

    def ask(self, prompt: str, history: list = None,
            system_instruction: str = None,
            file_data: bytes = None, mime_type: str = None,
            model: str = None) -> Tuple[str, list]:
        """
        توليد نص مع دعم السياق والوسائط.
        
        Returns:
            Tuple[str, list]: (النص المولد, التاريخ المحدث)
        """
        if not self.client:
            return "Error: No Gemini client available (check API key or ADC).", history or []

        effective_model = model or self.model
        contents = []

        # تجميع الرسائل السابقة كسياق
        if history:
            for item in history:
                if 'role' in item and 'parts' in item:
                    role_str = item['role']
                    parts_contents = [
                        p['text'] for p in item['parts'] if 'text' in p
                    ]
                    if parts_contents:
                        contents.append(
                            types.Content(
                                role=role_str,
                                parts=[
                                    types.Part.from_text(text=t)
                                    for t in parts_contents
                                ]
                            )
                        )

        # تجهيز الرسالة الحالية مع الملف إذا وجد
        current_parts = []
        if file_data and mime_type:
            try:
                current_parts.append(
                    types.Part.from_bytes(data=file_data, mime_type=mime_type)
                )
            except Exception as e:
                _logger.warning(f"Error attaching file: {e}")

        current_parts.append(
            types.Part.from_text(text=prompt or "Analyze the provided input.")
        )
        contents.append(types.Content(role='user', parts=current_parts))

        # تجهيز إعدادات التوليد
        config_args = {}
        if system_instruction:
            config_args["system_instruction"] = system_instruction
        gen_config = types.GenerateContentConfig(**config_args)

        try:
            response = self.client.models.generate_content(
                model=effective_model,
                contents=contents,
                config=gen_config
            )

            if response.text:
                new_history = history.copy() if history else []
                new_history.append({'role': 'user', 'parts': [{'text': prompt}]})
                new_history.append({'role': 'model', 'parts': [{'text': response.text}]})
                return response.text, new_history

            return "Error: Empty response from model.", history or []

        except Exception as e:
            _logger.error(f"generate_content failed: {e}")
            return f"Error: {str(e)}", history or []

    # ═══════════════════════════════════════════════════════
    # ║  2. توليد الصور (Image Generation)                  ║
    # ═══════════════════════════════════════════════════════

    def generate_image(self, prompt: str, output_path: str = None,
                       model: str = None) -> dict:
        """
        توليد صورة عبر Gemini مع responseModalities=[TEXT, IMAGE].
        
        Args:
            prompt: وصف الصورة المطلوبة
            output_path: مسار حفظ الصورة (اختياري)
            model: نموذج التوليد (افتراضي: image_model)
            
        Returns:
            dict: {"success": bool, "text": str, "image_data": bytes, "path": str}
        """
        if not self.client:
            return {"success": False, "error": "No client available."}

        effective_model = model or self.image_model

        try:
            from google.genai.types import GenerateContentConfig, Modality

            response = self.client.models.generate_content(
                model=effective_model,
                contents=prompt,
                config=GenerateContentConfig(
                    response_modalities=[Modality.TEXT, Modality.IMAGE],
                ),
            )

            result = {"success": True, "text": "", "image_data": None, "path": None}

            for part in response.candidates[0].content.parts:
                if part.text:
                    result["text"] = part.text
                elif part.inline_data:
                    result["image_data"] = part.inline_data.data

                    # حفظ الصورة إذا تم تحديد مسار
                    if output_path:
                        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
                        with open(output_path, "wb") as f:
                            f.write(part.inline_data.data)
                        result["path"] = output_path

            return result

        except Exception as e:
            _logger.error(f"Image generation failed: {e}")
            return {"success": False, "error": str(e)}

    # ═══════════════════════════════════════════════════════
    # ║  3. فهم الصور (Image Understanding)                 ║
    # ═══════════════════════════════════════════════════════

    def understand_image(self, prompt: str, image_data: bytes = None,
                         mime_type: str = "image/jpeg",
                         image_uri: str = None,
                         model: str = None) -> Tuple[str, list]:
        """
        تحليل وفهم صورة مع سؤال نصي.
        
        Args:
            prompt: السؤال عن الصورة
            image_data: بيانات الصورة كـ bytes
            mime_type: نوع الملف
            image_uri: رابط GCS (gs://...)
            
        Returns:
            Tuple[str, list]: (الوصف, [])
        """
        if not self.client:
            return "Error: No client available.", []

        effective_model = model or self.model
        content_parts = [prompt]

        if image_data:
            content_parts.append(
                types.Part.from_bytes(data=image_data, mime_type=mime_type)
            )
        elif image_uri:
            content_parts.append(
                types.Part.from_uri(file_uri=image_uri, mime_type=mime_type)
            )

        try:
            response = self.client.models.generate_content(
                model=effective_model,
                contents=content_parts,
            )
            return response.text or "No description generated.", []
        except Exception as e:
            _logger.error(f"Image understanding failed: {e}")
            return f"Error: {str(e)}", []

    # ═══════════════════════════════════════════════════════
    # ║  4. تنفيذ الأكواد (Code Execution)                  ║
    # ═══════════════════════════════════════════════════════

    def execute_code(self, prompt: str, model: str = None) -> dict:
        """
        استخدام أداة تنفيذ الأكواد المدمجة في Gemini.
        
        Args:
            prompt: وصف المهمة البرمجية
            
        Returns:
            dict: {"success": bool, "code": str, "result": str, "text": str}
        """
        if not self.client:
            return {"success": False, "error": "No client available."}

        effective_model = model or self.model

        try:
            from google.genai.types import (
                Tool, ToolCodeExecution, GenerateContentConfig
            )

            code_execution_tool = Tool(code_execution=ToolCodeExecution())
            response = self.client.models.generate_content(
                model=effective_model,
                contents=prompt,
                config=GenerateContentConfig(
                    tools=[code_execution_tool],
                    temperature=0,
                ),
            )

            result = {
                "success": True,
                "text": response.text or "",
                "code": "",
                "result": ""
            }

            # استخراج الكود والنتيجة
            try:
                if hasattr(response, 'executable_code') and response.executable_code:
                    result["code"] = response.executable_code
                if hasattr(response, 'code_execution_result') and response.code_execution_result:
                    result["result"] = response.code_execution_result
            except Exception:
                pass

            return result

        except Exception as e:
            _logger.error(f"Code execution failed: {e}")
            return {"success": False, "error": str(e)}

    # ═══════════════════════════════════════════════════════
    # ║  5. أدوات مساعدة                                    ║
    # ═══════════════════════════════════════════════════════

    def get_status(self) -> dict:
        """تقرير حالة الخدمة."""
        return {
            "auth_mode": self._auth_mode,
            "connected": self.client is not None,
            "model": self.model,
            "image_model": self.image_model,
            "use_vertex": self.use_vertex,
            "project": self.project if self.use_vertex else "N/A",
            "location": self.location if self.use_vertex else "N/A"
        }

    def switch_model(self, model: str) -> None:
        """تبديل النموذج الافتراضي."""
        self.model = model
        _logger.info(f"Model switched to: {model}")

    def list_available_models(self) -> list:
        """النماذج المتاحة على Agent Platform."""
        return [
            "gemini-3.5-flash",
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
        ]


# ═══════════════════════════════════════════════════════
# ║  Singleton                                          ║
# ═══════════════════════════════════════════════════════

gemini_service = GeminiService()
