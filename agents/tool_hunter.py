import os
import json
import requests
import logging
from datetime import datetime, timedelta
from core.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ToolHunterAgent(BaseAgent):
    """
    ToolHunterAgent — النمو الذاتي
    يبحث عن أدوات MCP جديدة على GitHub ويقوم بفلترتها وتخزينها.
    """

    def __init__(self):
        super().__init__(
            name="tool_hunter",
            description="وكيل البحث عن الأدوات (Self-Growth Agent)",
            version="1.0"
        )
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.discovered_file = os.path.join(base_dir, "storage", "discovered_tools.json")
        self.github_token = os.getenv("GITHUB_TOKEN")

    def search_mcp_servers(self) -> list:
        """البحث في GitHub عن مستودعات MCP"""
        last_week = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        query = f"topic:mcp-server created:>{last_week}"
        url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc"
        
        headers = {}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
            
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            items = response.json().get("items", [])
            
            filtered = []
            for item in items:
                if item["stargazers_count"] > 10 and item["language"] in ["Python", "JavaScript", "TypeScript"]:
                    filtered.append({
                        "id": item["id"],
                        "name": item["full_name"],
                        "url": item["html_url"],
                        "stars": item["stargazers_count"],
                        "language": item["language"],
                        "description": item["description"],
                        "discovered_at": datetime.now().isoformat()
                    })
            return filtered
        except Exception as e:
            self.log(f"GitHub Search failed: {e}", level="ERROR")
            return []

    def run(self, input_data: dict = None) -> dict:
        """دورة البحث اليومية"""
        self.log("Starting daily tool search...")
        tools = self.search_mcp_servers()
        
        if tools:
            self._update_discovered_tools(tools)
            self.record_metric("discovered_count", len(tools))
            return {"status": "success", "count": len(tools), "tools": tools}
        
        return {"status": "success", "count": 0}

    def _update_discovered_tools(self, new_tools: list):
        try:
            data = []
            if os.path.exists(self.discovered_file):
                with open(self.discovered_file, 'r') as f:
                    data = json.load(f)
            
            # منع التكرار بناءً على ID
            existing_ids = {item["id"] for item in data}
            for tool in new_tools:
                if tool["id"] not in existing_ids:
                    data.append(tool)
            
            with open(self.discovered_file, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            self.log(f"Failed to save discovered tools: {e}", level="ERROR")

tool_hunter = ToolHunterAgent()
