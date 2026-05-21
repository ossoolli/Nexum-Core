"""
☁️ GCP MCP Gateway — بوابة Google Cloud MCP لـ Nexum
يربط Nexum بكل MCP Servers المتاحة في مشروع GCP
"""
import os
try:
    from google.adk.tools.api_registry import ApiRegistry
except ImportError:
    # Fallback if library not installed yet in local env
    ApiRegistry = None

PROJECT_ID = "mytest-496209"
LOCATION = "global"

# MCP Servers المتاحة مع أدواتها
MCP_SERVERS = {
    "bigquery":         f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/bigquery.googleapis.com",
    "storage":          f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/storage.googleapis.com",
    "compute":          f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/compute.googleapis.com",
    "logging":          f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/logging.googleapis.com",
    "monitoring":       f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/monitoring.googleapis.com",
    "aiplatform":       f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/aiplatform.googleapis.com",
    "geminicloudassist":f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/geminicloudassist.googleapis.com",
    "agentregistry":    f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/agentregistry.googleapis.com",
    "cloudtrace":       f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/cloudtrace.googleapis.com",
}

def header_provider(context):
    return {"x-goog-user-project": PROJECT_ID}

class GCPMCPGateway:
    """بوابة مركزية لكل أدوات Google Cloud"""

    def __init__(self):
        if ApiRegistry:
            self.registry = ApiRegistry(
                api_registry_project_id=PROJECT_ID,
                header_provider=header_provider
            )
        else:
            self.registry = None
        self._toolsets = {}

    def get_toolset(self, service: str):
        """جلب أدوات خدمة معينة"""
        if not self.registry:
            return []
            
        if service not in self._toolsets:
            if service not in MCP_SERVERS:
                raise ValueError(f"خدمة غير معروفة: {service}")
            try:
                self._toolsets[service] = self.registry.get_toolset(
                    mcp_server_name=MCP_SERVERS[service]
                )
            except Exception as e:
                print(f"[GCPMCP] Error loading {service}: {e}")
                return []
        return self._toolsets[service]

    def list_available(self) -> list:
        return list(MCP_SERVERS.keys())

# Singleton
gcp_mcp = GCPMCPGateway()
