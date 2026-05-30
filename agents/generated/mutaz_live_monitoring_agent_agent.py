from core.base_agent import BaseAgent

class MutazLiveMonitoringAgentAgent(BaseAgent):
    def __init__(self):
        try:
            super().__init__(
                name="mutaz_live_monitoring_agent",
                goal="Monitor the status, identify errors, and report unexpected behavior within the user-specified system or process referred to as 'Mutaz live'. This requires initial configuration to define what 'Mutaz live' entails and how to interface with it.",
                tools=['search_web', 'fetch_webpage'],
                triggers=['every_hour']
            )
            self._mutaz_live_config = None # Placeholder for 'Mutaz live' configuration (e.g., URL, search terms)
            self.log("MutazLiveMonitoringAgentAgent initialized.", level="INFO")
            self._initial_configuration()
        except Exception as e:
            self.log(f"Error during MutazLiveMonitoringAgentAgent initialization: {e}", level="ERROR")

    def _initial_configuration(self):
        """
        Performs initial configuration to define 'Mutaz live'.
        In a real scenario, this might load from a config file,
        prompt the user, or perform an initial search.
        For this autonomous agent, we'll set a default or try to discover.
        """
        try:
            # Example: Assume 'Mutaz live' is a publicly accessible service or has a known status page.
            # This would be configured by the user or an orchestrator system.
            # For demonstration, we'll set a default search query.
            if not self._mutaz_live_config:
                self.log("Mutaz live target not explicitly configured. Attempting to discover via web search.", level="WARNING")
                search_query = "Mutaz live service status"
                search_results = self.search_web(search_query)

                # Attempt to find a suitable URL from search results
                found_url = None
                for result in search_results.get('results', []):
                    if 'url' in result and ('status' in result['title'].lower() or 'monitoring' in result['title'].lower()):
                        found_url = result['url']
                        break
                
                if found_url:
                    self._mutaz_live_config = {'type': 'webpage', 'target': found_url, 'search_terms': ['error', 'down', 'critical', 'issue']}
                    self.log(f"Configured 'Mutaz live' target URL: {found_url}", level="INFO")
                else:
                    self._mutaz_live_config = {'type': 'search_only', 'target': search_query, 'search_terms': ['error', 'down', 'critical', 'issue', 'unstable']}
                    self.log(f"Could not find a specific status page URL. Will rely on general web search for '{search_query}'.", level="WARNING")

            self.log("Initial configuration for 'Mutaz live' completed.", level="INFO")
        except Exception as e:
            self.log(f"Error during _initial_configuration: {e}", level="ERROR")

    def run(self):
        try:
            self.log("Starting Mutaz live monitoring cycle.", level="INFO")

            if not self._mutaz_live_config:
                self.log("Mutaz live configuration missing. Cannot perform monitoring. Attempting re-configuration.", level="ERROR")
                self._initial_configuration()
                if not self._mutaz_live_config:
                    self.log("Re-configuration failed. Aborting monitoring cycle.", level="ERROR")
                    return

            monitoring_type = self._mutaz_live_config.get('type')
            target = self._mutaz_live_config.get('target')
            search_terms = self._mutaz_live_config.get('search_terms', [])

            if monitoring_type == 'webpage' and target:
                self.log(f"Fetching content from Mutaz live status page: {target}", level="INFO")
                page_content = self.fetch_webpage(target)
                if page_content:
                    self._analyze_content(page_content, search_terms)
                else:
                    self.log(f"Failed to fetch webpage content from {target}. This might indicate an issue with Mutaz live or network.", level="ERROR")
                    self.report_unexpected_behavior(f"Failed to access Mutaz live status page at {target}")
            elif monitoring_type == 'search_only' and target:
                self.log(f"Performing general web search for Mutaz live status using query: {target}", level="INFO")
                search_results = self.search_web(target)
                self._analyze_search_results(search_results, search_terms)
            else:
                self.log("Invalid or incomplete Mutaz live configuration. Please verify settings.", level="ERROR")
                self.report_unexpected_behavior("Invalid or incomplete Mutaz live monitoring configuration detected.")

            self.log("Mutaz live monitoring cycle completed.", level="INFO")
        except Exception as e:
            self.log(f"Error during MutazLiveMonitoringAgentAgent run: {e}", level="ERROR")

    def _analyze_content(self, content, error_keywords):
        """Analyzes web page content for error keywords."""
        try:
            found_errors = []
            content_lower = content.lower()
            for keyword in error_keywords:
                if keyword in content_lower:
                    found_errors.append(keyword)
            
            if found_errors:
                self.log(f"Identified potential issues in Mutaz live status page. Keywords found: {', '.join(found_errors)}", level="CRITICAL")
                self.report_unexpected_behavior(f"Mutaz live reported issues. Keywords: {', '.join(found_errors)}")
            else:
                self.log("Mutaz live status page appears healthy.", level="INFO")
        except Exception as e:
            self.log(f"Error during _analyze_content: {e}", level="ERROR")

    def _analyze_search_results(self, search_results, error_keywords):
        """Analyzes web search results for error keywords."""
        try:
            found_errors = []
            for result in search_results.get('results', []):
                title_lower = result.get('title', '').lower()
                snippet_lower = result.get('snippet', '').lower()
                
                for keyword in error_keywords:
                    if keyword in title_lower or keyword in snippet_lower:
                        found_errors.append(f"'{keyword}' in {result.get('url', 'N/A')}")
            
            if found_errors:
                self.log(f"Identified potential issues for Mutaz live via web search. Mentions: {', '.join(found_errors)}", level="CRITICAL")
                self.report_unexpected_behavior(f"Web search indicates potential issues with Mutaz live. Mentions: {', '.join(found_errors)}")
            else:
                self.log("Web search for Mutaz live status returned no immediate red flags.", level="INFO")
        except Exception as e:
            self.log(f"Error during _analyze_search_results: {e}", level="ERROR")

    def report_unexpected_behavior(self, message):
        """
        Simulates reporting unexpected behavior. In a real system, this might
        trigger an alert, send an email, or create a ticket.
        """
        try:
            self.log(f"REPORTING UNEXPECTED BEHAVIOR: {message}", level="ALERT")
            # Placeholder for actual reporting mechanism (e.g., self.send_alert(message))
        except Exception as e:
            self.log(f"Error during report_unexpected_behavior: {e}", level="ERROR")