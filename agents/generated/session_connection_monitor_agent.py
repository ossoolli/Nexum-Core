import os
import sys
import time
import socket
import ssl
import traceback
from typing import List, Dict, Any
from core.base_agent import BaseAgent

class SessionConnectionMonitorAgent(BaseAgent):
    """
    SessionConnectionMonitorAgent
    An autonomous agent designed to monitor and analyze connection sessions in real-time,
    identifying precise causes of handshake failures or session disconnections.
    """

    def __init__(self, agent_id: str = "session_connection_monitor", *args, **kwargs):
        try:
            super().__init__(agent_id=agent_id, *args, **kwargs)
            self.agent_name = "Session Connection Monitor"
            self.tools = ['search_web', 'fetch_webpage']
            self.triggers = ['every_hour']
            self.monitored_targets = [
                {"host": "github.com", "port": 443},
                {"host": "api.openai.com", "port": 443},
                {"host": "google.com", "port": 443}
            ]
            self.log("SessionConnectionMonitorAgent initialized successfully.")
        except Exception as e:
            print(f"Error during initialization: {str(e)}")
            raise e

    def check_connection_sessions(self) -> List[Dict[str, Any]]:
        """
        Actively probes targets to monitor real-time connection status, 
        detecting TLS/SSL handshake failures or raw connection drops.
        """
        try:
            self.log("Starting active probe of monitored targets...")
            session_statuses = []

            for target in self.monitored_targets:
                host = target["host"]
                port = target["port"]
                status_entry = {
                    "host": host,
                    "port": port,
                    "connection_established": False,
                    "handshake_successful": False,
                    "error_type": None,
                    "error_details": None
                }

                # Try standard socket connection
                try:
                    sock = socket.create_connection((host, port), timeout=5)
                    status_entry["connection_established"] = True
                    
                    # Try TLS/SSL Handshake
                    context = ssl.create_default_context()
                    try:
                        secure_sock = context.wrap_socket(sock, server_hostname=host)
                        status_entry["handshake_successful"] = True
                        secure_sock.close()
                    except ssl.SSLError as ssl_err:
                        status_entry["error_type"] = "Handshake Failure"
                        status_entry["error_details"] = f"SSL/TLS Error: {str(ssl_err)}"
                        self.log(f"Handshake failed for {host}:{port} - {str(ssl_err)}", level="WARNING")
                    except Exception as handshake_err:
                        status_entry["error_type"] = "Handshake Failure"
                        status_entry["error_details"] = f"Generic Handshake Error: {str(handshake_err)}"
                        self.log(f"Generic Handshake failed for {host}:{port} - {str(handshake_err)}", level="WARNING")
                    finally:
                        sock.close()

                except socket.timeout:
                    status_entry["error_type"] = "Connection Timeout"
                    status_entry["error_details"] = "Connection attempt timed out. Firewall or routing issue suspected."
                    self.log(f"Timeout connecting to {host}:{port}", level="WARNING")
                except ConnectionRefusedError:
                    status_entry["error_type"] = "Connection Refused"
                    status_entry["error_details"] = "Remote host refused the connection on target port."
                    self.log(f"Connection refused by {host}:{port}", level="WARNING")
                except Exception as conn_err:
                    status_entry["error_type"] = "Network Issue"
                    status_entry["error_details"] = f"Failed to connect: {str(conn_err)}"
                    self.log(f"Network error connecting to {host}:{port} - {str(conn_err)}", level="WARNING")

                session_statuses.append(status_entry)

            return session_statuses
        except Exception as e:
            self.log(f"Error in check_connection_sessions: {str(e)}", level="ERROR")
            return []

    def run_deep_diagnostic(self, error_type: str, error_details: str) -> str:
        """
        Uses web tools autonomously to match obscure socket/SSL error codes to actual known fixes.
        """
        try:
            self.log(f"Running autonomous deep diagnosis for: [{error_type}] {error_details}")
            
            # Formulate query
            query = f"TLS handshake failure socket error {error_details} troubleshoot"
            self.log(f"Searching web using tool 'search_web' with query: {query}")
            
            # Simulate utilizing the 'search_web' tool
            search_results = self.call_tool("search_web", {"query": query})
            
            # Standard diagnostics resolution logic
            diagnostic_report = f"Analysis for: {error_type}.\nDetails: {error_details}\n"
            if "certificate verify failed" in error_details.lower():
                diagnostic_report += "Resolution: Local root certificates or CA bundle might be outdated/expired."
            elif "timeout" in error_type.lower():
                diagnostic_report += "Resolution: Check packet filters, outbound security rules, MTU path, or target server availability."
            elif "refused" in error_type.lower():
                diagnostic_report += "Resolution: Target port is not open, services are down, or traffic is blocked by target firewall."
            else:
                diagnostic_report += f"Resolution: Investigate network telemetry. Search results summary: {search_results}"
                
            return diagnostic_report
        except Exception as e:
            self.log(f"Error in run_deep_diagnostic: {str(e)}", level="ERROR")
            return "Failed to complete deep diagnostics."

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Wrapper to handle tool calls.
        """
        try:
            if tool_name in self.tools:
                self.log(f"Invoking tool '{tool_name}' with args: {arguments}")
                # Mock response to fit execution if base system tools execution is decoupled
                return f"[Mocked {tool_name} response for query/argument: {list(arguments.values())[0]}]"
            else:
                return f"Tool {tool_name} not available."
        except Exception as e:
            self.log(f"Error calling tool {tool_name}: {str(e)}", level="ERROR")
            return f"Error executing tool {tool_name}"

    def run(self) -> Dict[str, Any]:
        """
        Main execution loop triggered automatically.
        """
        try:
            self.log("SessionConnectionMonitorAgent execution cycle initiated.")
            
            # Step 1: Check connectivity and find handshake/session issues
            session_statuses = self.check_connection_sessions()
            
            failed_sessions = [s for s in session_statuses if not s["handshake_successful"] or not s["connection_established"]]
            successful_sessions = [s for s in session_statuses if s["handshake_successful"]]
            
            diagnostics = []
            
            # Step 2: Auto-diagnose failures
            if failed_sessions:
                self.log(f"Detected {len(failed_sessions)} unstable sessions. Starting diagnostics.")
                for session in failed_sessions:
                    diagnosis = self.run_deep_diagnostic(
                        error_type=session["error_type"],
                        error_details=session["error_details"]
                    )
                    diagnostics.append({
                        "host": session["host"],
                        "port": session["port"],
                        "error_type": session["error_type"],
                        "error_details": session["error_details"],
                        "suggested_remediation": diagnosis
                    })
            else:
                self.log("All monitored sessions are established and handshakes succeeded.")

            # Compile results
            report = {
                "status": "success",
                "timestamp": time.time(),
                "total_monitored": len(session_statuses),
                "healthy_sessions": len(successful_sessions),
                "unhealthy_sessions": len(failed_sessions),
                "failures_diagnosed": diagnostics
            }
            
            self.log(f"Cycle completed. Diagnostics report summary: {report}")
            return report

        except Exception as e:
            error_msg = f"Critical failure in Agent run loop: {str(e)}\n{traceback.format_exc()}"
            self.log(error_msg, level="ERROR")
            return {
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }