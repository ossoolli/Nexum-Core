import json
import traceback
import datetime
from core.base_agent import BaseAgent

class SystemEntityMonitorAgent(BaseAgent):
    def __init__(self):
        try:
            super().__init__()
            self.name = "system_entity_monitor"
            self.description = "Automatically detect, onboard, and monitor the health and status of user-defined system components or processes (e.g., 'Mutaz live') that are not explicitly pre-configured or known within NEXUM PRO's current operational scope or monitored environments, and report on any identified errors or unexpected behavior."
            self.tools = ['search_web', 'fetch_webpage']
            self.triggers = ['every_hour']
            
            # This list would ideally be persistent or loaded from a knowledge base
            self.monitored_entities = [] 
            self._initialize_monitored_entities()

            self.log(f"Agent '{self.name}' initialized successfully.")
        except Exception as e:
            self.log(f"Error during SystemEntityMonitorAgent initialization: {e}\n{traceback.format_exc()}")

    def _initialize_monitored_entities(self):
        try:
            if not any(e['name'] == 'Mutaz live' for e in self.monitored_entities):
                self.monitored_entities.append({'name': 'Mutaz live', 'last_status': 'unknown'})
            self.log(f"Initial monitored entities configured: {[e['name'] for e in self.monitored_entities]}")
        except Exception as e:
            self.log(f"Error during _initialize_monitored_entities: {e}\n{traceback.format_exc()}")

    async def run(self, input_data: dict = None):
        try:
            timestamp = datetime.datetime.now().isoformat()
            self.log(f"Agent '{self.name}' initiated run at {timestamp}.")

            # Phase 1: Dynamic Detection/Discovery of new user-defined system components
            discovery_queries = [
                "NEXUM PRO new system components status",
                "NEXUM PRO recently deployed services health",
                "user-defined system process issues"
            ]

            for query in discovery_queries:
                self.log(f"Attempting to discover new entities with query: '{query}' using search_web.")
                search_results = await self.search_web(query)
                if search_results:
                    self.log(f"Found search results for '{query}'. Processing for potential new entities.")
                    for result in search_results[:2]: 
                        potential_entity_name = self._extract_entity_from_search_result(result)
                        if potential_entity_name and not any(e['name'] == potential_entity_name for e in self.monitored_entities):
                            self.monitored_entities.append({'name': potential_entity_name, 'last_status': 'discovered'})
                            self.log(f"Dynamically 'onboarded' new entity: '{potential_entity_name}'")
                else:
                    self.log(f"No new potential entities found for query: '{query}'.")

            self.log(f"Current list of entities to monitor: {[e['name'] for e in self.monitored_entities]}")

            # Phase 2: Monitoring the health and status of identified components
            monitoring_results = []
            for entity in self.monitored_entities:
                entity_name = entity.get('name')
                self.log(f"Monitoring health of entity: '{entity_name}'.")
                status_query = f"{entity_name} health status NEXUM PRO"
                
                status_search_results = await self.search_web(status_query)
                
                entity_status = "unknown"
                error_detected = False
                report_message = f"Monitoring report for '{entity_name}': "

                if status_search_results:
                    relevant_url = None
                    for res in status_search_results:
                        if 'status' in res.get('link', '').lower() or 'health' in res.get('link', '').lower() or entity_name.replace(' ', '-').lower() in res.get('link', '').lower():
                            relevant_url = res['link']
                            break
                    
                    if relevant_url:
                        self.log(f"Fetching webpage for '{entity_name}' status from: {relevant_url}")
                        webpage_content = await self.fetch_webpage(relevant_url)
                        
                        if webpage_content:
                            if "error" in webpage_content.lower() or "down" in webpage_content.lower() or "issue" in webpage_content.lower() or "unhealthy" in webpage_content.lower():
                                entity_status = "unhealthy/error"
                                error_detected = True
                                report_message += f"ERROR/UNEXPECTED BEHAVIOR DETECTED on {relevant_url}. Snippet: {webpage_content[:200]}..."
                            else:
                                entity_status = "healthy"
                                report_message += f"Appears healthy based on {relevant_url}. Snippet: {webpage_content[:200]}..."
                        else:
                            entity_status = "fetch_failed"
                            report_message += f"Failed to fetch content from {relevant_url}. This might indicate an issue or an unreachable status page."
                    else:
                        entity_status = "no_direct_status_page_found"
                        report_message += f"No direct status page found in search results for '{entity_name}'. Further investigation might be needed."
                else:
                    entity_status = "no_search_results"
                    report_message += f"No relevant search results for '{entity_name}' status were found. Cannot determine health."
                
                entity['last_status'] = entity_status
                monitoring_results.append({
                    'entity': entity_name,
                    'status': entity_status,
                    'error_detected': error_detected,
                    'report': report_message
                })
                self.log(report_message)
                if error_detected:
                    self.log(f"!!! ALERT !!! Detected an issue with '{entity_name}'. Details: {report_message}")

            # Phase 3: Reporting identified errors or unexpected behavior
            final_report = {
                "agent_name": self.name,
                "timestamp": timestamp,
                "monitoring_summary": []
            }

            for result in monitoring_results:
                final_report["monitoring_summary"].append(result)
                if result['error_detected']:
                    self.log(f"Final Report Highlight (ERROR): {result['report']}")
            
            self.log(f"Agent '{self.name}' completed run. Full report: {json.dumps(final_report, indent=2)}")

            return final_report

        except Exception as e:
            self.log(f"Error during SystemEntityMonitorAgent run: {e}\n{traceback.format_exc()}")
            return {"status": "error", "message": str(e), "timestamp": datetime.datetime.now().isoformat()}

    def _extract_entity_from_search_result(self, search_result: dict) -> str:
        try:
            title = search_result.get('title', '')
            if "NEXUM PRO component" in title:
                parts = title.split("NEXUM PRO component")
                if len(parts) > 1:
                    return parts[1].strip().split(' ')[0].strip()
            elif "service" in title.lower() and "health" in title.lower():
                parts = title.lower().split(" health")
                return parts[0].strip().title() 

            words = title.split()
            if len(words) > 1 and words[0].istitle() and words[1].istitle():
                return " ".join(words[:2])
            
            return None
        except Exception as e:
            self.log(f"Error extracting entity from search result: {e} - {search_result.get('title')}")
            return None