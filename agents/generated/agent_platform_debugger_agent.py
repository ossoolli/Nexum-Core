import os
import requests
import json
from datetime import datetime
from typing import Dict, Any, List
from core.base_agent import BaseAgent

class AgentPlatformDebuggerAgent(BaseAgent):
    def __init__(self):
        try:
            super().__init__(
                name="agent_platform_debugger",
                tools=['search_web', 'fetch_webpage'],
                triggers=['every_hour']
            )
            self.log("AgentPlatformDebuggerAgent initialized successfully.")
        except Exception as e:
            # Fallback if logging fails before base initialization
            print(f"Error during initialization: {str(e)}")
            raise e

    def run(self, *args, **kwargs) -> Dict[str, Any]:
        try:
            self.log("Starting active platform connection diagnostics...")
            report = {
                "timestamp": datetime.utcnow().isoformat(),
                "status": "healthy",
                "failures_detected": [],
                "diagnostics": {}
            }

            # Define targets to monitor
            targets = {
                "OpenAI": {
                    "url": "https://api.openai.com/v1/models",
                    "key": os.getenv("OPENAI_API_KEY"),
                    "header_format": "Bearer {key}"
                },
                "Anthropic": {
                    "url": "https://api.anthropic.com/v1/messages",
                    "key": os.getenv("ANTHROPIC_API_KEY"),
                    "header_format": "{key}",
                    "extra_headers": {"anthropic-version": "2023-06-01", "content-type": "application/json"}
                },
                "HuggingFace": {
                    "url": "https://api-inference.huggingface.co/models",
                    "key": os.getenv("HF_API_KEY"),
                    "header_format": "Bearer {key}"
                }
            }

            for platform, config in targets.items():
                self.log(f"Diagnosing connection for {platform}...")
                test_result = self._test_connection(platform, config)
                report["diagnostics"][platform] = test_result
                
                if not test_result["success"]:
                    report["status"] = "degraded"
                    report["failures_detected"].append({
                        "platform": platform,
                        "error_type": test_result["error_type"],
                        "details": test_result["message"]
                    })
                    self._alert_user(platform, test_result)

            self.log(f"Diagnostics complete. Status: {report['status']}")
            return report
        except Exception as e:
            self.log(f"Fatal error in run execution: {str(e)}")
            return {"status": "failed", "error": str(e)}

    def _test_connection(self, platform: str, config: Dict[str, Any]) -> Dict[str, Any]:
        try:
            key = config.get("key")
            if not key:
                return {
                    "success": False,
                    "error_type": "Missing Credentials",
                    "message": f"API Key for {platform} is not set in environment variables."
                }

            headers = {
                "Authorization": config["header_format"].format(key=key)
            }
            if "extra_headers" in config:
                headers.update(config["extra_headers"])

            # Perform physical handshake test with a low timeout to prevent hanging
            response = requests.get(config["url"], headers=headers, timeout=10)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "message": "Connection active and authenticated."
                }
            elif response.status_code in [401, 403]:
                return {
                    "success": False,
                    "error_type": "Authentication Failure",
                    "status_code": response.status_code,
                    "message": "Invalid API key or unauthorized access scope."
                }
            elif response.status_code == 429:
                return {
                    "success": False,
                    "error_type": "Quota Exhaustion / Rate Limit",
                    "status_code": response.status_code,
                    "message": "API usage limit exceeded or rate limited."
                }
            else:
                return {
                    "success": False,
                    "error_type": f"Unexpected Status {response.status_code}",
                    "status_code": response.status_code,
                    "message": f"Server responded with: {response.text[:200]}"
                }

        except requests.exceptions.Timeout:
            self.log(f"Handshake timeout encountered for {platform}.")
            return {
                "success": False,
                "error_type": "Network Timeout",
                "message": "The connection attempt timed out. Check network configuration or platform status."
            }
        except requests.exceptions.RequestException as e:
            self.log(f"Network request exception for {platform}: {str(e)}")
            return {
                "success": False,
                "error_type": "Network Handshake Failure",
                "message": f"Failed to establish connection: {str(e)}"
            }
        except Exception as e:
            self.log(f"Unexpected error testing connection for {platform}: {str(e)}")
            return {
                "success": False,
                "error_type": "Unexpected Error",
                "message": str(e)
            }

    def _alert_user(self, platform: str, failure_info: Dict[str, Any]) -> None:
        try:
            # Log the critical alert locally
            alert_msg = f"[ALERT] Platform: {platform} | Type: {failure_info['error_type']} | Details: {failure_info['message']}"
            self.log(alert_msg)
            
            # Here we could also trigger automated web searches to see if the provider is down globally
            self.log(f"Triggering quick health status lookup for {platform} via search tools...")
            search_query = f"{platform} API status down check"
            # Simulated tool call wrapper safely handling failures
            try:
                search_results = self.search_web(search_query) if hasattr(self, 'search_web') else "Search tool unavailable"
                self.log(f"Global status search context: {str(search_results)[:300]}...")
            except Exception as tool_err:
                self.log(f"Could not fetch external status search: {str(tool_err)}")
                
        except Exception as e:
            self.log(f"Failed to generate alert notification: {str(e)}")