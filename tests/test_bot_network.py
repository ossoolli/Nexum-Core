import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
from core.bot_network import bot_network

class TestBotNetwork(unittest.TestCase):
    def test_local_fallback(self):
        # We assume redis is not connected in tests
        res = bot_network.broadcast_all("test_bot", "Hello Network")
        self.assertIsInstance(res, int)

if __name__ == "__main__":
    unittest.main()
