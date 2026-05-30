import sys
import os
# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import logging
from services.gemini_service import gemini_service

logger = logging.getLogger(__name__)
SUMMARY_THRESHOLD = 20  # لخّص كل 20 رسالة

class MemorySummarizer:
    """
    عندما يتجاوز السياق حداً معيناً،
    يطلب من Gemini تلخيص آخر N رسالة في 3 جمل.
    """
    def should_summarize(self, messages: list) -> bool:
        return len(messages) >= SUMMARY_THRESHOLD

    def summarize(self, messages: list) -> str:
        history = "\n".join(
            f"{m['role']}: {m.get('parts', [{'text': ''}])[0].get('text', '')}" for m in messages
        )
        prompt = (
            f"لخّص هذه المحادثة باللغة العربية في 3 جمل مختصرة تحافظ على "
            f"أهم المعلومات والقرارات:\n\n{history}"
        )
        try:
            summary, _ = gemini_service.ask(prompt)
            logger.debug(f"Memory summarized: {len(messages)} msgs → 3 sentences")
            return f"[ملخص سياق سابق]: {summary}"
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return "فشل تلخيص السياق السابق."

summarizer = MemorySummarizer()
