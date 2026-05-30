import os
import json
import base64
import requests
from core.base_agent import BaseAgent

class GithubDeploymentManagerAgent(BaseAgent):
    def __init__(self):
        try:
            name = "github_deployment_manager"
            goal = (
                "Directly and securely connect to GitHub repositories to perform actual "
                "Push, Commit, and file synchronization operations automatically."
            )
            tools = ['search_web', 'fetch_webpage']
            triggers = ['every_hour']

            super().__init__(name=name, goal=goal, tools=tools, triggers=triggers)
            
            # Retrieve Configuration from Environment Variables
            self.github_token = os.getenv("GITHUB_TOKEN")
            self.repository = os.getenv("GITHUB_REPOSITORY")  # Expected Format: "owner/repo"
            self.branch = os.getenv("GITHUB_BRANCH", "main")
            self.local_sync_dir = os.getenv("SYNC_DIR", "./deploy_sync")
            
            self.log("GithubDeploymentManagerAgent initialized successfully.")
        except Exception as e:
            if hasattr(self, 'log'):
                self.log(f"Error during initialization: {str(e)}")
            else:
                print(f"Error during initialization: {str(e)}")

    def get_headers(self):
        try:
            if not self.github_token:
                raise ValueError("Missing GITHUB_TOKEN environment variable.")
            return {
                "Authorization": f"Bearer {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
        except Exception as e:
            self.log(f"Error in get_headers: {str(e)}")
            return None

    def get_file_sha(self, path):
        try:
            headers = self.get_headers()
            if not headers or not self.repository:
                return None
            
            url = f"https://api.github.com/repos/{self.repository}/contents/{path}?ref={self.branch}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json().get("sha")
            return None
        except Exception as e:
            self.log(f"Error in get_file_sha for path '{path}': {str(e)}")
            return None

    def commit_and_push_file(self, path, content, commit_message="Automated sync commit by Agent"):
        try:
            headers = self.get_headers()
            if not headers:
                self.log("Authentication failed. Missing headers.")
                return False
            if not self.repository:
                self.log("Missing GITHUB_REPOSITORY specification.")
                return False

            sha = self.get_file_sha(path)
            url = f"https://api.github.com/repos/{self.repository}/contents/{path}"
            
            # Encode content to base64 as required by GitHub API
            encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            
            payload = {
                "message": commit_message,
                "content": encoded_content,
                "branch": self.branch
            }
            if sha:
                payload["sha"] = sha

            response = requests.put(url, headers=headers, json=payload)
            
            if response.status_code in [200, 201]:
                self.log(f"Successfully deployed: {path}")
                return True
            else:
                self.log(f"Failed deployment of {path}. Status: {response.status_code}. Response: {response.text}")
                return False
        except Exception as e:
            self.log(f"Error in commit_and_push_file for '{path}': {str(e)}")
            return False

    def sync_local_directory(self):
        try:
            if not os.path.exists(self.local_sync_dir):
                self.log(f"Sync directory '{self.local_sync_dir}' does not exist. Creating default directory structure.")
                os.makedirs(self.local_sync_dir, exist_ok=True)
                return

            self.log(f"Initiating repository sync from local directory: '{self.local_sync_dir}'")
            for root, dirs, files in os.walk(self.local_sync_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, self.local_sync_dir).replace('\\', '/')
                    
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        self.log(f"Syncing: {relative_path}")
                        self.commit_and_push_file(
                            path=relative_path, 
                            content=content, 
                            commit_message=f"Sync {relative_path} automatically by GithubDeploymentManagerAgent"
                        )
                    except Exception as file_err:
                        self.log(f"Failed to process local file {full_path}: {str(file_err)}")
        except Exception as e:
            self.log(f"Error in sync_local_directory: {str(e)}")

    def run(self):
        try:
            self.log("Starting GithubDeploymentManagerAgent run loop.")
            
            if not self.github_token or not self.repository:
                self.log("Agent deactivated: Credentials (GITHUB_TOKEN/GITHUB_REPOSITORY) are not configured.")
                return
            
            # Execute active file deployment from workspace synchronization folder
            self.sync_local_directory()
            
            self.log("GithubDeploymentManagerAgent run completed successfully.")
        except Exception as e:
            self.log(f"Error in run method execution: {str(e)}")