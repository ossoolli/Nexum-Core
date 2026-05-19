import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
from core.bot_fleet import bot_fleet

class TestBotFleet(unittest.TestCase):
    def test_list_bots(self):
        bots = bot_fleet.list_bots()
        self.assertIsInstance(bots, list)

    def test_registry_path(self):
        self.assertTrue(bot_fleet.registry_path.endswith(".json"))

if __name__ == "__main__":
    unittest.main()
