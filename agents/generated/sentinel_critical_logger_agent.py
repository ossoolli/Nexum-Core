import datetime
import requests
from bs4 import BeautifulSoup
from core.base_agent import BaseAgent

class SentinelCriticalLoggerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="sentinel_critical_logger",
            description="An autonomous AI agent designed to monitor and log critical system failures and security alerts to a dedicated sentinel system.",
            goal="Monitor and log critical system failures and security alerts (e.g., primary AI failure, security breaches) to a dedicated, secure, and potentially external 'sentinel' system, beyond standard logging. This implies a specialized agent or integration for robust critical event management and alerting.",
            tools=['search_web', 'fetch_webpage'],
            triggers=['every_hour']
        )
        self.sentinel_api_endpoint = "https://api.example.com/sentinel_logs"
        self.sentinel_api_key = "YOUR_SENTINEL_API_KEY"

    def _send_to_sentinel_system(self, event_data: dict):
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.sentinel_api_key}"
            }
            response = requests.post(self.sentinel_api_endpoint, json=event_data, headers=headers, timeout=10)
            response.raise_for_status()
            self.log(f"Successfully sent event to sentinel system: {response.status_code}")
            return True
        except requests.exceptions.RequestException as e:
            self.log(f"ERROR: Failed to send event to sentinel system: {e}", level="error")
            return False
        except Exception as e:
            self.log(f"ERROR: An unexpected error occurred while sending to sentinel: {e}", level="error")
            return False

    def _process_web_content(self, html_content: str, source: str) -> list:
        critical_keywords = ["outage", "failure", "breach", "compromise", "down", "critical alert", "security incident"]
        found_events = []
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            text_content = soup.get_text()
            searchable_text = text_content[:5000].lower()

            for keyword in critical_keywords:
                if keyword in searchable_text:
                    event_description = f"Potential critical event detected from {source}: keyword '{keyword}' found."
                    found_events.append({
                        "timestamp": datetime.datetime.now().isoformat(),
                        "severity": "CRITICAL",
                        "source": source,
                        "description": event_description,
                        "raw_content_snippet": text_content[:1000]
                    })
            return found_events
        except Exception as e:
            self.log(f"ERROR: Failed to process web content from {source}: {e}", level="error")
            return []

    def run(self):
        self.log("Sentinel Critical Logger Agent initiated hourly run.")
        critical_events_found = []

        try:
            search_query = "recent major system outages OR security breaches OR AI critical failure OR global internet issues"
            search_results = self.search_web(search_query)
            self.log(f"Performed web search for critical events. Found {len(search_results)} results.")

            for i, result in enumerate(search_results[:5]):
                try:
                    self.log(f"Fetching content from search result ({i+1}/{len(search_results)}): {result['link']}")
                    webpage_content = self.fetch_webpage(result['link'])
                    if webpage_content:
                        events_from_page = self._process_web_content(webpage_content, f"Web Search: {result['title']} ({result['link']})")
                        critical_events_found.extend(events_from_page)
                except Exception as e:
                    self.log(f"WARNING: Could not process search result link '{result['link']}': {e}", level="warning")

        except Exception as e:
            self.log(f"ERROR: Failed during web search phase: {e}", level="error")

        try:
            known_status_pages = [
                "https://status.openai.com/",
                "https://status.cloud.google.com/",
                "https://www.cisa.gov/news-events/cybersecurity-advisories",
            ]
            for url in known_status_pages:
                try:
                    self.log(f"Fetching content from known status page: {url}")
                    page_content = self.fetch_webpage(url)
                    if page_content:
                        events_from_page = self._process_web_content(page_content, f"Known Status Page: {url}")
                        critical_events_found.extend(events_from_page)
                except Exception as e:
                    self.log(f"WARNING: Could not fetch or process known status page '{url}': {e}", level="warning")
        except Exception as e:
            self.log(f"ERROR: Failed during known status pages monitoring phase: {e}", level="error")

        if critical_events_found:
            self.log(f"Detected {len(critical_events_found)} potential critical events. Sending to sentinel system.")
            for event in critical_events_found:
                self._send_to_sentinel_system(event)
        else:
            self.log("No critical events detected in this run.")

        self.log("Sentinel Critical Logger Agent hourly run completed.")