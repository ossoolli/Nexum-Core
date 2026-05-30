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
    "bigquery":             f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/bigquery.googleapis.com",
    "storage":              f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/storage.googleapis.com",
    "compute":              f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/compute.googleapis.com",
    "logging":              f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/logging.googleapis.com",
    "monitoring":           f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/monitoring.googleapis.com",
    "aiplatform":           f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/aiplatform.googleapis.com",
    "geminicloudassist":    f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/geminicloudassist.googleapis.com",
    "agentregistry":        f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/agentregistry.googleapis.com",
    "cloudtrace":           f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/cloudtrace.googleapis.com",
    "pubsub":               f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/pubsub.googleapis.com",
    "spanner":              f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/spanner.googleapis.com",
    "sqladmin":             f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/sqladmin.googleapis.com",
    # خوادم GCP MCP الإضافية كما طلب المايسترو
    "apptopology":          f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/apptopology.googleapis.com",
    "bigquerydatatransfer": f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/bigquerydatatransfer.googleapis.com",
    "bigquerymigration":    f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/bigquerymigration.googleapis.com",
    "ces":                  f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/ces.googleapis.com",
    "container":            f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/container.googleapis.com",
    "dataplex":             f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/dataplex.googleapis.com",
    "dataproc":             f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/dataproc.googleapis.com",
    "designcenter":         f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/designcenter.googleapis.com",
    "discoveryengine":      f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/discoveryengine.googleapis.com",
    "saasservicemgmt":      f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/saasservicemgmt.googleapis.com",
    "cloudresourcemanager": f"projects/{PROJECT_ID}/locations/{LOCATION}/mcpServers/cloudresourcemanager.googleapis.com",
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
