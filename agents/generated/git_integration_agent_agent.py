import os
import json
import base64
import requests
from typing import Dict, Any, Optional
from core.base_agent import BaseAgent

class GitIntegrationAgentAgent(BaseAgent):
    """
    An autonomous agent that securely connects to GitHub repositories
    to manage branches, commit updates, and push files using the GitHub REST API.
    """
    
    def __init__(self, agent_id: str, name: str = "git_integration_agent", config: Optional[Dict[str, Any]] = None):
        try:
            super().__init__(agent_id=agent_id, name=name, config=config)
            self.tools = ['search_web', 'fetch_webpage']
            self.triggers = ['every_hour']
            
            # Retrieve credentials from environment or config
            self.github_token = os.environ.get("GITHUB_TOKEN") or (config.get("github_token") if config else None)
            self.default_repo = os.environ.get("GITHUB_REPO") or (config.get("default_repo") if config else None)
            self.api_url = "https://api.github.com"
            
            self.log("GitIntegrationAgentAgent successfully initialized.")
        except Exception as e:
            if hasattr(self, 'log'):
                self.log(f"Error initializing GitIntegrationAgentAgent: {str(e)}", level="ERROR")
            else:
                print(f"Error initializing GitIntegrationAgentAgent: {str(e)}")

    def _get_headers(self) -> Dict[str, str]:
        """Generates required headers for GitHub API requests."""
        try:
            if not self.github_token:
                raise ValueError("GitHub Personal Access Token (GITHUB_TOKEN) is missing.")
            return {
                "Authorization": f"Bearer {self.github_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }
        except Exception as e:
            self.log(f"Error generating headers: {str(e)}", level="ERROR")
            raise

    def get_file_sha(self, repo: str, path: str, ref: str = "main") -> Optional[str]:
        """Retrieves the SHA of a file if it exists, necessary for updates."""
        try:
            url = f"{self.api_url}/repos/{repo}/contents/{path}"
            headers = self._get_headers()
            params = {"ref": ref}
            
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response.json().get("sha")
            elif response.status_code == 404:
                return None
            else:
                self.log(f"GitHub API returned code {response.status_code}: {response.text}", level="WARNING")
                return None
        except Exception as e:
            self.log(f"Error retrieving file SHA for {path}: {str(e)}", level="ERROR")
            return None

    def create_or_update_file(self, repo: str, path: str, content: str, commit_message: str, branch: str = "main") -> bool:
        """Commits and pushes a file to the specified repository path."""
        try:
            url = f"{self.api_url}/repos/{repo}/contents/{path}"
            headers = self._get_headers()
            
            # Fetch SHA if the file already exists (required for updates)
            sha = self.get_file_sha(repo, path, branch)
            
            # Base64 encode file content
            encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
            
            data = {
                "message": commit_message,
                "content": encoded_content,
                "branch": branch
            }
            if sha:
                data["sha"] = sha
                
            response = requests.put(url, headers=headers, json=data)
            
            if response.status_code in [200, 201]:
                self.log(f"Successfully committed and pushed '{path}' to branch '{branch}' in repository '{repo}'.")
                return True
            else:
                self.log(f"Failed to commit file. Status code: {response.status_code}. Response: {response.text}", level="ERROR")
                return False
        except Exception as e:
            self.log(f"Exception during create_or_update_file: {str(e)}", level="ERROR")
            return False

    def create_branch(self, repo: str, new_branch_name: str, source_branch: str = "main") -> bool:
        """Creates a new branch from an existing source branch."""
        try:
            headers = self._get_headers()
            
            # Get base branch ref SHA
            ref_url = f"{self.api_url}/repos/{repo}/git/ref/heads/{source_branch}"
            ref_response = requests.get(ref_url, headers=headers)
            
            if ref_response.status_code != 200:
                self.log(f"Could not find branch {source_branch}. Status code: {ref_response.status_code}", level="ERROR")
                return False
                
            sha = ref_response.json().get("object", {}).get("sha")
            
            # Create new reference
            create_ref_url = f"{self.api_url}/repos/{repo}/git/refs"
            payload = {
                "ref": f"refs/heads/{new_branch_name}",
                "sha": sha
            }
            
            response = requests.post(create_ref_url, headers=headers, json=payload)
            if response.status_code == 201:
                self.log(f"Successfully created branch '{new_branch_name}' from '{source_branch}' in '{repo}'.")
                return True
            else:
                self.log(f"Failed to create branch. Status code: {response.status_code}. Response: {response.text}", level="ERROR")
                return False
        except Exception as e:
            self.log(f"Exception during create_branch: {str(e)}", level="ERROR")
            return False

    def search_web(self, query: str) -> str:
        """Tool implementation: Mocked web search for retrieving updates to integrate."""
        try:
            self.log(f"Executing web search for: '{query}'")
            # Simulated search response
            return f"Search Results for '{query}': AI and Git integrations are rapidly standardizing CI/CD pipelines."
        except Exception as e:
            self.log(f"Error executing search_web: {str(e)}", level="ERROR")
            return ""

    def fetch_webpage(self, url: str) -> str:
        """Tool implementation: Fetching page information for updates."""
        try:
            self.log(f"Fetching webpage content from: {url}")
            response = requests.get(url, timeout=10)
            return response.text[:2000] # Safe slice for logging/handling
        except Exception as e:
            self.log(f"Error executing fetch_webpage for {url}: {str(e)}", level="ERROR")
            return ""

    def run(self) -> Dict[str, Any]:
        """
        Main execution loop. Fetches data, processes updates,
        and securely performs genuine commits to the target GitHub repository.
        """
        try:
            self.log("Starting GitIntegrationAgentAgent execution workflow.")
            
            if not self.github_token or not self.default_repo:
                self.log("Missing configuration: 'GITHUB_TOKEN' and 'GITHUB_REPO' are required for operation.", level="ERROR")
                return {"status": "error", "message": "Credentials/Repository missing"}

            # Phase 1: Retrieve context/information using tools
            search_query = "latest Python repository automated workflows 2024"
            search_context = self.search_web(search_query)
            
            # Phase 2: Formulate dynamic content to save
            report_content = (
                f"# Git Integration Agent Sync Report\n\n"
                f"**Agent Name:** {self.name}\n"
                f"**Trigger:** Hourly Synchronizer\n\n"
                f"### Collected Information Context:\n"
                f"{search_context}\n\n"
                f"--- \n*Generated automatically by sovereign GitIntegrationAgentAgent.*"
            )
            
            # Phase 3: Perform secure commits using GitHub REST API
            target_file_path = "reports/agent_sync_report.md"
            target_branch = "main"
            
            self.log(f"Attempting to commit update directly to GitHub target: {target_file_path}")
            success = self.create_or_update_file(
                repo=self.default_repo,
                path=target_file_path,
                content=report_content,
                commit_message="chore: automated sovereign update of sync report [skip ci]",
                branch=target_branch
            )
            
            if success:
                self.log("Sovereign execution and commit completed successfully.")
                return {"status": "success", "file_updated": target_file_path, "branch": target_branch}
            else:
                self.log("Failed to commit sync report to GitHub.", level="ERROR")
                return {"status": "failure", "message": "Commit operation returned false status"}
                
        except Exception as e:
            self.log(f"Execution failed in run(): {str(e)}", level="ERROR")
            return {"status": "error", "exception": str(e)}