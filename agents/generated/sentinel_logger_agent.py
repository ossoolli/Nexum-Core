from core.base_agent import BaseAgent
import datetime

class SentinelLoggerAgent(BaseAgent):
    def __init__(self):
        try:
            super().__init__(
                name="sentinel_logger",
                description="To establish and manage a specialized logging and monitoring agent ('Sentinel') capable of receiving, processing, and potentially alerting on critical system events, as implied by the user's proposed `log_to_sentinel` function call within the modified Python code. This implies that 'Sentinel' is not just a function within the core system, but a distinct monitoring entity that NEXUM PRO would need to manage or integrate with to fulfill the logging objective.",
                tools=['search_web', 'fetch_webpage'],
                triggers=['every_hour']
            )
            self.log_buffer = []
            self.log("INFO", "SentinelLoggerAgent initialized successfully.")
        except Exception as e:
            self.log("ERROR", f"SentinelLoggerAgent failed to initialize: {e}")

    def run(self):
        try:
            self.log("INFO", f"SentinelLoggerAgent: Starting hourly log processing at {datetime.datetime.now()}.")
            
            # Get a copy of logs currently in buffer and clear the original for new incoming logs
            logs_to_process = self.log_buffer[:] 
            self.log_buffer.clear() 

            if not logs_to_process:
                self.log("INFO", "SentinelLoggerAgent: No new logs to process this hour.")
                return

            processed_count, critical_events = self._process_logs(logs_to_process)
            self.log("INFO", f"SentinelLoggerAgent: Processed {processed_count} logs.")

            if critical_events:
                self.log("WARNING", f"SentinelLoggerAgent: Detected {len(critical_events)} critical events.")
                for event in critical_events:
                    self._alert_on_critical_event(event)
            else:
                self.log("INFO", "SentinelLoggerAgent: No critical events detected.")

            self.log("INFO", "SentinelLoggerAgent: Hourly log processing completed.")
        except Exception as e:
            self.log("ERROR", f"SentinelLoggerAgent: An error occurred during run: {e}")

    def log_to_sentinel(self, log_entry: str):
        """
        Receives a log entry from another part of the system and adds it to the buffer.
        This method acts as the entry point for other system components to log to Sentinel.
        """
        try:
            timestamp = datetime.datetime.now().isoformat()
            full_log_entry = f"[{timestamp}] {log_entry}"
            self.log_buffer.append(full_log_entry)
            self.log("DEBUG", f"SentinelLoggerAgent: Received log: {full_log_entry[:100]}...")
        except Exception as e:
            self.log("ERROR", f"SentinelLoggerAgent: Failed to receive log entry '{log_entry[:50]}...': {e}")

    def _process_logs(self, logs: list) -> (int, list):
        """
        Processes a list of log entries, identifying critical events based on keywords.
        Returns the number of logs processed and a list of identified critical events.
        """
        critical_events = []
        processed_count = 0
        try:
            for log_entry in logs:
                processed_count += 1
                # Simple heuristic: check for keywords like "ERROR", "CRITICAL", "FAILURE", "EXCEPTION"
                # In a real system, this would involve more sophisticated parsing,
                # regex, ML models, or structured log analysis.
                if any(keyword in log_entry.upper() for keyword in ["ERROR", "CRITICAL", "FAILURE", "EXCEPTION", "ALERT"]):
                    critical_events.append(log_entry)
                # Additional processing logic could be added here, e.g.,
                # - Store processed logs in a database
                # - Aggregate metrics
                # - Detect patterns over time
            self.log("DEBUG", f"SentinelLoggerAgent: _process_logs completed for {processed_count} logs.")
            return processed_count, critical_events
        except Exception as e:
            self.log("ERROR", f"SentinelLoggerAgent: Error processing logs: {e}")
            return processed_count, critical_events # Return what was processed so far

    def _alert_on_critical_event(self, event: str):
        """
        Handles alerting for a critical event, leveraging search tools to gather more context or potential solutions.
        """
        try:
            self.log("CRITICAL", f"SentinelLoggerAgent: !!! CRITICAL EVENT DETECTED !!! - {event}")
            
            # Attempt to extract a concise error message for searching
            search_term = event
            if ']' in event: # If timestamp is present, get the message part
                search_term = event.split('] ')[-1] 
            search_query = f"troubleshoot {search_term.split(':')[0]} error" # Focus on the first part of the message

            self.log("INFO", f"SentinelLoggerAgent: Searching for solutions using query: '{search_query}'")
            
            search_results = self.search_web(search_query)
            if search_results:
                self.log("INFO", f"SentinelLoggerAgent: Found search results for '{search_query}':")
                for i, result in enumerate(search_results[:3]): # Log top 3 results
                    self.log("INFO", f"  Result {i+1}: {result.get('title', 'N/A')} - {result.get('link', 'N/A')}")
                    
                    # Optionally, fetch content from the first result for deeper analysis
                    if i == 0 and 'link' in result:
                        try:
                            page_content = self.fetch_webpage(result['link'])
                            self.log("DEBUG", f"SentinelLoggerAgent: Fetched content snippet from {result['link']}: {page_content[:500]}...")
                            # Further analysis of page_content for actionable insights could happen here
                        except Exception as fetch_e:
                            self.log("ERROR", f"SentinelLoggerAgent: Failed to fetch webpage {result['link']}: {fetch_e}")
            else:
                self.log("INFO", f"SentinelLoggerAgent: No relevant search results found for '{search_query}'.")

            # In a real production system, this section would integrate with actual alerting tools
            # (e.g., sending emails, SMS, PagerDuty alerts, creating incident tickets).
            self.log("INFO", "SentinelLoggerAgent: Alerting mechanism (simulated) triggered for critical event.")
        except Exception as e:
            self.log("ERROR", f"SentinelLoggerAgent: An error occurred during critical event alerting for '{event[:100]}...': {e}")