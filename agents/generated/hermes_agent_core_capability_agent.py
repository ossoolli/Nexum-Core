import re
from core.base_agent import BaseAgent

class HermesAgentCoreCapabilityAgent(BaseAgent):
    def __init__(self):
        try:
            super().__init__(
                name="hermes_agent_core_capability",
                description="An autonomous, self-generating agent.",
                goal="Ability to intelligently parse, complete (if necessary), and integrate complex or new function logic provided as high-level programming language code snippets (e.g., Python functions) into existing source files by generating precise and executable modification commands (e.g., advanced `sed` patterns, dedicated code generation/insertion tools, or direct file manipulation logic within a script) as requested for the AI fallback mechanism.",
                tools=['search_web', 'fetch_webpage'],
                triggers=['every_hour']
            )
            self.log("HermesAgentCoreCapabilityAgent initialized successfully.", level="info")
        except Exception as e:
            self.log(f"Error during HermesAgentCoreCapabilityAgent initialization: {e}", level="error")
            raise

    def run(self, code_snippet: str, target_file_content: str, target_file_path: str, language: str = "python") -> str:
        try:
            self.log(f"Agent '{self.name}' received a request to integrate a code snippet.", level="info")
            self.log(f"Snippet preview: {code_snippet[:100]}...", level="debug")
            self.log(f"Target file content preview: {target_file_content[:100]}...", level="debug")

            analysis_output = self._perform_initial_analysis(code_snippet, target_file_content, target_file_path, language)
            self.log(f"Initial analysis performed. Output: {str(analysis_output)[:100]}...", level="debug")

            if analysis_output.get("external_knowledge_needed") and self.tools:
                search_query = analysis_output.get("search_query", f"how to integrate {language} snippet into existing code")
                if 'search_web' in self.tools:
                    self.log(f"Performing web search for: '{search_query}'", level="info")
                    search_results = self.search_web(search_query)
                    self.log(f"Web search completed. Results count: {len(search_results)}", level="debug")
                    if search_results and 'fetch_webpage' in self.tools:
                        first_link = next((r['link'] for r in search_results if 'link' in r), None)
                        if first_link:
                            self.log(f"Fetching webpage: {first_link}", level="debug")
                            webpage_content = self.fetch_webpage(first_link)
                            self.log(f"Fetched webpage content preview: {webpage_content[:100]}...", level="debug")
                        else:
                            self.log("No relevant links found in search results to fetch.", level="debug")
                else:
                    self.log("search_web tool not available, skipping web research.", level="warn")
            else:
                self.log("No external knowledge needed or no tools available for research.", level="debug")

            modification_commands = self._generate_integration_commands(
                code_snippet, target_file_content, target_file_path, analysis_output, language
            )

            if not modification_commands:
                self.log("Failed to generate precise modification commands.", level="error")
                return ""

            self.log("Successfully generated modification commands.", level="info")
            return modification_commands

        except Exception as e:
            self.log(f"Error in {self.name} run method: {e}", level="error")
            raise

    def _perform_initial_analysis(self, code_snippet: str, target_file_content: str, target_file_path: str, language: str) -> dict:
        try:
            self.log("Performing initial analysis.", level="debug")
            analysis = {
                "snippet_type": "function_definition",
                "dependencies": [],
                "suggested_insertion_point": "end_of_file_or_class",
                "external_knowledge_needed": True,
                "search_query": f"{language} best practices for integrating {code_snippet.splitlines()[0]}",
                "completeness_check": "needs_imports_or_context"
            }
            self.log("Initial analysis complete.", level="debug")
            return analysis
        except Exception as e:
            self.log(f"Error during initial analysis: {e}", level="error")
            raise

    def _generate_integration_commands(self, code_snippet: str, target_file_content: str, target_file_path: str, analysis: dict, language: str) -> str:
        try:
            self.log("Generating integration commands.", level="debug")
            commands = ""
            if language == "python":
                lines = target_file_content.splitlines()
                last_import_line = -1
                for i, line in enumerate(lines):
                    if re.match(r'^\s*(import|from)\s+', line):
                        last_import_line = i

                if last_import_line != -1:
                    commands = f"""# Python script to insert code into '{target_file_path}'\n"""
                    commands += f"""import re\n"""
                    commands += f"""\n"""
                    commands += f"""target_path = '{target_file_path}'\n"""
                    commands += f"""new_code_to_insert = '''\n{code_snippet}\n'''\n"""
                    commands += f"""\n"""
                    commands += f"""with open(target_path, 'r') as f:\n"""
                    commands += f"""    lines = f.readlines()\n"""
                    commands += f"""\n"""
                    commands += f"""last_import_index = -1\n"""
                    commands += f"""for i, line in enumerate(lines):\n"""
                    commands += f"""    if re.match(r'^\\s*(import|from)\\s+', line):\n"""
                    commands += f"""        last_import_index = i\n"""
                    commands += f"""\n"""
                    commands += f"""if last_import_index != -1:\n"""
                    commands += f"""    lines.insert(last_import_index + 1, '\\n' + new_code_to_insert + '\\n')\n"""
                    commands += f"""else:\n"""
                    commands += f"""    lines.append('\\n' + new_code_to_insert + '\\n')\n"""
                    commands += f"""\n"""
                    commands += f"""with open(target_path, 'w') as f:\n"""
                    commands += f"""    f.writelines(lines)\n"""
                else:
                    commands = f"""# Python script to append code to '{target_file_path}'\n"""
                    commands += f"""target_path = '{target_file_path}'\n"""
                    commands += f"""new_code_to_insert = '''\n{code_snippet}\n'''\n"""
                    commands += f"""with open(target_path, 'a') as f:\n"""
                    commands += f"""    f.write('\\n' + new_code_to_insert + '\\n')\n"""
            else:
                self.log(f"Unsupported language for precise command generation: {language}", level="warn")
                commands = f"# Unable to generate precise modification commands for language: {language}"

            self.log("Integration commands generated.", level="debug")
            return commands
        except Exception as e:
            self.log(f"Error during command generation: {e}", level="error")
            raise