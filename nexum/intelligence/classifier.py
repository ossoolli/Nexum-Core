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
        'انشئ ملف', 'انشيء ملف', 'اكتب ملف', 'احذف ملف', 'شغل', 'نفذ',
        'execute', 'run', 'mkdir', 'touch', 'rm', 'cat', 'ls',
        'pip', 'npm', 'python', 'node', 'bash', 'sh',
        'افتح', 'اغلق', 'اعد تشغيل', 'restart', 'reboot',
        'ثبت', 'install', 'حدث', 'update', 'اصنع', 'ابني',
        'create', 'write', 'delete', 'make', 'build',
        'فولدر', 'مجلد', 'folder', 'directory',
    ],
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
