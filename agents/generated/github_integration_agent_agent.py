import os
import sys
import subprocess
import requests
import json
import base64
from datetime import datetime
from typing import Dict, Any, List

from core.base_agent import BaseAgent

class GithubIntegrationAgentAgent(BaseAgent):
    def __init__(self, agent_id: str = "github_integration_agent", configs: Dict[str, Any] = None):
        try:
            super().__init__(agent_id=agent_id, configs=configs)
            self.name = "github_integration_agent"
            self.goals = [
                "Securely connect the system to external GitHub repositories.",
                "Automatically upload and update codebase files.",
                "Manage push and commit operations seamlessly.",
                "Track repository status in real-time."
            ]
            self.tools = ['search_web', 'fetch_webpage']
            self.triggers = ['every_hour']
            
            # Load credentials safely
            self.github_token = os.getenv("GITHUB_TOKEN") or (configs.get("github_token") if configs else None)
            self.repo_owner = os.getenv("GITHUB_OWNER") or (configs.get("repo_owner") if configs else None)
            self.repo_name = os.getenv("GITHUB_REPO") or (configs.get("repo_name") if configs else None)
            self.branch = os.getenv("GITHUB_BRANCH", "main") or (configs.get("branch", "main") if configs else "main")
            self.local_repo_path = os.getenv("LOCAL_REPO_PATH", ".") or (configs.get("local_repo_path", ".") if configs else ".")
            
            self.api_base_url = "https://api.github.com"
            self.log("GithubIntegrationAgentAgent initialized successfully.")
        except Exception as e:
            self.log(f"Error during initialization: {str(e)}", "ERROR")

    def log(self, message: str, level: str = "INFO"):
        try:
            super().log(f"[{level}] {message}")
        except Exception:
            print(f"[{datetime.now().isoformat()}] [{level}] {message}")

    def run(self) -> Dict[str, Any]:
        self.log("Running GithubIntegrationAgentAgent execution cycle...")
        status_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "initiated",
            "actions_performed": []
        }
        
        try:
            if not self._validate_credentials():
                status_report["status"] = "failed"
                status_report["error"] = "Invalid or incomplete GitHub credentials"
                return status_report

            # Retrieve actual remote repository state
            repo_status = self._get_remote_repository_status()
            status_report["actions_performed"].append("checked_remote_status")
            
            # Find local files changed that need synchronization
            modified_files = self._get_modified_files()
            
            if modified_files:
                self.log(f"Detected {len(modified_files)} files modified locally. Starting sync...")
                for file_path in modified_files:
                    success = self._push_file_to_github(file_path)
                    if success:
                        status_report["actions_performed"].append(f"pushed_{file_path}")
                status_report["status"] = "success"
                status_report["message"] = "Synchronization completed successfully."
            else:
                self.log("Repository is already fully synchronized. No action needed.")
                status_report["status"] = "idle"
                status_report["message"] = "No modified files detected."

        except Exception as e:
            self.log(f"Critical execution failure: {str(e)}", "ERROR")
            status_report["status"] = "failed"
            status_report["error"] = str(e)
            
        return status_report

    def _validate_credentials(self) -> bool:
        try:
            if not self.github_token or not self.repo_owner or not self.repo_name:
                self.log("Credentials or repository configurations are missing.", "ERROR")
                return False
            
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            url = f"{self.api_base_url}/repos/{self.repo_owner}/{self.repo_name}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                self.log(f"Credentials validated. Connected to repository: {self.repo_owner}/{self.repo_name}")
                return True
            else:
                self.log(f"Credential validation failed with HTTP Status: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Exception during credential validation: {str(e)}", "ERROR")
            return False

    def _get_remote_repository_status(self) -> Dict[str, Any]:
        try:
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            url = f"{self.api_base_url}/repos/{self.repo_owner}/{self.repo_name}/branches/{self.branch}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Active remote branch: {self.branch}. Latest commit SHA: {data['commit']['sha']}")
                return data
            else:
                self.log(f"Could not retrieve branch status. HTTP {response.status_code}", "WARNING")
                return {}
        except Exception as e:
            self.log(f"Exception fetching remote repository status: {str(e)}", "ERROR")
            return {}

    def _get_modified_files(self) -> List[str]:
        modified_files = []
        try:
            # Check if directory is configured as Git repository locally
            git_dir = os.path.join(self.local_repo_path, ".git")
            if os.path.exists(git_dir):
                self.log("Local Git configuration detected. Scanning via Git CLI...")
                result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=self.local_repo_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )
                if result.stdout.strip():
                    lines = result.stdout.strip().split("\n")
                    for line in lines:
                        parts = line.strip().split(" ", 1)
                        if len(parts) > 1:
                            file_path = parts[1].strip()
                            if not file_path.startswith(".git") and os.path.exists(os.path.join(self.local_repo_path, file_path)):
                                modified_files.append(file_path)
            else:
                self.log("No local git repo found. Checking for files modified in the last hour...")
                for root, _, files in os.walk(self.local_repo_path):
                    if ".git" in root or "__pycache__" in root:
                        continue
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, self.local_repo_path)
                        try:
                            mtime = os.path.getmtime(full_path)
                            if (datetime.now().timestamp() - mtime) < 3600:
                                modified_files.append(rel_path)
                        except OSError:
                            continue
        except Exception as e:
            self.log(f"Exception checking modified files: {str(e)}", "ERROR")
        return modified_files

    def _push_file_to_github(self, relative_file_path: str) -> bool:
        try:
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            full_path = os.path.join(self.local_repo_path, relative_file_path)
            if not os.path.isfile(full_path):
                self.log(f"File not found on local path: {full_path}", "WARNING")
                return False

            with open(full_path, "rb") as f:
                content = base64.b64encode(f.read()).decode("utf-8")

            # Check if file exists on remote branch to acquire file's unique SHA blob
            url = f"{self.api_base_url}/repos/{self.repo_owner}/{self.repo_name}/contents/{relative_file_path}?ref={self.branch}"
            get_resp = requests.get(url, headers=headers)
            
            sha = None
            if get_resp.status_code == 200:
                sha = get_resp.json().get("sha")

            # Create commit payloads safely
            commit_message = f"Auto-sync by github_integration_agent: {relative_file_path} @ {datetime.utcnow().isoformat()}"
            payload = {
                "message": commit_message,
                "content": content,
                "branch": self.branch
            }
            if sha:
                payload["sha"] = sha

            put_url = f"{self.api_base_url}/repos/{self.repo_owner}/{self.repo_name}/contents/{relative_file_path}"
            put_resp = requests.put(put_url, headers=headers, json=payload)
            
            if put_resp.status_code in [200, 201]:
                self.log(f"Synchronized file successfully: {relative_file_path} on branch {self.branch}.")
                return True
            else:
                self.log(f"Failed synchronization for {relative_file_path}. Code: {put_resp.status_code} Response: {put_resp.text}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Exception trying to push file {relative_file_path}: {str(e)}", "ERROR")
            return False