import os
import subprocess
import urllib.request
import urllib.parse
import json
from datetime import datetime
from core.base_agent import BaseAgent

class GithubSyncManagerAgent(BaseAgent):
    def __init__(self):
        try:
            super().__init__(
                name="github_sync_manager",
                tools=['search_web', 'fetch_webpage'],
                triggers=['every_hour']
            )
            self.github_token = os.getenv("GITHUB_TOKEN")
            self.github_user = os.getenv("GITHUB_USER")
            self.github_repo = os.getenv("GITHUB_REPO")  # Format: "owner/repo"
            self.local_repo_path = os.getenv("LOCAL_REPO_PATH", "/app/workspace")
            self.branch = os.getenv("GITHUB_BRANCH", "main")
            self.git_user_name = os.getenv("GIT_USER_NAME", "Github Sync Manager Agent")
            self.git_user_email = os.getenv("GIT_USER_EMAIL", "agent@sync-manager.local")
            
            self.log("GithubSyncManagerAgent initialized successfully.")
        except Exception as e:
            if hasattr(self, 'log'):
                self.log(f"Error initializing GithubSyncManagerAgent: {str(e)}")
            else:
                print(f"Error initializing GithubSyncManagerAgent: {str(e)}")

    def run(self):
        try:
            self.log("Starting Github synchronization process...")
            
            if not self.github_token or not self.github_repo or not self.github_user:
                self.log("Error: Missing required environment variables: GITHUB_TOKEN, GITHUB_USER, or GITHUB_REPO.")
                return {"status": "error", "message": "Missing credentials"}

            if not os.path.exists(self.local_repo_path):
                self.log(f"Local repository path {self.local_repo_path} does not exist. Creating it.")
                os.makedirs(self.local_repo_path, exist_ok=True)

            self._configure_git_globals()
            self._initialize_or_verify_repo()
            sync_result = self._sync_repository()
            
            self.log(f"Synchronization flow finished with status: {sync_result['status']}")
            return sync_result
        except Exception as e:
            self.log(f"Error during runtime: {str(e)}")
            return {"status": "error", "message": str(e)}

    def _run_command(self, command, cwd=None):
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.local_repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            return {"success": True, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {' '.join(command)}. Error: {e.stderr.strip()}")
            return {"success": False, "stdout": e.stdout.strip(), "stderr": e.stderr.strip()}
        except Exception as e:
            self.log(f"Exception running command {' '.join(command)}: {str(e)}")
            return {"success": False, "stdout": "", "stderr": str(e)}

    def _configure_git_globals(self):
        try:
            self.log("Configuring global Git credentials...")
            self._run_command(["git", "config", "--global", "user.name", self.git_user_name])
            self._run_command(["git", "config", "--global", "user.email", self.git_user_email])
            # Set safe directory to bypass permission limitations in containers
            self._run_command(["git", "config", "--global", "--add", "safe.directory", self.local_repo_path])
        except Exception as e:
            self.log(f"Failed to configure git globals: {str(e)}")

    def _initialize_or_verify_repo(self):
        try:
            git_dir = os.path.join(self.local_repo_path, ".git")
            if not os.path.exists(git_dir):
                self.log("Initializing new local Git repository...")
                self._run_command(["git", "init"])
                
                # Construct remote URL with token authentication securely
                remote_url = f"https://{self.github_user}:{self.github_token}@github.com/{self.github_repo}.git"
                self._run_command(["git", "remote", "add", "origin", remote_url])
                
                # Check if remote repository has content by fetching
                fetch_res = self._run_command(["git", "fetch", "origin"])
                if fetch_res["success"]:
                    self._run_command(["git", "checkout", "-b", self.branch])
                    self._run_command(["git", "pull", "origin", self.branch])
            else:
                self.log("Existing Git repository verified locally.")
                # Update remote URL to ensure token is valid and current
                remote_url = f"https://{self.github_user}:{self.github_token}@github.com/{self.github_repo}.git"
                self._run_command(["git", "remote", "set-url", "origin", remote_url])
        except Exception as e:
            self.log(f"Error verifying/initializing repository: {str(e)}")

    def _sync_repository(self):
        try:
            self.log("Checking repository status...")
            status_res = self._run_command(["git", "status", "--porcelain"])
            
            if not status_res["success"]:
                return {"status": "error", "message": "Failed to get repository status"}

            if not status_res["stdout"]:
                self.log("No changes detected. Local workspace is up to date.")
                return {"status": "success", "message": "No changes to sync"}

            self.log("Changes detected. Preparing to add, commit, and push updates...")
            
            # Stage all changes
            add_res = self._run_command(["git", "add", "-A"])
            if not add_res["success"]:
                return {"status": "error", "message": "Failed to stage changes"}

            # Create commit message with metadata
            commit_msg = f"Automated sync by GithubSyncManagerAgent - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            commit_res = self._run_command(["git", "commit", "-m", commit_msg])
            if not commit_res["success"]:
                return {"status": "error", "message": "Failed to commit changes"}

            # Push changes
            self.log(f"Pushing updates to branch: {self.branch}...")
            push_res = self._run_command(["git", "push", "origin", self.branch])
            if not push_res["success"]:
                # Try setting upstream branch if failure occurred
                self.log("Push failed, attempting push with upstream tracking...")
                push_res = self._run_command(["git", "push", "--set-upstream", "origin", self.branch])
                if not push_res["success"]:
                    return {"status": "error", "message": "Failed to push updates to remote repository"}

            self.log("Successfully synchronized local updates to GitHub repository.")
            return {"status": "success", "message": "Repository synchronized successfully"}
            
        except Exception as e:
            self.log(f"Error during repository sync: {str(e)}")
            return {"status": "error", "message": str(e)}

    def search_web(self, query):
        try:
            self.log(f"Searching web for query: {query}")
            # Mock or basic standard search API request representation
            api_url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json"
            req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                related_topics = data.get('RelatedTopics', [])
                results = []
                for topic in related_topics[:3]:
                    if 'Text' in topic and 'FirstURL' in topic:
                        results.append({"title": topic['Text'], "url": topic['FirstURL']})
                return {"results": results}
        except Exception as e:
            self.log(f"Search failed: {str(e)}")
            return {"error": str(e)}

    def fetch_webpage(self, url):
        try:
            self.log(f"Fetching webpage content from: {url}")
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8', errors='ignore')
                # Return top 2000 characters of page source as plain-text proxy
                return {"content": html[:2000]}
        except Exception as e:
            self.log(f"Failed to fetch webpage: {str(e)}")
            return {"error": str(e)}