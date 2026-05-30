import json
from core.memory.sovereign_memory import SovereignMemory

def populate_mcp_catalog():
    memory = SovereignMemory()
    import os
    project_dir = os.path.dirname(os.path.abspath(__file__))
    catalog_path = os.path.join(project_dir, "storage", "mcp-servers.json")
    if not os.path.exists(catalog_path):
        print(f"MCP catalog file not found at {catalog_path}")
        return
    with open(catalog_path, "r") as f:
        data = json.load(f)
    
    servers = data.get("mcpServers", {})
    for name, config in servers.items():
        description = f"MCP Server: {name}, Command: {config['command']}, Args: {config['args']}"
        memory.add_memory("mcp_catalog", description)
        print(f"Stored MCP server: {name}")

if __name__ == "__main__":
    populate_mcp_catalog()
