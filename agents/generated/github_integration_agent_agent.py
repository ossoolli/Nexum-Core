import os
import base64
import requests
from typing import Dict, Any, Optional
from core.base_agent import BaseAgent

class GithubIntegrationAgentAgent(BaseAgent):
    def __init__(self):
        try:
            super().__init__(
                name="github_integration_agent",
                tools=['search_web', 'fetch_webpage'],
                triggers=['every_hour']
            )
            self.github_token = os.getenv("GITHUB_TOKEN")
            self.repo = os.getenv("GITHUB_REPO")  # Format: "owner/repo"
            self.branch = os.getenv("GITHUB_BRANCH", "main")
            self.api_url = "https://api.github.com"
            self.log("GithubIntegrationAgentAgent successfully initialized.")
        except Exception as e:
            if hasattr(self, 'log'):
                self.log(f"Error during initialization: {str(e)}")
            else:
                print(f"Error initializing GithubIntegrationAgentAgent: {str(e)}")

    def _get_headers(self) -> Dict[str, str]:
        try:
            return {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
        except Exception as e:
            self.log(f"Error generating authorization headers: {str(e)}")
            return {}

    def get_file_sha(self, path: str, branch: str) -> Optional[str]:
        try:
            url = f"{self.api_url}/repos/{self.repo}/contents/{path}?ref={branch}"
            response = requests.get(url, headers=self._get_headers())
            if response.status_code == 200:
                return response.json().get("sha")
            return None
        except Exception as e:
            self.log(f"Error fetching file SHA for target path '{path}': {str(e)}")
            return None

    def push_file(self, path: str, content: str, commit_message: str, branch: Optional[str] = None) -> bool:
        try:
            target_branch = branch or self.branch
            if not self.github_token or not self.repo:
                self.log("Error: GITHUB_TOKEN or GITHUB_REPO credentials not provided in environment variables.")
                return False

            sha = self.get_file_sha(path, target_branch)
            url = f"{self.api_url}/repos/{self.repo}/contents/{path}"
            
            encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            
            payload = {
                "message": commit_message,
                "content": encoded_content,
                "branch": target_branch
            }
            if sha:
                payload["sha"] = sha

            response = requests.put(url, headers=self._get_headers(), json=payload)
            
            if response.status_code in [200, 201]:
                self.log(f"Successfully committed and pushed file '{path}' to branch '{target_branch}'.")
                return True
            else:
                self.log(f"Failed to push file via API. Status: {response.status_code}, Error: {response.text}")
                return False
        except Exception as e:
            self.log(f"Critical error during file push operations: {str(e)}")
            return False

    def create_branch(self, new_branch: str, parent_branch: str = "main") -> bool:
        try:
            if not self.github_token or not self.repo:
                self.log("Error: Missing credentials for branch operations.")
                return False

            ref_url = f"{self.api_url}/repos/{self.repo}/git/ref/heads/{parent_branch}"
            ref_response = requests.get(ref_url, headers=self._get_headers())
            if ref_response.status_code != 200:
                self.log(f"Failed to retrieve parent branch reference: {ref_response.text}")
                return False
            
            sha = ref_response.json().get("object", {}).get("sha")
            if not sha:
                self.log("Unable to extract reference SHA for parent branch.")
                return False

            create_ref_url = f"{self.api_url}/repos/{self.repo}/git/refs"
            payload = {
                "ref": f"refs/heads/{new_branch}",
                "sha": sha
            }
            response = requests.post(create_ref_url, headers=self._get_headers(), json=payload)
            if response.status_code == 201:
                self.log(f"Successfully generated new branch '{new_branch}' from parent '{parent_branch}'.")
                return True
            else:
                self.log(f"Failed to create new branch reference. Error: {response.text}")
                return False
        except Exception as e:
            self.log(f"Exception triggered during branch creation cycle: {str(e)}")
            return False

    def run(self) -> Dict[str, Any]:
        try:
            self.log("Activating run cycle for autonomous repository integration.")
            
            if not self.github_token or not self.repo:
                self.log("Configuration dynamic check failed: Missing GITHUB_TOKEN or GITHUB_REPO.")
                return {
                    "status": "error",
                    "message": "Authentication variables absent. Action aborted."
                }

            test_file_path = "integration_heartbeat.txt"
            test_content = f"Autonomously generated log by GithubIntegrationAgentAgent.\nStatus: Active\nTarget Repo: {self.repo}\nTarget Branch: {self.branch}"
            commit_message = "chore: automated agent sync and heartbeat validation [skip ci]"

            push_success = self.push_file(
                path=test_file_path,
                content=test_content,
                commit_message=commit_message,
                branch=self.branch
            )

            if push_success:
                return {
                    "status": "success",
                    "message": f"Successfully performed heartbeat write to {self.repo} on branch {self.branch}."
                }
            else:
                return {
                    "status": "failure",
                    "message": "Repository write cycle failed. Review internal error logs."
                }
        except Exception as e:
            self.log(f"Execution run loop failure: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }