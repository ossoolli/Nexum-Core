# -*- coding: utf-8 -*-
# council/consensus_engine.py
"""
🔱 CouncilConsensusEngine — المحرك المركزي لمجلس الحكماء (v1.0.0)
================================================================
- تشغيل Claude Sonnet 4 و Gemini 3.5 Flash و GPT-4o بالتوازي لتقييم المهام الحساسة.
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
from services.grok_service import grok_service
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
            "502",
            "404",
            "NOT_FOUND",
            "not found",
            "خطأ في Agent Platform",
            "Exception",
            "exception",
            "failed to"
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
            return f"REJECTED: Fallback alternate failed: {e}"

    async def _ask_sage_by_id(self, sage_id: str, prompt: str) -> str:
        """
        تستعلم عن حكيم نشط بشكل ديناميكي بناءً على معرّفه الفريد.
        Queries an active sage dynamically by its ID.
        """
        config = self._load_consensus_config()
        active_models = config.get("active_models", [])
        sage_config = None
        for m in active_models:
            if m.get("id") == sage_id:
                sage_config = m
                break
                
        if not sage_config:
            sage_config = {"id": sage_id, "model_name": sage_id}
            
        return await self._ask_sage(sage_config, prompt)

    async def _ask_sage(self, sage_config: dict, prompt: str) -> str:
        """
        تستعلم عن نموذج عبر Agent Platform كخيار أساسي، مع التحويل للاحتياطي عند حدوث فشل.
        Queries a sage dynamically via AgentPlatform or its designated direct fallback.
        """
        sage_id = sage_config.get("id", "")
        model_name = sage_config.get("model_name", "")
        
        # 1. الاستعلام عبر Agent Platform (الخيار الرئيسي الموحد)
        if agent_platform.is_available:
            logger.info(f"[Council] Attempting {sage_id.upper()} ({model_name}) via Agent Platform...")
            res, _ = await asyncio.to_thread(agent_platform.ask, prompt, model_name)
            if not self._is_api_error(res):
                return res
            logger.warning(f"[Council] Agent Platform failed for {sage_id.upper()} ({model_name}). Trying fallback...")

        # 2. الاستعلام عبر قنوات الصمود والاحتياط الفردية (Direct Fallbacks)
        try:
            if sage_id == "claude":
                res, _ = await asyncio.to_thread(llm_engine.ask, prompt, model_name)
                return res
            elif sage_id == "gpt":
                res, _ = await asyncio.to_thread(openai_engine.ask, prompt, model_name)
                return res
            elif sage_id == "gemini":
                res, _ = await asyncio.to_thread(gemini_service.ask, prompt, model=model_name)
                return res
            elif sage_id == "grok":
                if grok_service.is_available:
                    res, _ = await asyncio.to_thread(grok_service.ask, prompt, model=model_name)
                    return res
                else:
                    return await self._ask_fallback(prompt, "grok")
            else:
                # أي نموذج مخصص إضافي يوجه للاحتياطي السحابي العام
                return await self._ask_fallback(prompt, sage_id)
        except Exception as e:
            logger.error(f"[Council] Fallback connection failed for {sage_id.upper()}: {e}")
            return f"REJECTED: Fallback failed: {e}"

    async def deliberate(self, task: str, code: str = None) -> ConsensusToken:
        """عقد جلسة حكماء لمناقشة وإصدار قرار إجماع نهائي"""
        logger.info(f"[Council] Starting dynamic deliberation session on task: {task[:60]}...")
        
        prompt = (
            f"You are a member of the sovereign Council of Sages of NEXUM PRO.\n"
            f"Evaluate the proposed task. You must explicitly start your response with 'APPROVED' or 'REJECTED'.\n"
            f"Provide a clear, technical reason for your vote.\n\n"
            f"Proposed Task: {task}\n"
        )
        if code:
            prompt += f"\nCode Context:\n```python\n{code}\n```\n"

        # شحن الإعدادات وقراءة النماذج النشطة ديناميكياً
        config = self._load_consensus_config()
        active_models = config.get("active_models", [])
        if not active_models:
            # Fallback to standard core sages
            active_models = [
                {"id": "claude", "model_name": "anthropic/claude-sonnet-4"},
                {"id": "gpt", "model_name": "gpt-4o-mini"},
                {"id": "gemini", "model_name": "gemini-3.5-flash"}
            ]

        # تشغيل جميع النماذج النشطة بالتوازي عبر خيوط معالجة آمنة
        tasks = []
        for model_info in active_models:
            tasks.append(self._ask_sage(model_info, prompt))

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"[Council] Parallel deliberation failed: {e}")
            return self._create_failed_token(str(e))

        # معالجة أصوات ومبررات الحكماء ديناميكياً
        votes = {}
        reasoning = {}
        
        for idx, model_info in enumerate(active_models):
            sage_id = model_info["id"]
            res = results[idx]
            if isinstance(res, Exception):
                res_str = f"REJECTED: Call Error: {str(res)}"
            else:
                res_str = str(res)
                
            votes[sage_id] = self._extract_vote(res_str)
            reasoning[sage_id] = res_str

        # تطبيق الصمود والاحتياط (Resiliency Fallback) عند فشل API الأعضاء الأساسيين
        enable_fallback = config.get("consensus_rules", {}).get("enable_fallback_on_api_error", True)
        if enable_fallback:
            fallback_tasks = []
            fallback_indices = []
            
            for idx, model_info in enumerate(active_models):
                sage_id = model_info["id"]
                if self._is_api_error(reasoning[sage_id]):
                    logger.warning(f"[Council] Sage {sage_id.upper()} endpoint failed. Invoking alternate...")
                    fallback_tasks.append(self._ask_fallback(prompt, sage_id))
                    fallback_indices.append(idx)
                    
            if fallback_tasks:
                fallback_results = await asyncio.gather(*fallback_tasks, return_exceptions=True)
                for f_idx, idx in enumerate(fallback_indices):
                    sage_id = active_models[idx]["id"]
                    res = fallback_results[f_idx]
                    res_str = str(res) if not isinstance(res, Exception) else f"REJECTED: Fallback alternate failed: {str(res)}"
                    votes[sage_id] = self._extract_vote(res_str)
                    reasoning[sage_id] = res_str

        total_sages = len(votes)
        approve_count = sum(1 for v in votes.values() if v)
        approval_ratio = approve_count / total_sages if total_sages > 0 else 0.0
        
        # ─── تحقق الإجماع الكلي (Unanimous) ───
        if approve_count == total_sages:
            merged = await self._merge_deliberation(task, reasoning)
            token = ConsensusToken(
                approved=True,
                votes=votes,
                reasoning=reasoning,
                consensus_grade="AAA Unanimous",
                merged_output=merged,
                timestamp=datetime.now().isoformat()
            )
            knowledge_archive.archive(task, token)
            return token

        # ─── تحقق توافق الأغلبية (Majority) — إطلاق بروتوكول النقاش ───
        rules = config.get("consensus_rules", {})
        threshold = rules.get("general_approval_threshold", 0.66)
        
        if approval_ratio >= threshold and approve_count >= 2:
            logger.info(f"[Council] Disagreement detected ({approve_count}/{total_sages} approved). Launching Debate Protocol...")
            debate_token = await self.debate_protocol.debate(task, reasoning, votes)
            if debate_token.approved:
                knowledge_archive.archive(task, debate_token)
            return debate_token

        # ─── الرفض التام (أقل من الحد الأدنى) ───
        logger.warning(f"[Council] Task rejected by majority of sages ({approve_count}/{total_sages} approved).")
        return ConsensusToken(
            approved=False,
            votes=votes,
            reasoning=reasoning,
            consensus_grade="F Failed",
            merged_output="",
            timestamp=datetime.now().isoformat()
        )

    async def _ask_claude(self, prompt: str) -> str:
        """استدعاء كلود كحكيم نشط بشكل ديناميكي"""
        return await self._ask_sage_by_id("claude", prompt)

    async def _ask_gpt(self, prompt: str) -> str:
        """استدعاء جي بي تي كحكيم نشط بشكل ديناميكي"""
        return await self._ask_sage_by_id("gpt", prompt)

    async def _ask_gemini(self, prompt: str) -> str:
        """استدعاء جيميني كحكيم نشط بشكل ديناميكي"""
        return await self._ask_sage_by_id("gemini", prompt)

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
            f"Here is the reasoning of GPT-4o:\n{reasoning['gpt']}\n\n"
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
