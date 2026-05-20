import json
import logging
import re
from dataclasses import dataclass
from enum import Enum
# ملاحظة: سنستخدم الخدمة الحالية مؤقتاً حتى يتم النقل الكامل
from services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

class Intent(str, Enum):
    BROADCAST = "broadcast"
    MONITOR   = "monitor"
    DEPLOY    = "deploy"
    EXECUTE   = "execute"
    CHAT      = "chat"

@dataclass
class ClassificationResult:
    intent: Intent
    confidence: float
    reasoning: str

_SYSTEM = """
أنت مصنّف نوايا لنظام NEXUM OS.
مهمتك: تحليل رسالة المستخدم وتحديد نيته الأساسية.

أجب بـ JSON فقط بهذا الشكل بالضبط (بلا أي نص خارجه):
{
  "intent": "broadcast|monitor|deploy|execute|chat",
  "confidence": 0.0-1.0,
  "reasoning": "سبب مختصر بجملة واحدة"
}

تعريف كل نية:
- broadcast: المستخدم يريد إرسال شيء للقناة
- monitor: يريد معرفة حالة السيرفر أو الموارد
- deploy: يريد رفع كود أو نشر تحديث
- execute: يريد تنفيذ مهمة معقدة (إنشاء، بناء، بحث، برمجة)
- chat: محادثة عادية أو سؤال
"""

class GeminiClassifier:
    def classify(self, text: str) -> ClassificationResult:
        try:
            # استخدام gemini_service الحالية
            response, _ = gemini_service.ask(
                prompt=f"الرسالة: {text}",
                system_instruction=_SYSTEM
            )
            
            # استخراج JSON من الرد
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found")
                
            data = json.loads(json_match.group(0))
            return ClassificationResult(
                intent=Intent(data["intent"]),
                confidence=float(data["confidence"]),
                reasoning=data.get("reasoning", ""),
            )
        except Exception as e:
            logger.warning(f"Classifier failed, falling back to CHAT: {e}")
            return ClassificationResult(
                intent=Intent.CHAT,
                confidence=0.5,
                reasoning="classification failed",
            )

classifier = GeminiClassifier()
