import os
import subprocess
import json
import urllib.request
from urllib.request import Request
from core.base_agent import BaseAgent

class GithubConnectorAgentAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        try:
            super().__init__(*args, **kwargs)
            self.name = "github_connector_agent"
            self.tools = ['search_web', 'fetch_webpage']
            self.triggers = ['every_hour']
            self.github_token = os.getenv("GITHUB_TOKEN")
            self.github_user = os.getenv("GITHUB_USER")
            self.github_repo = os.getenv("GITHUB_REPO")  # Format: "owner/repo"
            self.local_repo_path = os.getenv("LOCAL_REPO_PATH", "./cloned_repo")
            self.log("GithubConnectorAgentAgent initialized successfully.")
        except Exception as e:
            if hasattr(self, 'log'):
                self.log(f"Error in __init__: {str(e)}")
            else:
                print(f"Error in __init__: {str(e)}")

    def run(self, *args, **kwargs):
        try:
            self.log("Starting run cycle for GithubConnectorAgentAgent...")
            if not self.github_token or not self.github_repo:
                self.log("Missing GITHUB_TOKEN or GITHUB_REPO environment variables. Skipping execution.")
                return False
            
            # Step 1: Authenticate and verify permissions
            auth_success = self._authenticate_github()
            if not auth_success:
                self.log("Authentication failed. Aborting operations.")
                return False

            # Step 2: Manage and Sync Branch
            branch_name = os.getenv("GITHUB_BRANCH", "main")
            sync_success = self._sync_repository(self.github_repo, branch_name, self.local_repo_path)
            
            if sync_success:
                self.log("Repository sync completed successfully.")
                return True
            else:
                self.log("Repository sync failed.")
                return False
        except Exception as e:
            self.log(f"Error in run: {str(e)}")
            return False

    def _authenticate_github(self):
        try:
            self.log("Verifying GitHub credentials and API access...")
            url = f"https://api.github.com/repos/{self.github_repo}"
            req = Request(url)
            req.add_header("Authorization", f"token {self.github_token}")
            req.add_header("Accept", "application/vnd.github.v3+json")
            
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    repo_data = json.loads(response.read().decode())
                    permissions = repo_data.get('permissions', {})
                    if permissions.get('push', False):
                        self.log("Authentication successful. Write/Push permissions verified.")
                        return True
                    else:
                        self.log("Authentication successful, but lack push access to this repository.")
                        return False
            return False
        except Exception as e:
            self.log(f"Error in _authenticate_github: {str(e)}")
            return False

    def _execute_git_command(self, command, cwd=None):
        try:
            self.log(f"Executing Git command: {' '.join(command)}")
            result = subprocess.run(
                command,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            self.log(f"Git command failed: {e.stderr}")
            return False, e.stderr
        except Exception as e:
            self.log(f"Error in _execute_git_command: {str(e)}")
            return False, str(e)

    def _sync_repository(self, repo, branch, local_path):
        try:
            self.log(f"Synchronizing local path {local_path} with remote {repo} on branch {branch}")
            authenticated_url = f"https://{self.github_user}:{self.github_token}@github.com/{repo}.git"
            
            # Create local folder if not exists
            if not os.path.exists(local_path):
                self.log(f"Cloning repository {repo} to {local_path}...")
                os.makedirs(local_path, exist_ok=True)
                success, output = self._execute_git_command(
                    ["git", "clone", "-b", branch, authenticated_url, local_path]
                )
                if not success:
                    return False
            else:
                self.log("Repository already exists locally. Fetching and merging updates...")
                success, _ = self._execute_git_command(["git", "fetch", "origin"], cwd=local_path)
                if not success:
                    return False
                
                success, _ = self._execute_git_command(["git", "checkout", branch], cwd=local_path)
                if not success:
                    # Create the branch locally if it only exists on remote
                    self._execute_git_command(["git", "checkout", "-b", branch, f"origin/{branch}"], cwd=local_path)
                
                success, _ = self._execute_git_command(["git", "pull", "origin", branch], cwd=local_path)
                if not success:
                    return False

            # Check for local modifications to commit/push
            success, status_out = self._execute_git_command(["git", "status", "--porcelain"], cwd=local_path)
            if success and status_out.strip():
                self.log("Local changes detected. Committing and pushing...")
                self._execute_git_command(["git", "add", "."], cwd=local_path)
                self._execute_git_command(
                    ["git", "-c", "user.name='AI Agent'", "-c", "user.email='agent@ai-connector.internal'", "commit", "-m", "Auto-sync update from GithubConnectorAgentAgent"], 
                    cwd=local_path
                )
                push_success, _ = self._execute_git_command(["git", "push", "origin", branch], cwd=local_path)
                return push_success
            
            self.log("No local changes to commit or push.")
            return True
        except Exception as e:
            self.log(f"Error in _sync_repository: {str(e)}")
            return False

    def search_web(self, query):
        try:
            self.log(f"Searching web for query: {query}")
            # Placeholder for tool execution logic
            return {"results": f"Simulated search results for: {query}"}
        except Exception as e:
            self.log(f"Error in search_web: {str(e)}")
            return None

    def fetch_webpage(self, url):
        try:
            self.log(f"Fetching webpage content from: {url}")
            # Placeholder for tool execution logic
            return {"content": f"Simulated content retrieved from: {url}"}
        except Exception as e:
            self.log(f"Error in fetch_webpage: {str(e)}")
            return None