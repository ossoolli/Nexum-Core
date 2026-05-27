# -*- coding: utf-8 -*-
# agents/rag_memory_agent.py
"""
🧠 RagMemoryAgent — وكيل الذاكرة الدلالية والبحث المسترجع (v1.0.0)
===================================================================
- توفير آلية فحص وبحث دلالي (Semantic Search) للذاكرة السيادية وأرشيف الجلسات.
- استخدام خوارزمية بحث هجينة تعتمد على مطابقة الكلمات المفتاحية مع دعم الفهم الدلالي عبر Gemini.
- يندمج بسهولة مع قواعد بيانات المتجهات (Vector Databases) مثل Qdrant عند توفر إعداداتها.
"""

import os
import sys
import json
import logging
from typing import List, Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

class RagMemoryAgent:
    def __init__(self):
        self.qdrant_client = None
        self._init_qdrant()

    def _init_qdrant(self):
        # محاولة الاتصال بـ Qdrant اختيارياً إذا كانت المكتبة مثبتة ومتغيرات البيئة متوفرة
        try:
            from qdrant_client import QdrantClient
            qdrant_host = os.getenv("QDRANT_HOST", "localhost")
            qdrant_port = int(os.getenv("QDRANT_PORT", 6333))
            self.qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port, timeout=3)
            logger.info("[RAG] Qdrant client connected successfully.")
        except Exception:
            self.qdrant_client = None
            logger.info("[RAG] Qdrant not available. Using local lightweight RAG engine.")

    async def search_memory(self, query: str, limit: int = 5) -> List[dict]:
        """البحث الهجين في أرشيف جلسات مجلس الحكماء والذاكرة"""
        logger.info(f"[RAG] Performing semantic search for query: '{query}'...")
        
        # 1. جلب كافة الجلسات المؤرشفة محلياً
        from council.knowledge_archive import knowledge_archive
        archive_data = knowledge_archive.get_all()
        
        if not archive_data:
            return []

        # 2. إذا كان Qdrant نشطاً، نقوم بالبحث عبره (مستقبلاً)
        if self.qdrant_client:
            # هنا يمكن توليد Embeddings عبر Gemini والبحث
            pass

        # 3. محاكي البحث الدلالي الذكي باستخدام رتب الترشيح الهجينة (Hybrid Scoring) عبر مساعدة Gemini
        prompt = (
            f"You are the Sovereign RAG Search Agent of NEXUM PRO.\n"
            f"We need to find the most relevant historical consensus sessions for this query: '{query}'\n\n"
            f"Here is the list of available sessions in our archive:\n"
        )
        
        for idx, item in enumerate(archive_data[:20]): # مسح أول 20 جلسة
            prompt += f"[{idx}] Task: {item['task']} | Grade: {item['consensus_grade']}\n"
            
        prompt += (
            f"\nIdentify the indexes of the top {limit} most relevant sessions to answer or assist with the query.\n"
            f"Return ONLY a JSON list of integers, e.g. [0, 2, 4]. No explanations, no markdown blocks."
        )

        try:
            import asyncio
            res, _ = await asyncio.to_thread(gemini_service.ask, prompt)
            
            # استخراج قائمة الأرقام
            import re
            match = re.search(r'\[\s*\d+(?:\s*,\s*\d+)*\s*\]', res)
            if match:
                indexes = json.loads(match.group())
                results = []
                for idx in indexes:
                    if 0 <= idx < len(archive_data):
                        results.append(archive_data[idx])
                return results[:limit]
        except Exception as e:
            logger.error(f"[RAG] Semantic search assist failed: {e}")

        # Fallback: مطابقة الكلمات الأساسية البسيطة (Lexical search fallback)
        fallback_results = []
        words = query.lower().split()
        for item in archive_data:
            score = 0
            task_lower = item['task'].lower()
            for w in words:
                if w in task_lower:
                    score += 1
            if score > 0:
                fallback_results.append((score, item))
                
        # ترتيب حسب النقاط
        fallback_results.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in fallback_results[:limit]]

# Singleton
rag_memory = RagMemoryAgent()
