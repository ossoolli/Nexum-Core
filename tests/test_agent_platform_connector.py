# -*- coding: utf-8 -*-
"""
🧪 Unit Test Suite for Google Cloud Agent Platform Integration
=============================================================
Verifies successful SDK package integration, IAM configuration management,
Dialogflow CX conversational workflows, and Discovery Engine RAG search fallbacks.
"""

import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from nexum.cloud import (
    GoogleAgentPlatformConnector,
    NexumSecurityConfig,
    DialogflowCXConnector,
    DiscoveryEngineConnector
)

class TestAgentPlatformConnector(unittest.TestCase):
    def setUp(self):
        # Initialize the gateway with a dummy service account to run in mock fallback/simulation mode
        self.gateway = GoogleAgentPlatformConnector(
            service_account_path="non_existent_credentials.json",
            project_id="test-project-1234",
            location="us-central1",
            agent_id="test-agent-9999",
            search_engine_id="test-search-engine"
        )

    def test_imports_and_exposure(self):
        """Verify all critical Agent Platform classes import and load successfully"""
        self.assertIsNotNone(GoogleAgentPlatformConnector)
        self.assertIsNotNone(NexumSecurityConfig)
        self.assertIsNotNone(DialogflowCXConnector)
        self.assertIsNotNone(DiscoveryEngineConnector)

    def test_security_config_initialization(self):
        """Verify NexumSecurityConfig initializes and handles non-existent credentials gracefully"""
        config = NexumSecurityConfig(
            service_account_path="missing_file.json",
            project_id="my-project"
        )
        self.assertEqual(config.project_id, "my-project")
        self.assertEqual(config.location, "us-central1")
        self.assertIsNone(config.credentials, "Credentials should be None when credential file is missing.")

    def test_dialogflow_intent_detection(self):
        """Verify DialogflowCXConnector detect_intent successfully returns simulated conversational results"""
        # Test Development Plan Intent
        res_plan = self.gateway.dialogflow.detect_intent("أعطني خطة تطوير النظام")
        self.assertIsInstance(res_plan, dict)
        self.assertEqual(res_plan["intent_name"], "system_development_plan")
        self.assertIn("خطة", res_plan["fulfillment_text"])
        self.assertTrue(res_plan["parameters"]["simulation_mode"])

        # Test Security Audit Intent
        res_sec = self.gateway.dialogflow.detect_intent("فحص أمان وموارد السيرفر")
        self.assertIsInstance(res_sec, dict)
        self.assertEqual(res_sec["intent_name"], "security_audit_run")
        self.assertIn("nominal", res_sec["fulfillment_text"])

    def test_discovery_engine_rag_search(self):
        """Verify DiscoveryEngineConnector search_knowledge successfully retrieves semantic documents"""
        # Test search query matching consensus documentation
        res = self.gateway.search.search_knowledge("Consensus")
        
        self.assertIsInstance(res, dict)
        self.assertGreaterEqual(res["retrieved_count"], 1)
        self.assertEqual(res["query"], "Consensus")
        
        # Verify document structure
        first_doc = res["results"][0]
        self.assertIn("id", first_doc)
        self.assertIn("title", first_doc)
        self.assertIn("snippet", first_doc)
        self.assertIn("link", first_doc)
        self.assertIn("Consensus", first_doc["snippet"] + first_doc["title"])

    def test_unified_cognitive_flow(self):
        """Verify GoogleAgentPlatformConnector run_cognitive_flow coordinates conversation and RAG context"""
        prompt = "أعطني خطة أمان وتطوير لمجلس الحكماء"
        flow_res = self.gateway.run_cognitive_flow(prompt, session_id="test_session_abc")
        
        self.assertIsInstance(flow_res, dict)
        self.assertEqual(flow_res["prompt"], prompt)
        self.assertEqual(flow_res["session_id"], "test_session_abc")
        self.assertIsNotNone(flow_res["fulfillment_response"])
        self.assertIsNotNone(flow_res["detected_intent"])
        self.assertIn("rag_knowledge_context", flow_res)
        self.assertIn("Consensus", flow_res["rag_knowledge_context"])
        self.assertFalse(flow_res["gcp_connected"], "Should be false in mock simulation mode.")

if __name__ == "__main__":
    unittest.main()
