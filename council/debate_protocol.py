# -*- coding: utf-8 -*-
# council/debate_protocol.py
"""
📜 CouncilDebateProtocol — بروتوكول النقاش الذاتي والمحاكاة بين النماذج (v1.0.0)
=============================================================================
- تفعيل النقاش التفاعلي لتقريب وجهات النظر عند حدوث خلاف (2 موافق ضد 1 معترض).
- يمرر حجة المعترض للموافقين لتعديل أو تأكيد قرارهم، وحجة الموافقين للمعترض لإقناعه بالترميم.
- يستقر القرار في النهاية إما بالتوافق الإجماعي أو الرفض الذكي.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from core.llm_engine import llm_engine
from services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

class CouncilDebateProtocol:
    def __init__(self, consensus_engine):
        self.engine = consensus_engine

    async def debate(self, task: str, initial_reasoning: dict, initial_votes: dict) -> Any:
        """تشغيل دورة النقاش بين الحكماء"""
        logger.info("[Debate] Initiating sage deliberation exchange...")
        
        # تحديد من هو المعترض ومن الموافق
        dissenters = [k for k, v in initial_votes.items() if not v]
        supporters = [k for k, v in initial_votes.items() if v]
        
        if not dissenters:
            # لا تعارض
            return await self._compile_consensus_token(task, initial_reasoning, initial_votes, "AAA Unanimous", True)

        dissenting_agent = dissenters[0]
        dissenting_reason = initial_reasoning[dissenting_agent]

        # جولة النقاش 1: إرسال اعتراض المعترض إلى الموافقين
        logger.info(f"[Debate] Asking supporters {supporters} to review dissent from {dissenting_agent}...")
        
        reconsider_prompt = (
            f"You are a member of the sovereign Council of Sages of NEXUM PRO.\n"
            f"You previously voted APPROVED for the task: '{task}'.\n"
            f"However, Sage {dissenting_agent.upper()} has REJECTED this task with the following objection:\n"
            f"\"\"\"\n{dissenting_reason}\n\"\"\"\n\n"
            f"Please review this objection. Do you still stand by your APPROVED vote? "
            f"Respond with APPROVED if you still believe it is 100% safe, or REJECTED if you agree with the objection."
        )

        # استجواب الموافقين بالتوازي
        reconsider_tasks = []
        for sup in supporters:
            if sup == "claude":
                reconsider_tasks.append(self.engine._ask_claude(reconsider_prompt))
            elif sup == "gpt":
                reconsider_tasks.append(self.engine._ask_gpt(reconsider_prompt))
            elif sup == "gemini":
                reconsider_tasks.append(self.engine._ask_gemini(reconsider_prompt))

        sup_results = await asyncio.gather(*reconsider_tasks, return_exceptions=True)
        
        # تحديث أصوات الموافقين
        updated_votes = initial_votes.copy()
        for idx, sup in enumerate(supporters):
            res = sup_results[idx] if not isinstance(sup_results[idx], Exception) else "REJECTED"
            updated_votes[sup] = self.engine._extract_vote(res)
            initial_reasoning[sup] = f"Reconsideration Statement:\n{res}"

        # جولة النقاش 2: إرسال مبررات الموافقين إلى المعترض لإقناعه بالترميم
        if updated_votes[supporters[0]] and updated_votes[supporters[1]]:
            logger.info(f"[Debate] Supporters confirmed. Asking dissenter {dissenting_agent} to reconsider...")
            convince_prompt = (
                f"You are a member of the sovereign Council of Sages of NEXUM PRO.\n"
                f"You previously voted REJECTED for the task: '{task}' due to: '{dissenting_reason}'.\n"
                f"However, the other two Sages strongly defend the approval for the following reasons:\n"
                f"1. {initial_reasoning[supporters[0]]}\n"
                f"2. {initial_reasoning[supporters[1]]}\n\n"
                f"Based on their defense, can you approve this task with conditional safeguards? "
                f"Respond with APPROVED if convinced, or stand firm with REJECTED and state your absolute veto reason."
            )

            if dissenting_agent == "claude":
                dissent_res = await self.engine._ask_claude(convince_prompt)
            elif dissenting_agent == "gpt":
                dissent_res = await self.engine._ask_gpt(convince_prompt)
            else:
                dissent_res = await self.engine._ask_gemini(convince_prompt)

            updated_votes[dissenting_agent] = self.engine._extract_vote(dissent_res)
            initial_reasoning[dissenting_agent] = f"Final Debate Response:\n{dissent_res}"

        # ─── فحص حالة التوافق النهائية ───
        if all(updated_votes.values()):
            logger.info("[Debate] Unanimous consensus reached after debate!")
            return await self._compile_consensus_token(task, initial_reasoning, updated_votes, "AAA Unanimous", True)
        
        approve_count = sum(1 for v in updated_votes.values() if v)
        if approve_count >= 2:
            logger.info("[Debate] Absolute 2/3 consensus maintained. Executive authorization granted.")
            return await self._compile_consensus_token(task, initial_reasoning, updated_votes, "A Consensus", True)

        logger.warning("[Debate] Debate did not resolve conflict. Task rejected.")
        return await self._compile_consensus_token(task, initial_reasoning, updated_votes, "F Failed", False)

    async def _compile_consensus_token(self, task: str, reasoning: dict, votes: dict, grade: str, approved: bool) -> Any:
        from council.consensus_engine import ConsensusToken
        merged = ""
        if approved:
            merged = await self.engine._merge_deliberation(task, reasoning)
        return ConsensusToken(
            approved=approved,
            votes=votes,
            reasoning=reasoning,
            consensus_grade=grade,
            merged_output=merged,
            timestamp=datetime.now().isoformat()
        )
