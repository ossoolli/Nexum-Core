import sys
import os
import logging
sys.path.append('/home/madarmutaz/Nexum-Core')

from nexum.cloud.agent_platform_connector import GoogleAgentPlatformConnector

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_gcp_connection")

def test():
    # If GOOGLE_APPLICATION_CREDENTIALS is set, it will be used by the connector if passed
    # However, NexumSecurityConfig logic:
    # 60: if self.service_account_path and os.path.exists(self.service_account_path):
    # 61:     os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.service_account_path
    
    # So we need to provide a path.
    
    # Check if a credential file exists in a default location or env
    creds_path = os.getenv("GCP_SA_KEY_PATH", "credentials.json")
    
    if not os.path.exists(creds_path):
        logger.warning(f"Credentials file not found at {creds_path}. Please set GCP_SA_KEY_PATH or provide a valid path.")
        return

    try:
        logger.info(f"Attempting connection with credentials at {creds_path}")
        connector = GoogleAgentPlatformConnector(
            service_account_path=creds_path,
            project_id="mytest-496209", # As seen in connector.py default
            agent_id="agent-platform-cx-99"
        )
        # Try a real flow
        result = connector.run_cognitive_flow("Hello")
        
        if result.get("gcp_connected"):
            print("✅ Successfully connected to Vertex AI!")
            print(f"Result: {result}")
        else:
            print("❌ Failed to connect to Vertex AI. Simulation mode is active.")
            print(f"Result: {result}")
            
    except Exception as e:
        logger.error(f"Error connecting to Vertex AI: {e}")

if __name__ == "__main__":
    test()
