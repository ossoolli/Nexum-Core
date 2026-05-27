# -*- coding: utf-8 -*-
# council/knowledge_archive.py
"""
💾 CouncilKnowledgeArchive — أرشفة وحفظ قرارات مجلس الحكماء (v1.0.0)
===================================================================
- حفظ التوافقات والقرارات التاريخية لتشكل ذاكرة تشغيلية محلية للرجوع لها (RAG).
- الحفاظ على حجم السجل في حدود 100 جلسة لمنع تضخم المساحة.
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class CouncilKnowledgeArchive:
    def __init__(self):
        self.archive_path = os.path.join(BASE_DIR, "storage", "sovereign_memory", "consensus_archive.json")
        os.makedirs(os.path.dirname(self.archive_path), exist_ok=True)

    def archive(self, task: str, token: Any) -> bool:
        """أرشفة جلسة إجماع ناجحة"""
        try:
            # تحويل التوكن لقاموس
            from dataclasses import asdict
            record = {
                "task": task,
                "timestamp": datetime.now().isoformat(),
                "approved": token.approved,
                "votes": token.votes,
                "consensus_grade": token.consensus_grade,
                "reasoning": token.reasoning,
                "merged_output": token.merged_output[:2000] # اقتطاع المخرج للذاكرة
            }

            records = self.get_all()
            records.append(record)

            # الحفاظ على آخر 100 جلسة فقط
            if len(records) > 100:
                records.pop(0)

            with open(self.archive_path, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=4, ensure_ascii=False)
            
            logger.info(f"[Archive] Consensus session archived successfully under: {self.archive_path}")
            return True
        except Exception as e:
            logger.error(f"[Archive] Failed to save consensus: {e}")
            return False

    def get_all(self) -> list:
        """جلب كامل الأرشيف التاريخي"""
        if not os.path.exists(self.archive_path):
            return []
        try:
            with open(self.archive_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"[Archive] Failed to load archive: {e}")
            return []

# Singleton
knowledge_archive = CouncilKnowledgeArchive()
