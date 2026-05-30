import sys
import os
# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import json
from core.memory.sovereign_memory import SovereignMemory

class MCPDispatcher:
    def __init__(self):
        self.memory = SovereignMemory()
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.mcp_config_path = os.path.join(project_root, "storage", "mcp-servers.json")
        with open(self.mcp_config_path, "r") as f:
            self.servers = json.load(f).get("mcpServers", {})

    def find_relevant_mcp_server(self, task_description: str):
        # Recall from memory
        relevant_memories = self.memory.search_memory(task_description)
        
        # Simple heuristic: look for server name in query
        for name, config in self.servers.items():
            if name.lower() in task_description.lower():
                return {"server": name, "config": config}
        
        return None
