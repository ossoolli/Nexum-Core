import json
from core.memory.sovereign_memory import SovereignMemory

def populate_mcp_catalog():
    memory = SovereignMemory()
    with open("/home/madarmutaz/Nexum-Core/storage/mcp-servers.json", "r") as f:
        data = json.load(f)
    
    servers = data.get("mcpServers", {})
    for name, config in servers.items():
        description = f"MCP Server: {name}, Command: {config['command']}, Args: {config['args']}"
        memory.add_memory("mcp_catalog", description)
        print(f"Stored MCP server: {name}")

if __name__ == "__main__":
    populate_mcp_catalog()
