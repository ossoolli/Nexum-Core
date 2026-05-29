from nexum.cloud.agent_platform_connector import GoogleAgentPlatformConnector

def verify_orchestrator():
    connector = GoogleAgentPlatformConnector()
    task = "query the bigquery table"
    result = connector.run_cognitive_flow(task)
    
    mcp_task = result.get("mcp_task")
    print(f"Task: {task}")
    print(f"MCP Task Identified: {mcp_task}")
    
    if mcp_task and mcp_task['server'] == 'bigquery':
        print("Verification Successful: BigQuery MCP server identified.")
    else:
        print("Verification Failed: Could not identify BigQuery MCP server.")

if __name__ == "__main__":
    verify_orchestrator()
