import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class Intent(str, Enum):
    BROADCAST = "broadcast"
    MONITOR   = "monitor"
    DEPLOY    = "deploy"
    EXECUTE   = "execute"
    CHAT      = "chat"
    
    # ─── Google Cloud Intents ───
    CLOUD_STORAGE   = "cloud_storage"    # "ارفع ملف لـ Storage"
    CLOUD_BIGQUERY  = "cloud_bigquery"   # "اعمل query على BigQuery"
    CLOUD_COMPUTE   = "cloud_compute"    # "شغل VM" / "أوقف VM"
    CLOUD_MONITOR   = "cloud_monitor"    # "حالة السيرفرات" / "logs"
    CLOUD_AI        = "cloud_ai"         # "شغل Vertex AI model"
    CLOUD_GENERAL   = "cloud_general"    # أي أمر cloud عام

@dataclass
class ClassificationResult:
    intent: Intent
    confidence: float
    reasoning: str

# تصنيف محلي سريع بدون استهلاك API — أسرع وأذكى
_KEYWORD_MAP = {
    Intent.MONITOR: [
        'حالة', 'status', 'النبض', 'pulse', 'cpu', 'ram', 'disk',
        'موارد', 'سيرفر', 'server', 'health', 'نظام', 'مراقبة'
    ],
    Intent.DEPLOY: [
        'ارفع', 'انشر', 'deploy', 'push', 'sync', 'git', 'نشر',
        'مزامنة', 'رفع', 'تحديث الكود'
    ],
    Intent.BROADCAST: [
        'بث', 'broadcast', 'ارسل للقناة', 'انشر للكل', 'قنواتي'
    ],
    Intent.EXECUTE: [
        'فولدر', 'مجلد', 'folder', 'directory',
    ],
    Intent.CLOUD_STORAGE:  ["storage", "باكت", "bucket", "ارفع ملف", "حمّل ملف", "gcs"],
    Intent.CLOUD_BIGQUERY: ["bigquery", "query", "جدول", "dataset", "sql", "استعلام"],
    Intent.CLOUD_COMPUTE:  ["vm", "instance", "سيرفر", "شغل جهاز", "أوقف جهاز", "compute"],
    Intent.CLOUD_MONITOR:  ["logs", "سجلات", "monitoring", "تنبيه", "alert", "أداء"],
    Intent.CLOUD_AI:       ["vertex", "model", "تدريب", "vertex ai", "aiplatform"],
}

class LocalClassifier:
    """مصنف محلي فوري — مع حماية من تداخل الكلمات"""
    def classify(self, text: str) -> ClassificationResult:
        import re
        lower = text.lower().strip()

        # أوامر Shell المباشرة
        if lower.startswith('!'):
            return ClassificationResult(Intent.EXECUTE, 1.0, "shell prefix")

        # بحث بالكلمات المفتاحية (تطابق الكلمات الكاملة)
        for intent, keywords in _KEYWORD_MAP.items():
            for kw in keywords:
                # نمط بسيط وفعال لاكتشاف الكلمة ككتلة واحدة
                pattern = rf'(?:\s|^){re.escape(kw)}(?:\s|$)'
                if re.search(pattern, lower):
                    return ClassificationResult(intent, 0.9, f"keyword: {kw}")

        # الافتراضي
        return ClassificationResult(Intent.CHAT, 0.7, "default chat")

classifier = LocalClassifier()
