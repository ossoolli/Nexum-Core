# -*- coding: utf-8 -*-
# agents/self_evolver.py
"""
🧬 SelfEvolverAgent — وكيل التطور الذاتي المتكامل مع مجلس الحكماء (v1.0.0)
========================================================================
- تصفية السجلات ومراقبة الأخطاء وملفات الوكلاء المولدين.
- تحضير المهام وترقية الأكواد وعرضها على مجلس الحكماء للموافقة الجماعية.
- كتابة الأكواد المصححة وترقيتها حياً عند الحصول على التوكن المعتمد (ConsensusToken).
"""

import os
import sys
import logging
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from council.consensus_engine import council_consensus

logger = logging.getLogger(__name__)

class SelfEvolverAgent:
    def __init__(self):
        pass

    async def evolve_from_error(self, error_log: str, file_path: str) -> dict:
        """ترقية وترميم كود ملف معيب بعد تمريره ومناقشته في مجلس الحكماء"""
        logger.info(f"🧬 [Evolver] Proposing evolution for file: {file_path}...")
        
        if not os.path.exists(file_path):
            return {"status": "rejected", "error": f"Target file not found: {file_path}"}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                current_code = f.read()
        except Exception as e:
            return {"status": "rejected", "error": f"Failed to read file: {e}"}

        # صياغة موجه المحاكمة لمجلس الحكماء
        task_prompt = (
            f"Bugs or crashes detected in the following agent file. Perform a code patch.\n"
            f"Traceback Error:\n{error_log}\n\n"
            f"You must deliver the complete, corrected, and highly optimized Python code for this agent. "
            f"Ensure all base dependencies are preserved and subclassing is correct. "
            f"Do not return explanations, markdown code blocks, or comments outside Python syntax. "
            f"State APPROVED if your patched code is perfect and ready to overwrite the current file, or REJECTED otherwise."
        )

        # Deliberation across Claude, GPT-4o, and Gemini in parallel!
        token = await council_consensus.deliberate(task_prompt, code=current_code)

        if token.approved:
            logger.info(f"🏆 [Evolver] Council Sages APPROVED the patch! (Grade: {token.consensus_grade})")
            
            # تنظيف الكود المدمج من المخرجات
            patched_code = token.merged_output.strip()
            # إزالة علامات الاقتباس الفولاذية ```python أو ``` إذا وُجدت
            import re
            patched_code = re.sub(r'^```(?:python)?\s*', '', patched_code)
            patched_code = re.sub(r'\s*```$', '', patched_code)
            patched_code = patched_code.strip()

            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(patched_code)
                logger.info(f"🛡️ [Evolver] Overwrote file {file_path} with council approved patched code.")
                return {
                    "status": "evolved",
                    "file": file_path,
                    "consensus_grade": token.consensus_grade,
                    "votes": token.votes
                }
            except Exception as e:
                logger.error(f"[Evolver] Failed to overwrite file with patch: {e}")
                return {"status": "failed_write", "error": str(e), "votes": token.votes}
        else:
            logger.warning(f"❌ [Evolver] Council Sages REJECTED the patch proposal. (Grade: {token.consensus_grade})")
            return {
                "status": "rejected",
                "votes": token.votes,
                "reasoning": token.reasoning
            }

# Singleton
self_evolver = SelfEvolverAgent()
