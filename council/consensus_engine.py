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
from core.agent_platform_engine import agent_platform
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

    def _load_consensus_config(self) -> dict:
        """شحن وقراءة ملف إعدادات بروتوكول التوافق والاعتراضات ديناميكياً"""
        try:
            import yaml
            path = os.path.join(BASE_DIR, "protocols", "consensus.yaml")
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"[Council] Failed to load consensus.yaml: {e}")
            return {}

    def _is_api_error(self, res: Any) -> bool:
        """تحديد ما إذا كان الرد يمثل خطأ استدعاء أو عطلاً في الرصيد/الشبكة"""
        if isinstance(res, Exception):
            return True
        res_str = str(res)
        error_indicators = [
            "خطأ في الاتصال",
            "Payment Required",
            "402",
            "Rate Limit",
            "429",
            "Unauthorized",
            "401",
            "Internal Server Error",
            "500",
            "Bad Gateway",
            "502"
        ]
        return any(ind in res_str for ind in error_indicators)

    async def _ask_fallback(self, prompt: str, target_sage: str) -> str:
        """استدعاء وكيل احتياطي سيادي (Gemini) للتصويت بالنيابة عن الموديل المتعطل برمجياً"""
        logger.info(f"[Council Fallback] Invoking Gemini alternate to deliberate as Sage {target_sage.upper()}...")
        fallback_prompt = (
            f"⚠️ [SYSTEM FALLBACK SYSTEM ACTIVE]\n"
            f"You are acting as the Sovereign Alternate for Sage {target_sage.upper()} in the NEXUM PRO Council of Sages.\n"
            f"Sage {target_sage.upper()}'s API endpoint is currently offline (Billing or Connection Issue).\n"
            f"You must evaluate the proposed task from {target_sage.upper()}'s specific perspective (e.g. strict security and logic check for Claude, or strategic/analytical layout for GPT).\n"
            f"You must explicitly start your response with 'APPROVED' or 'REJECTED' followed by your technical reasoning.\n\n"
            f"Here is the original deliberation prompt:\n{prompt}"
        )
        try:
            res, _ = await asyncio.to_thread(gemini_service.ask, fallback_prompt, model="gemini-3.5-flash")
            return f"♻️ [Fallback for {target_sage.upper()}] " + res
        except Exception as e:
            logger.error(f"[Council Fallback] Alternate resolution failed for {target_sage}: {e}")
            return f"REJECTED: Fallback alternate failed: {e}"

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

        # تطبيق الصمود التلقائي (Resiliency Fallback) عند كشف أعطال API
        config = self._load_consensus_config()
        enable_fallback = config.get("consensus_rules", {}).get("enable_fallback_on_api_error", True)

        if enable_fallback:
            if self._is_api_error(claude_res):
                logger.warning("[Council] Claude endpoint failed. Invoking alternate for Claude...")
                claude_res = await self._ask_fallback(prompt, "claude")
            
            if self._is_api_error(gpt_res):
                logger.warning("[Council] GPT endpoint failed. Invoking alternate for GPT...")
                gpt_res = await self._ask_fallback(prompt, "gpt")

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
        """استدعاء كلود أوبوس 4.6 عبر Agent Platform (أو OpenRouter كاحتياطي)"""
        if agent_platform.is_available:
            logger.info("[Council] Attempting Claude via Agent Platform (Primary)...")
            res, _ = await asyncio.to_thread(agent_platform.ask, prompt, "anthropic/claude-opus-4.6")
            if not self._is_api_error(res):
                return res
            logger.warning(f"[Council] Agent Platform Claude failed. Falling back to OpenRouter. Error: {res}")

        # الاحتياطي: OpenRouter
        res, _ = await asyncio.to_thread(llm_engine.ask, prompt, "anthropic/claude-opus-4.6")
        return res

    async def _ask_gpt(self, prompt: str) -> str:
        """استدعاء جي بي تي 5.4 نانو عبر Agent Platform (أو OpenAI كاحتياطي)"""
        if agent_platform.is_available:
            logger.info("[Council] Attempting GPT via Agent Platform (Primary)...")
            res, _ = await asyncio.to_thread(agent_platform.ask, prompt, "gpt-5.4-nano")
            if not self._is_api_error(res):
                return res
            logger.warning(f"[Council] Agent Platform GPT failed. Falling back to OpenAI. Error: {res}")

        # الاحتياطي: OpenAI
        res, _ = await asyncio.to_thread(openai_engine.ask, prompt, "gpt-5.4-nano")
        return res

    async def _ask_gemini(self, prompt: str) -> str:
        """استدعاء جيميني 3.5 فلاش عبر Agent Platform (أو GeminiService كاحتياطي)"""
        if agent_platform.is_available:
            logger.info("[Council] Attempting Gemini via Agent Platform (Primary)...")
            res, _ = await asyncio.to_thread(agent_platform.ask, prompt, "gemini-3.5-flash")
            if not self._is_api_error(res):
                return res
            logger.warning(f"[Council] Agent Platform Gemini failed. Falling back to GeminiService. Error: {res}")

        # الاحتياطي: GeminiService
        res, _ = await asyncio.to_thread(gemini_service.ask, prompt, model="gemini-3.5-flash")
        return res

    def _extract_vote(self, response: str) -> bool:
        """استخراج قرار التصويت بناء على بدء الرد"""
        clean = str(response).strip().upper()
        if "APPROVED" in clean[:300]:
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
