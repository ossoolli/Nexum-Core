import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
from agents.agent_smith import agent_smith

class TestAgentSmith(unittest.TestCase):
    def test_list_agents(self):
        agents = agent_smith.list_agents()
        self.assertIsInstance(agents, list)

    def test_spec_dir(self):
        spec_dir = os.path.join("storage", "agent_specs")
        self.assertTrue(os.path.isdir(spec_dir))

if __name__ == "__main__":
    unittest.main()
