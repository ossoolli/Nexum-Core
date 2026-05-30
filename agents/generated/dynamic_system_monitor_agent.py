from core.base_agent import BaseAgent
import time # Used for basic timestamping for monitored entities

class DynamicSystemMonitorAgent(BaseAgent):
    def __init__(self, agent_id: str, *args, **kwargs):
        """
        Initializes the DynamicSystemMonitorAgent.
        """
        try:
            super().__init__(
                agent_id=agent_id, # Unique identifier for the agent instance
                name="dynamic_system_monitor",
                goal="Proactively discover, onboard, and continuously monitor the health and operational status of new or undefined services, processes, or external entities within or relevant to the NEXUM PRO environment, and automatically identify and report anomalies or issues.",
                tools=['search_web', 'fetch_webpage'],
                triggers=['every_hour'],
                *args,
                **kwargs
            )
            # A simple in-memory store for entities being monitored
            # In a real system, this would be persisted (e.g., database, file)
            self.monitored_entities = {}
            self.log("DynamicSystemMonitorAgent initialized successfully.", level="INFO")
        except Exception as e:
            self.log(f"Error during DynamicSystemMonitorAgent initialization: {e}", level="ERROR")

    def run(self):
        """
        Executes the main monitoring cycle of the agent.
        This method is called based on the defined triggers (e.g., 'every_hour').
        """
        try:
            self.log("DynamicSystemMonitorAgent run cycle started.", level="INFO")

            # --- Step 1: Proactively discover new services/entities ---
            self.log("Attempting to discover new services or external entities relevant to NEXUM PRO...", level="INFO")
            
            # Use search_web tool to look for new services, status pages, or relevant news
            discovery_queries = [
                "NEXUM PRO new service announcements",
                "NEXUM PRO external integrations status",
                "NEXUM PRO partner systems operational status"
            ]
            
            newly_discovered_urls = set()
            for query in discovery_queries:
                try:
                    search_results = self.call_tool('search_web', query=query)
                    if search_results:
                        self.log(f"Search for '{query}' returned {len(search_results)} results. Processing...", level="INFO")
                        for item in search_results:
                            if isinstance(item, dict) and 'link' in item:
                                if item['link'] not in self.monitored_entities:
                                    newly_discovered_urls.add(item['link'])
                                    self.log(f"Potential new entity discovered: {item['link']}", level="DEBUG")
                    else:
                        self.log(f"No results for discovery query: '{query}'", level="DEBUG")
                except Exception as search_e:
                    self.log(f"Error during web search for '{query}': {search_e}", level="ERROR")

            # Onboard newly discovered entities
            if newly_discovered_urls:
                for url in newly_discovered_urls:
                    if url not in self.monitored_entities:
                        self.monitored_entities[url] = {
                            "status": "unknown",
                            "last_check_time": None,
                            "first_discovered_time": time.time(),
                            "history": [] # To store status changes
                        }
                        self.log(f"Onboarded new entity for monitoring: {url}", level="INFO")
            else:
                self.log("No new entities discovered for onboarding during this cycle.", level="INFO")

            # --- Step 2: Continuously monitor the health and operational status ---
            self.log("Monitoring health and operational status of known entities...", level="INFO")
            
            entities_to_monitor = list(self.monitored_entities.keys())
            if not entities_to_monitor:
                self.log("No entities currently onboarded for monitoring.", level="INFO")

            for entity_url in entities_to_monitor:
                current_timestamp = time.time()
                previous_status = self.monitored_entities[entity_url].get("status")
                
                try:
                    self.log(f"Fetching status for entity: {entity_url}...", level="INFO")
                    webpage_content = self.call_tool('fetch_webpage', url=entity_url)
                    
                    current_status = "operational" # Default assumption
                    anomaly_detected = False
                    report_message = None

                    if webpage_content:
                        # Simple content analysis for health status and anomaly detection
                        content_lower = webpage_content.lower()
                        
                        if any(keyword in content_lower for keyword in ["error", "down", "issue", "outage", "unreachable"]):
                            current_status = "degraded/down"
                            anomaly_detected = True
                            report_message = f"Potential anomaly detected for {entity_url}: Keywords 'error'/'down'/'issue'/'outage' found in content."
                        elif any(keyword in content_lower for keyword in ["maintenance", "planned downtime"]):
                            current_status = "maintenance"
                            report_message = f"Entity {entity_url} is in maintenance mode."
                        
                        # Compare with previous status for changes
                        if previous_status != current_status and current_status != "unknown":
                            anomaly_detected = True
                            report_message = f"Status change detected for {entity_url}: {previous_status} -> {current_status}"
                            self.log(report_message, level="WARNING")
                        
                        self.log(f"Entity {entity_url} is currently {current_status}.", level="INFO")

                    else: # webpage_content is None or empty, indicating fetch failure
                        current_status = "unreachable"
                        anomaly_detected = True
                        report_message = f"Failed to fetch content for {entity_url}. Entity might be down or unreachable."
                        self.log(report_message, level="ERROR")
                    
                    # Update entity state
                    self.monitored_entities[entity_url]["status"] = current_status
                    self.monitored_entities[entity_url]["last_check_time"] = current_timestamp
                    self.monitored_entities[entity_url]["history"].append({
                        "timestamp": current_timestamp,
                        "status": current_status,
                        "anomaly_detected": anomaly_detected
                    })

                    # --- Step 3: Automatically identify and report anomalies or issues ---
                    if anomaly_detected:
                        self.log(f"ANOMALY REPORT for {entity_url}: {report_message if report_message else 'Anomaly detected without specific message.'}", level="CRITICAL")
                    
                except Exception as monitor_e:
                    self.log(f"Error monitoring {entity_url}: {monitor_e}", level="ERROR")
                    # Mark status as monitoring error if an exception occurs during monitoring
                    self.monitored_entities[entity_url]["status"] = "monitoring_error"
                    self.monitored_entities[entity_url]["last_check_time"] = current_timestamp
                    self.monitored_entities[entity_url]["history"].append({
                        "timestamp": current_timestamp,
                        "status": "monitoring_error",
                        "anomaly_detected": True,
                        "error_message": str(monitor_e)
                    })
                    self.log(f"ANOMALY REPORT for {entity_url}: Monitoring failed due to {monitor_e}", level="CRITICAL")

            self.log("DynamicSystemMonitorAgent run cycle finished.", level="INFO")

        except Exception as e:
            self.log(f"Unhandled error during DynamicSystemMonitorAgent run cycle: {e}", level="CRITICAL")