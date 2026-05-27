# -*- coding: utf-8 -*-
"""
tests/test_dynamic_council.py

اختبارات نظام مجلس الحكماء الديناميكي وإضافة العضو الجديد Grok.
تتحقق من الاستعلام المتوازي، معالجة الأخطاء، الصمود والتحويل للاحتياطي، واتخاذ القرارات بالتوافق الديناميكي.
"""

import unittest
from unittest.mock import patch, MagicMock
import asyncio

from council.consensus_engine import CouncilConsensusEngine, ConsensusToken
from council.debate_protocol import CouncilDebateProtocol


class TestDynamicCouncil(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.engine = CouncilConsensusEngine()

    @patch("council.consensus_engine.agent_platform")
    @patch("council.consensus_engine.llm_engine")
    @patch("council.consensus_engine.openai_engine")
    @patch("council.consensus_engine.gemini_service")
    @patch("council.consensus_engine.grok_service")
    async def test_unanimous_consensus_dynamic(self, mock_grok, mock_gemini, mock_openai, mock_llm, mock_platform):
        """التحقق من إجماع الحكماء الكلي ديناميكياً والموافقة المباشرة (Unanimous 4/4)"""
        # تهيئة حالة المحاكي
        mock_platform.is_available = True
        
        # محاكاة ردود النماذج الأربعة بالـ APPROVED
        mock_platform.ask.side_effect = lambda prompt, model: (f"APPROVED: I agree. Model: {model}", None)
        mock_gemini.ask.return_value = ("APPROVED: Merged code payload", None)

        token = await self.engine.deliberate("Test dynamic critical task")
        
        self.assertTrue(token.approved)
        self.assertEqual(token.consensus_grade, "AAA Unanimous")
        self.assertIn("claude", token.votes)
        self.assertIn("gpt", token.votes)
        self.assertIn("gemini", token.votes)
        self.assertIn("grok", token.votes)
        self.assertTrue(all(token.votes.values()))

    @patch("council.consensus_engine.agent_platform")
    @patch("council.consensus_engine.llm_engine")
    @patch("council.consensus_engine.openai_engine")
    @patch("council.consensus_engine.gemini_service")
    @patch("council.consensus_engine.grok_service")
    async def test_majority_consensus_initiates_debate(self, mock_grok, mock_gemini, mock_openai, mock_llm, mock_platform):
        """التحقق من حدوث خلاف (3 موافق، 1 معترض) وإطلاق بروتوكول النقاش الذاتي ديناميكياً"""
        mock_platform.is_available = True
        
        # محاكاة: claude, gpt, gemini -> APPROVED | grok -> REJECTED
        def platform_mock(prompt, model):
            if "grok" in model:
                return "REJECTED: Security risk found in task.", None
            return "APPROVED: Code looks safe.", None
            
        mock_platform.ask.side_effect = platform_mock
        mock_gemini.ask.return_value = ("APPROVED: Merged", None)

        # محاكاة بروتوكول النقاش ليرجع رد تأكيد
        with patch.object(self.engine.debate_protocol, "debate") as mock_debate:
            mock_debate.return_value = ConsensusToken(
                approved=True,
                votes={"claude": True, "gpt": True, "gemini": True, "grok": True},
                reasoning={},
                consensus_grade="A Consensus",
                merged_output="Merged code payload",
                timestamp=""
            )
            
            token = await self.engine.deliberate("Test debate task")
            
            self.assertTrue(token.approved)
            mock_debate.assert_called_once()

    @patch("council.consensus_engine.agent_platform")
    @patch("council.consensus_engine.grok_service")
    @patch("council.consensus_engine.gemini_service")
    async def test_grok_direct_fallback(self, mock_gemini, mock_grok, mock_platform):
        """التحقق من صمود النظام والتحويل للمستعلم المباشر لـ Grok عند تعطل منصة جوجل"""
        # منصة جوجل معطلة
        mock_platform.is_available = False
        
        # Grok المباشر متاح
        mock_grok.is_available = True
        mock_grok.ask.return_value = ("APPROVED: Direct Grok analysis ok.", None)
        mock_gemini.ask.return_value = ("APPROVED: Fallback", None)

        # استدعاء _ask_sage لنموذج grok
        grok_config = {"id": "grok", "model_name": "grok-beta"}
        res = await self.engine._ask_sage(grok_config, "Test prompt")
        
        self.assertIn("APPROVED", res)
        mock_grok.ask.assert_called_once()

    @patch("council.consensus_engine.agent_platform")
    @patch("council.consensus_engine.grok_service")
    @patch("council.consensus_engine.gemini_service")
    async def test_grok_ultimate_fallback_to_gemini(self, mock_gemini, mock_grok, mock_platform):
        """التحقق من التحويل الاحتياطي النهائي لجيميني عند تعطل كل من منصة جوجل والـ API المباشر لـ Grok"""
        mock_platform.is_available = False
        mock_grok.is_available = False
        
        # جيميني الاحتياطي جاهز للرد
        mock_gemini.ask.return_value = ("APPROVED: Gemini acting on behalf of Grok.", None)

        grok_config = {"id": "grok", "model_name": "grok-beta"}
        res = await self.engine._ask_sage(grok_config, "Test prompt")
        
        self.assertIn("acting on behalf of grok", res.lower())
        mock_gemini.ask.assert_called_once()


if __name__ == "__main__":
    unittest.main()
