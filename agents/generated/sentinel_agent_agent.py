import logging
from core.base_agent import BaseAgent

class SentinelAgentAgent(BaseAgent):
    """
    وكيل سيادي مستقل مولد تلقائياً لمراقبة وتسجيل والتنبيه المحتمل على أحداث
    العودة إلى الخلف (fallback events) الحرجة في الذكاء الاصطناعي.
    """
    def __init__(self, agent_id: str, config: dict, message_bus):
        try:
            super().__init__(agent_id, config, message_bus)
            self.name = "sentinel_agent"
            self.description = "Autonomous agent for monitoring, logging, and alerting on critical AI fallback events."
            self.tools = ['search_web', 'fetch_webpage']
            self.triggers = ['every_hour']
            self.log(logging.INFO, "Sentinel Agent initialized successfully.")
        except Exception as e:
            # In case self.log is not yet available due to super().__init__ failure,
            # use a direct logger or print as a fallback.
            logging.error(f"Error initializing Sentinel Agent {agent_id}: {e}")
            raise # Re-raise to ensure the system knows initialization failed

    async def run(self):
        """
        يقوم بتشغيل دورة المراقبة الساعية للبحث عن أحداث العودة إلى الخلف الحرجة في الذكاء الاصطناعي.
        """
        try:
            self.log(logging.INFO, "Sentinel Agent: Starting hourly monitoring for AI fallback events.")

            # Use search_web to look for recent AI incident reports or news
            search_query = "recent AI system failures OR AI incident reports OR AI fallback events OR AI service outage"
            self.log(logging.INFO, f"Performing web search for: '{search_query}'")
            
            # Assuming search_web returns a dictionary with a 'results' key containing a list of dicts
            search_results = await self.search_web(query=search_query)

            if search_results and isinstance(search_results, dict) and search_results.get('results'):
                self.log(logging.INFO, f"Found {len(search_results['results'])} potential events from web search.")
                critical_event_detected_flag = False
                
                for result in search_results['results']:
                    title = result.get('title', 'N/A')
                    link = result.get('link', 'N/A')
                    snippet = result.get('snippet', 'N/A')

                    # Simple heuristic: Check for keywords implying criticality in title or snippet
                    critical_keywords = ['failure', 'outage', 'critical', 'downtime', 'fallback', 'incident', 'error', 'malfunction']
                    if any(keyword in title.lower() or keyword in snippet.lower() for keyword in critical_keywords):
                        self.log(logging.CRITICAL, f"CRITICAL AI FALLBACK EVENT DETECTED: Title='{title}', Link='{link}', Snippet='{snippet}'")
                        # Here, an actual alerting mechanism could be triggered, e.g., by publishing a message
                        # await self.publish_message(f"ALERT: Critical AI event: {title}", tags=['alert', 'critical', 'ai_fallback'])
                        critical_event_detected_flag = True
                    else:
                        self.log(logging.DEBUG, f"Monitored AI event (non-critical): Title='{title}', Link='{link}'")
                
                if not critical_event_detected_flag:
                    self.log(logging.INFO, "No critical AI fallback events directly identified from current web search results.")
            else:
                self.log(logging.INFO, "Web search for AI fallback events yielded no relevant results or was empty.")

            self.log(logging.INFO, "Sentinel Agent: Hourly monitoring cycle completed.")

        except Exception as e:
            self.log(logging.ERROR, f"An unexpected error occurred during Sentinel Agent's run: {e}", exc_info=True)