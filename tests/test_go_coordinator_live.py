# -*- coding: utf-8 -*-
"""
🧪 Unit Test for Live Go REST Microservice & Bridge
===================================================
Verifies the Go server's background startup, REST API endpoints,
and the Python bridge communication flow.
"""

import os
import sys
import unittest
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from core.go_coordinator_bridge import GoCoordinatorBridge

class TestGoCoordinatorLive(unittest.TestCase):
    def setUp(self):
        # Start a bridge on a separate custom test port to avoid conflict with main port
        self.bridge = GoCoordinatorBridge(port=50052)

    def tearDown(self):
        # Stop and clean up Go server
        self.bridge.close()

    def test_server_status_and_ping(self):
        """Verify the Go REST server starts and exposes /status endpoint successfully"""
        self.assertTrue(self.bridge._is_port_open(), "Go REST server failed to start or bind to port.")
        
        # Test status endpoint directly
        import requests
        try:
            response = requests.get(f"{self.bridge.server_url}/status", timeout=1.0)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data.get("status"), "active")
            self.assertIn("redis_online", data)
        except Exception as e:
            self.fail(f"Failed to query /status endpoint: {e}")

    def test_execute_task_consensus(self):
        """Verify task execution successfully coordinates consensus and returns formatted results"""
        task_desc = "Implement high-performance Go coordinator and Redis state synchronizer"
        
        # Run with threshold allowing successful consensus (0.3 threshold, security QA is 0.05)
        res = self.bridge.execute_task(task_desc, threshold=0.3)
        
        self.assertIsInstance(res, dict)
        self.assertTrue(res.get("consensus_reached"), "Consensus should be reached with threshold 0.3")
        self.assertIn("approved_proposal", res)
        self.assertEqual(res["approved_proposal"]["agent_id"], "Agent-Security-QA")
        self.assertLessEqual(res["approved_proposal"]["risk_score"], 0.3)
        self.assertIn("system_metrics", res)
        self.assertIn("Security & QA Auditor", res["system_metrics"])

    def test_execute_task_failed_consensus(self):
        """Verify task execution fails consensus if threshold is extremely strict"""
        task_desc = "Test strict safety thresholds"
        
        # Run with an extremely strict threshold (e.g. 0.01) which rejects all proposals
        res = self.bridge.execute_task(task_desc, threshold=0.01)
        
        self.assertIsInstance(res, dict)
        self.assertFalse(res.get("consensus_reached"), "Consensus should fail with a 0.01 risk threshold.")
        self.assertEqual(res["approved_proposal"]["agent_id"], "N/A")
        self.assertEqual(res["approved_proposal"]["risk_score"], 1.0)

if __name__ == "__main__":
    unittest.main()
