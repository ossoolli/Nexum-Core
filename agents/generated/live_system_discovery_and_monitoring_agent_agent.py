import asyncio
from core.base_agent import BaseAgent

class LiveSystemDiscoveryAndMonitoringAgentAgent(BaseAgent):
    def __init__(self):
        try:
            super().__init__()
            self.name = "live_system_discovery_and_monitoring_agent"
            self.description = "An autonomous, self-generating agent designed for proactive discovery, onboarding, and continuous monitoring of user-defined live operational systems or processes within the user's ecosystem."
            self.goal = "وكيل سيادي مستقل مولد تلقائياً للقيام بـ: Proactively discover, onboard, and continuously monitor user-defined live operational systems or processes (like 'Mutaz live') within the user's ecosystem, providing real-time status, incident detection, and error reporting without requiring explicit, step-by-step configuration for initial awareness."
            self.tools = ['search_web', 'fetch_webpage']
            self.triggers = ['every_hour']
            
            # Initialize agent-specific memory for storing monitored systems
            if 'monitored_systems' not in self.memory:
                self.memory['monitored_systems'] = {} # {system_name: {'url': '...', 'status': '...', 'last_checked': '...'}}
            
            self.log("LiveSystemDiscoveryAndMonitoringAgentAgent initialized successfully.", level="INFO")
        except Exception as e:
            self.log(f"Error during LiveSystemDiscoveryAndMonitoringAgentAgent initialization: {e}", level="ERROR")

    async def run(self):
        try:
            self.log("LiveSystemDiscoveryAndMonitoringAgentAgent run started.", level="INFO")

            # --- Phase 1: Proactive Discovery ---
            self.log("Phase 1: Initiating proactive discovery of systems.", level="INFO")
            discovery_keywords = ["live operational system", "user services dashboard", "critical system status"]
            potential_targets = []

            for keyword in discovery_keywords:
                self.log(f"Searching web for: '{keyword}'", level="DEBUG")
                search_results = await self.call_tool('search_web', query=f"{keyword} in user's environment")
                
                # Simulate parsing search results for URLs or system names
                if search_results:
                    for result in search_results.get('results', []):
                        if result.get('link') and result.get('title'):
                            potential_targets.append({'name': result['title'], 'url': result['link']})
                    self.log(f"Found {len(search_results.get('results', []))} search results for '{keyword}'.", level="DEBUG")
                else:
                    self.log(f"No significant search results for '{keyword}'.", level="DEBUG")
                
                # Avoid overwhelming search APIs or memory with too many targets
                if len(potential_targets) > 50: 
                    self.log("Reached maximum potential targets for this discovery cycle.", level="WARNING")
                    break

            # Deduplicate potential targets
            unique_potential_targets = {}
            for target in potential_targets:
                unique_potential_targets[target['url']] = target
            potential_targets = list(unique_potential_targets.values())

            self.log(f"Identified {len(potential_targets)} potential targets for onboarding.", level="INFO")

            # --- Phase 2: Onboarding New Systems ---
            self.log("Phase 2: Attempting to onboard new systems.", level="INFO")
            newly_onboarded_count = 0
            for target in potential_targets:
                system_name = target['name']
                system_url = target['url']

                if system_url in self.memory['monitored_systems']:
                    self.log(f"System '{system_name}' (URL: {system_url}) already onboarded. Skipping.", level="DEBUG")
                    continue

                self.log(f"Attempting to onboard system: '{system_name}' at {system_url}", level="INFO")
                try:
                    # Attempt to fetch the webpage to verify accessibility or get initial status
                    webpage_content = await self.call_tool('fetch_webpage', url=system_url)
                    
                    if webpage_content:
                        # Simulate a check for "operational" keywords or API response structure
                        is_operational = "status: operational" in webpage_content.lower() or "healthcheck" in webpage_content.lower()
                        
                        if is_operational:
                            self.memory['monitored_systems'][system_url] = {
                                'name': system_name,
                                'url': system_url,
                                'status': 'operational',
                                'last_checked': self.get_current_timestamp()
                            }
                            self.log(f"Successfully onboarded system: '{system_name}' ({system_url})", level="SUCCESS")
                            newly_onboarded_count += 1
                        else:
                            self.log(f"System '{system_name}' at {system_url} deemed non-operational or irrelevant during onboarding.", level="WARNING")
                    else:
                        self.log(f"Failed to fetch webpage for '{system_name}' at {system_url}. Skipping onboarding.", level="WARNING")
                except Exception as e:
                    self.log(f"Error onboarding '{system_name}' at {system_url}: {e}", level="ERROR")
            
            self.log(f"Onboarded {newly_onboarded_count} new systems.", level="INFO")


            # --- Phase 3: Continuous Monitoring of Onboarded Systems ---
            self.log("Phase 3: Performing continuous monitoring of onboarded systems.", level="INFO")
            if not self.memory['monitored_systems']:
                self.log("No systems are currently onboarded for monitoring.", level="INFO")
            else:
                for url, system_info in list(self.memory['monitored_systems'].items()): # Iterate over a copy to allow modification
                    system_name = system_info['name']
                    self.log(f"Monitoring system: '{system_name}' at {url}", level="DEBUG")

                    try:
                        webpage_content = await self.call_tool('fetch_webpage', url=url)
                        
                        current_status = 'unknown'
                        if webpage_content:
                            # Simulate advanced status parsing and incident detection
                            if "service is unavailable" in webpage_content.lower() or "error 500" in webpage_content.lower():
                                current_status = 'incident'
                                self.log(f"INCIDENT DETECTED for '{system_name}' at {url}: Service appears to be down or erroring.", level="CRITICAL")
                                # In a real scenario, this would trigger an alert/report
                            elif "operational" in webpage_content.lower() or "all systems green" in webpage_content.lower():
                                current_status = 'operational'
                                self.log(f"System '{system_name}' at {url} is currently operational.", level="INFO")
                            else:
                                current_status = 'degraded'
                                self.log(f"System '{system_name}' at {url} status appears degraded or ambiguous.", level="WARNING")
                        else:
                            current_status = 'unreachable'
                            self.log(f"ERROR: System '{system_name}' at {url} is unreachable.", level="ERROR")
                            # In a real scenario, this would also trigger an alert

                        # Update system status in memory
                        self.memory['monitored_systems'][url]['status'] = current_status
                        self.memory['monitored_systems'][url]['last_checked'] = self.get_current_timestamp()

                    except Exception as e:
                        self.log(f"Error monitoring '{system_name}' at {url}: {e}", level="ERROR")
                        self.memory['monitored_systems'][url]['status'] = f'monitoring_error: {e}'
                        self.memory['monitored_systems'][url]['last_checked'] = self.get_current_timestamp()
            
            self.log("LiveSystemDiscoveryAndMonitoringAgentAgent run finished. Current monitored systems:", level="INFO")
            for url, info in self.memory['monitored_systems'].items():
                self.log(f"  - {info['name']} ({url}): Status='{info['status']}', Last Checked='{info['last_checked']}'", level="INFO")

        except Exception as e:
            self.log(f"An unexpected error occurred during LiveSystemDiscoveryAndMonitoringAgentAgent run: {e}", level="CRITICAL")

    def get_current_timestamp(self):
        """Helper to get current time for logging/tracking."""
        import datetime
        return datetime.datetime.now().isoformat()