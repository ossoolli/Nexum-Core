import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
from agents.webforge_agent import webforge

class TestWebForge(unittest.TestCase):
    def test_project_listing(self):
        projects = webforge.list_projects()
        self.assertIsInstance(projects, list)

    def test_template_existence(self):
        template_path = os.path.join("storage", "templates", "landing_page.html")
        self.assertTrue(os.path.exists(template_path))

if __name__ == "__main__":
    unittest.main()
