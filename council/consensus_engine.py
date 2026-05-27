# -*- coding: utf-8 -*-
# council/consensus_engine.py
"""
🔱 CouncilConsensusEngine — المحرك المركزي لمجلس الحكماء (v1.0.0)
================================================================
- تشغيل Claude 3.5 و Gemini 3.5 و GPT-4o بالتوازي لتقييم المهام الحساسة.
- حل وتمرير الاستدعاءات بالتزامن عبر asyncio.to_thread لعدم تجميد خادم التطبيق.
- التكامل الفوري مع بروتوكول النقاش (Debate Protocol) لتصفية الخلافات.
"""

import os
import sys
import json
import asyncio
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from core.llm_engine import llm_engine, openai_engine
from services.gemini_service import gemini_service
from council.debate_protocol import CouncilDebateProtocol
from council.knowledge_archive import knowledge_archive

logger = logging.getLogger(__name__)

@dataclass
class ConsensusToken:
    approved: bool
    votes: dict          # {"claude": bool, "gemini": bool, "gpt": bool}
    reasoning: dict      # {"claude": str, "gemini": str, "gpt": str}
    consensus_grade: str # "AAA Unanimous" | "A Consensus" | "F Failed"
    merged_output: str
    timestamp: str

class CouncilConsensusEngine:
    def __init__(self):
        self.debate_protocol = CouncilDebateProtocol(self)

    async def deliberate(self, task: str, code: str = None) -> ConsensusToken:
        """عقد جلسة حكماء لمناقشة وإصدار قرار إجماع نهائي"""
        logger.info(f"[Council] Starting deliberation session on task: {task[:60]}...")
        
        prompt = (
            f"You are a member of the sovereign Council of Sages of NEXUM PRO.\n"
            f"Evaluate the proposed task. You must explicitly start your response with 'APPROVED' or 'REJECTED'.\n"
            f"Provide a clear, technical reason for your vote.\n\n"
            f"Proposed Task: {task}\n"
        )
        if code:
            prompt += f"\nCode Context:\n```python\n{code}\n```\n"

        # تشغيل النماذج الثلاثة بالتوازي عبر خيوط معالجة آمنة
        try:
            results = await asyncio.gather(
                self._ask_claude(prompt),
                self._ask_gemini(prompt),
                self._ask_gpt(prompt),
                return_exceptions=True
            )
        except Exception as e:
            logger.error(f"[Council] Parallel deliberation failed: {e}")
            return self._create_failed_token(str(e))

        # معالجة النتائج وتصفية الأخطاء
        claude_res = results[0] if not isinstance(results[0], Exception) else f"REJECTED: Error: {results[0]}"
        gemini_res = results[1] if not isinstance(results[1], Exception) else f"REJECTED: Error: {results[1]}"
        gpt_res    = results[2] if not isinstance(results[2], Exception) else f"REJECTED: Error: {results[2]}"

        votes = {
            "claude": self._extract_vote(claude_res),
            "gemini": self._extract_vote(gemini_res),
            "gpt":    self._extract_vote(gpt_res)
        }
        
        reasoning = {
            "claude": str(claude_res),
            "gemini": str(gemini_res),
            "gpt":    str(gpt_res)
        }

        # ─── تحقق الإجماع الكلي (3/3) ───
        if all(votes.values()):
            merged = await self._merge_deliberation(task, reasoning)
            token = ConsensusToken(
                approved=True,
                votes=votes,
                reasoning=reasoning,
                consensus_grade="AAA Unanimous",
                merged_output=merged,
                timestamp=datetime.now().isoformat()
            )
            # أرشفة القرار الناجح
            knowledge_archive.archive(task, token)
            return token

        # ─── تحقق توافق الأغلبية (2/3) — إطلاق بروتوكول النقاش ───
        approve_count = sum(1 for v in votes.values() if v)
        if approve_count >= 2:
            logger.info("[Council] Disagreement detected (2 APPROVED, 1 REJECTED). Launching Debate Protocol...")
            debate_token = await self.debate_protocol.debate(task, reasoning, votes)
            if debate_token.approved:
                knowledge_archive.archive(task, debate_token)
            return debate_token

        # ─── الرفض التام (أقل من صوتين موافقة) ───
        logger.warning("[Council] Task rejected by majority of sages.")
        return ConsensusToken(
            approved=False,
            votes=votes,
            reasoning=reasoning,
            consensus_grade="F Failed",
            merged_output="",
            timestamp=datetime.now().isoformat()
        )

    async def _ask_claude(self, prompt: str) -> str:
        """استدعاء كلود أوبوس 4.6 عبر OpenRouter"""
        res, _ = await asyncio.to_thread(llm_engine.ask, prompt, "anthropic/claude-opus-4.6")
        return res

    async def _ask_gpt(self, prompt: str) -> str:
        """استدعاء جي بي تي 5.4 نانو عبر OpenAI مباشرة"""
        res, _ = await asyncio.to_thread(openai_engine.ask, prompt, "gpt-5.4-nano")
        return res

    async def _ask_gemini(self, prompt: str) -> str:
        """استدعاء جيميني 3.5 فلاش محلياً/سحابياً"""
        # دمج سياق جيميني عبر ask العادية
        res, _ = await asyncio.to_thread(gemini_service.ask, prompt, model="gemini-3.5-flash")
        return res

    def _extract_vote(self, response: str) -> bool:
        """استخراج قرار التصويت بناء على بدء الرد"""
        clean = str(response).strip().upper()
        if "APPROVED" in clean[:150]:
            return True
        return False

    async def _merge_deliberation(self, task: str, reasoning: dict) -> str:
        """تخليق المخرج المدمج النهائي بناء على إجماع الحكماء"""
        merge_prompt = (
            f"You are the Sovereign Consensus Merging Engine of NEXUM PRO.\n"
            f"The Council of Sages has unanimously approved the following task: {task}\n\n"
            f"Here is the reasoning of Claude:\n{reasoning['claude']}\n\n"
            f"Here is the reasoning of Gemini:\n{reasoning['gemini']}\n\n"
            f"Here is the reasoning of GPT-5.4-nano:\n{reasoning['gpt']}\n\n"
            f"Merge the recommendations and generate the optimal implementation code or text output. "
            f"If it is code, output ONLY raw clean executable code without markdown block wrappers."
        )
        res, _ = await asyncio.to_thread(gemini_service.ask, merge_prompt)
        return res.strip()

    def _create_failed_token(self, error: str) -> ConsensusToken:
        return ConsensusToken(
            approved=False,
            votes={"claude": False, "gemini": False, "gpt": False},
            reasoning={"error": error},
            consensus_grade="F Failed",
            merged_output="",
            timestamp=datetime.now().isoformat()
        )

# Singleton
council_consensus = CouncilConsensusEngine()
