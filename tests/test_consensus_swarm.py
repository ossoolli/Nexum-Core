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

    def test_agent_contract_event_serialization(self):
        """Verify AgentEvent serialization, base64 payload, and validation"""
        from protocols.agent_contract import AgentEvent, AgentContractValidator
        
        payload_dict = {"module": "auth", "status": "nominal"}
        import json
        payload_bytes = json.dumps(payload_dict).encode("utf-8")
        
        event = AgentEvent(
            sender="TestAgent",
            topic="security_alerts",
            payload=payload_bytes
        )
        
        # Test validation
        self.assertTrue(AgentContractValidator.validate_event(event))
        
        # Test serialization
        serialized = event.serialize()
        self.assertIsInstance(serialized, str)
        self.assertIn("TestAgent", serialized)
        self.assertIn("security_alerts", serialized)
        
        # Test deserialization
        deserialized = AgentEvent.deserialize(serialized)
        self.assertEqual(deserialized.sender, "TestAgent")
        self.assertEqual(deserialized.topic, "security_alerts")
        
        # Verify binary payload roundtrip
        decoded_payload = json.loads(deserialized.payload.decode("utf-8"))
        self.assertEqual(decoded_payload["module"], "auth")
        self.assertEqual(decoded_payload["status"], "nominal")

    def test_agent_contract_verdict_validation(self):
        """Verify DeliberationVerdict contract structures and schema validity"""
        from protocols.agent_contract import DeliberationVerdict, ModelVote, AgentContractValidator
        
        votes = [
            ModelVote(model_id="claude", approved=True, reasoning="Looks clean"),
            ModelVote(model_id="gpt", approved=True, reasoning="Verified specifications"),
            ModelVote(model_id="gemini", approved=False, reasoning="Minor concern")
        ]
        
        verdict = DeliberationVerdict(
            task_id="task-9999",
            approved=True,
            votes=votes,
            merged_output="print('Patched successfully!')",
            consensus_grade="A Consensus"
        )
        
        # Test validation
        self.assertTrue(AgentContractValidator.validate_verdict(verdict))
        
        # Convert to dictionary and back
        data = verdict.to_dict()
        self.assertEqual(data["task_id"], "task-9999")
        self.assertEqual(len(data["votes"]), 3)
        self.assertTrue(data["approved"])
        
        recreated = DeliberationVerdict.from_dict(data)
        self.assertEqual(recreated.consensus_grade, "A Consensus")
        self.assertEqual(recreated.votes[0].model_id, "claude")
        self.assertTrue(recreated.votes[0].approved)

    def test_adk_swarm_engine_initialization(self):
        """Verify ADKSwarmEngine initialization and collaborative Pydantic structures"""
        from swarm.adk_engine import ADKSwarmEngine
        engine = ADKSwarmEngine()
        
        # If Agent/ADK package is active, check structure, otherwise verify simulation
        try:
            from google.adk import Agent
        except ImportError:
            Agent = None
        if Agent:
            self.assertIsNotNone(engine.sentinel_agent)
            self.assertEqual(engine.sentinel_agent.name, "sentinel_audit_agent")
            self.assertEqual(len(engine.sentinel_agent.sub_agents), 1)
            self.assertEqual(engine.sentinel_agent.sub_agents[0].name, "gcp_deploy_agent")
            self.assertIsNotNone(engine.runner)
        else:
            self.assertIsNone(engine.sentinel_agent)

    def test_go_coordinator_bridge_execution(self):
        """Verify GoCoordinatorBridge executes cleanly and parses JSON correctly"""
        from core.go_coordinator_bridge import go_coordinator
        res = go_coordinator.execute_task("Self-test task via unittest", 0.3)
        self.assertIsInstance(res, dict)
        self.assertTrue(res["consensus_reached"])
        self.assertEqual(res["approved_proposal"]["agent_id"], "Agent-Security-QA")
        self.assertIn("Self-test task via unittest", res["approved_proposal"]["solution"])

if __name__ == "__main__":
    unittest.main()
