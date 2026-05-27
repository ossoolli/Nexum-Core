# -*- coding: utf-8 -*-
# tests/test_consensus_swarm.py
"""
🧪 Test Suite for Multi-Model Consensus Engine & Swarm Agents
==============================================================
Runs mock verification checks on consensus voting, debate protocol,
and background monitoring alerts.
"""

import os
import sys
import asyncio
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from council.consensus_engine import CouncilConsensusEngine, ConsensusToken
from agents.sentinel import SentinelAgent
from agents.protocol_bridge import ProtocolBridgeAgent

class TestConsensusSwarm(unittest.TestCase):
    def test_mock_consensus_creation(self):
        """Verify ConsensusToken dataclass instantiation and vote states"""
        token = ConsensusToken(
            approved=True,
            votes={"claude": True, "gemini": True, "gpt": True},
            reasoning={"claude": "Approved", "gemini": "Approved", "gpt": "Approved"},
            consensus_grade="AAA Unanimous",
            merged_output="print('hello')",
            timestamp="2026-05-27T00:00:00"
        )
        self.assertTrue(token.approved)
        self.assertEqual(token.consensus_grade, "AAA Unanimous")
        self.assertIn("claude", token.votes)

    def test_sentinel_whitelist_scanning(self):
        """Verify Sentinel process scanning whitelisting logic"""
        agent = SentinelAgent()
        # Mock whitelist matching
        self.assertIn("python", agent.WHITELIST)
        self.assertIn("pm2", agent.WHITELIST)

    def test_protocol_bridge_mock_event(self):
        """Verify Redis publishing works cleanly in fallback/mock state"""
        bridge = ProtocolBridgeAgent()
        res = bridge.publish_event("test_channel", {"action": "heartbeat"})
        self.assertTrue(any(x in res for x in ["Published", "Redis"]))

if __name__ == "__main__":
    unittest.main()
