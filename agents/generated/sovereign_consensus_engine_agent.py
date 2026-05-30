import json
from core.base_agent import BaseAgent

class SovereignConsensusEngineAgent(BaseAgent):
    """
    وكيل سيادي مستقل مولد تلقائياً للقيام بـ: To facilitate or perform 'Sovereign Scrutiny',
    integrate 'Consensus' decisions from various inputs (e.g., individual votes, system analyses),
    and extract a unified, strict programmatic output based on these decisions for the system to implement.
    This agent, as part of NEXUM PRO, is tasked with monitoring and validating the results of a consensus
    process that has already occurred and extracted a programmatic output externally, rather than
    performing the consensus-building and output extraction process itself within this specific
    execution context.
    """
    def __init__(self):
        try:
            super().__init__(
                name="sovereign_consensus_engine",
                description="To facilitate or perform 'Sovereign Scrutiny', integrate 'Consensus' decisions from various inputs (e.g., individual votes, system analyses), and extract a unified, strict programmatic output based on these decisions for the system to implement. This agent, as part of NEXUM PRO, is tasked with monitoring and validating the results of a consensus process that has already occurred and extracted a programmatic output externally, rather than performing the consensus-building and output extraction process itself within this specific execution context.",
                tools=['search_web', 'fetch_webpage'],
                triggers=['every_hour']
            )
            self.last_known_output_hash = None # To track changes in programmatic output
            self.log("INFO", "SovereignConsensusEngineAgent initialized.")
        except Exception as e:
            # In a real scenario, BaseAgent might handle its own __init__ logging,
            # but for completeness, we wrap here.
            print(f"ERROR: Failed to initialize SovereignConsensusEngineAgent: {e}") 

    async def run(self, *args, **kwargs):
        try:
            self.log("INFO", "Sovereign Consensus Engine Agent: Initiating hourly scrutiny cycle for programmatic output.")
            
            # The agent's role is to monitor and validate existing outputs.
            # It uses its tools to find information related to these outputs.
            search_query = "latest official programmatic output consensus updates"
            self.log("INFO", f"Searching the web for: '{search_query}'")
            
            search_results = await self.call_tool('search_web', query=search_query)
            
            if not search_results:
                self.log("WARNING", "No relevant search results found for recent consensus output updates.")
                return

            potential_output_url = None
            # Prioritize links that explicitly mention "programmatic output" or "unified decision"
            for result in search_results:
                title = result.get('title', '').lower()
                snippet = result.get('snippet', '').lower()
                if "programmatic output" in title or "programmatic output" in snippet or \
                   "unified decision" in title or "unified decision" in snippet:
                    potential_output_url = result['link']
                    self.log("INFO", f"Identified a highly relevant URL for programmatic output: {potential_output_url}")
                    break
            
            if not potential_output_url:
                self.log("INFO", "Could not find a highly relevant link among search results to fetch.")
                # As a fallback, try the first result if no specific one was found
                if search_results:
                    potential_output_url = search_results[0]['link']
                    self.log("INFO", f"Falling back to fetching the top search result: {potential_output_url}")
                else:
                    self.log("INFO", "No search results to fall back on.")
                    return

            self.log("INFO", f"Fetching content from: {potential_output_url}")
            webpage_content = await self.call_tool('fetch_webpage', url=potential_output_url)

            if not webpage_content:
                self.log("ERROR", f"Failed to fetch content from {potential_output_url}. Skipping programmatic output extraction.")
                return

            # Simulate the "integration of Consensus decisions" and "extraction of a unified, strict programmatic output"
            # This method acts as a placeholder for complex parsing and validation logic
            extracted_programmatic_output = self._simulate_output_extraction(webpage_content)

            if extracted_programmatic_output:
                current_output_hash = hash(json.dumps(extracted_programmatic_output, sort_keys=True))
                if current_output_hash != self.last_known_output_hash:
                    self.log("SUCCESS", "Sovereign Scrutiny identified a NEW or UPDATED programmatic output.")
                    self.log("INFO", f"Extracted Programmatic Output:\n{json.dumps(extracted_programmatic_output, indent=2)}")
                    self.last_known_output_hash = current_output_hash
                    # In a real system, this extracted and validated output would then be forwarded
                    # for system implementation, adhering to the "strict programmatic output" requirement.
                    self.log("INFO", "Programmatic output is ready for potential system implementation based on its content.")
                else:
                    self.log("INFO", "Programmatic output remains unchanged since the last scrutiny cycle.")
            else:
                self.log("INFO", "No strict programmatic output could be extracted or validated from the current source.")

            self.log("INFO", "Sovereign Consensus Engine Agent: Scrutiny cycle completed.")

        except Exception as e:
            self.log("ERROR", f"An unexpected error occurred during Sovereign Scrutiny cycle: {e}")

    def _simulate_output_extraction(self, content: str) -> dict | None:
        """
        Simulates the extraction of a unified, strict programmatic output from content.
        This method represents the 'integration' and 'extraction' part of the agent's goal.
        It looks for a JSON structure as a strict programmatic output.
        """
        try:
            self.log("DEBUG", "Attempting simulated programmatic output extraction.")
            
            # A common pattern for strict programmatic output might be a JSON blob.
            # We'll look for markers or attempt to parse portions as JSON.
            
            # Heuristic 1: Look for a specific JSON block marker
            json_start_marker = "<PROGRAMMATIC_OUTPUT_JSON>"
            json_end_marker = "</PROGRAMMATIC_OUTPUT_JSON>"

            if json_start_marker in content and json_end_marker in content:
                start_idx = content.find(json_start_marker) + len(json_start_marker)
                end_idx = content.find(json_end_marker)
                
                if start_idx < end_idx:
                    json_str = content[start_idx:end_idx].strip()
                    try:
                        parsed_json = json.loads(json_str)
                        self.log("INFO", "Successfully extracted programmatic output from JSON block.")
                        return parsed_json
                    except json.JSONDecodeError:
                        self.log("WARNING", "Found a programmatic output JSON block, but content was not valid JSON.")
                        return {"error": "Invalid JSON format in designated block", "raw_content": json_str}

            # Heuristic 2: Look for general JSON-like structures that might represent output
            # This is more complex and prone to errors, but demonstrates the intent.
            # For simplicity, let's assume if it finds a dict-like structure at a certain point.
            # This is a very basic simulation.
            if '{' in content and '}' in content:
                first_brace = content.find('{')
                last_brace = content.rfind('}')
                if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                    potential_json_str = content[first_brace : last_brace + 1]
                    try:
                        parsed_json = json.loads(potential_json_str)
                        self.log("INFO", "Successfully extracted programmatic output from a general JSON-like structure.")
                        return parsed_json
                    except json.JSONDecodeError:
                        self.log("DEBUG", "Could not parse general JSON-like structure. Continuing search.")

            self.log("INFO", "No specific programmatic output structure found in the content.")
            return None
        except Exception as e:
            self.log("ERROR", f"Error during simulated programmatic output extraction: {e}")
            return None