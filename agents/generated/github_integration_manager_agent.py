import os
import subprocess
import shutil
from core.base_agent import BaseAgent

class GithubIntegrationManagerAgent(BaseAgent):
    def __init__(self):
        try:
            super().__init__(
                name="github_integration_manager",
                goal="Automate and manage external Git operations and repositories, push code and updates directly and in real-time to GitHub, and synchronize changes with the system environment.",
                tools=['search_web', 'fetch_webpage'],
                triggers=['every_hour']
            )
            self.github_token = os.getenv("GITHUB_TOKEN")
            self.repo_url = os.getenv("GITHUB_REPO_URL")
            self.local_path = os.getenv("LOCAL_REPO_PATH", "./managed_git_repo")
            self.log("GithubIntegrationManagerAgent initialized successfully.")
        except Exception as e:
            if hasattr(self, 'log'):
                self.log(f"Error initializing agent: {str(e)}", level="error")
            else:
                print(f"Error initializing agent: {str(e)}")

    def run(self):
        try:
            self.log("Starting GitHub integration execution cycle...")
            if not self._check_git_requirements():
                self.log("Git requirements check failed. Execution halted.", level="error")
                return
            
            self._clone_or_pull_repo()
            self._sync_changes()
            self._add_commit_push()
            self.log("GitHub integration execution cycle completed successfully.")
        except Exception as e:
            self.log(f"Error in run execution: {str(e)}", level="error")

    def _check_git_requirements(self) -> bool:
        try:
            result = subprocess.run(["git", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                self.log("Git is not installed or not in system PATH.", level="error")
                return False
            
            if not self.repo_url:
                self.log("GITHUB_REPO_URL environment variable is not set.", level="error")
                return False
                
            return True
        except Exception as e:
            self.log(f"Error checking git requirements: {str(e)}", level="error")
            return False

    def _clone_or_pull_repo(self):
        try:
            authenticated_url = self.repo_url
            if self.github_token and "github.com" in self.repo_url and not self.repo_url.startswith("git@"):
                authenticated_url = self.repo_url.replace("https://", f"https://oauth2:{self.github_token}@")

            if not os.path.exists(self.local_path):
                self.log(f"Cloning repository to {self.local_path}...")
                result = subprocess.run(["git", "clone", authenticated_url, self.local_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if result.returncode == 0:
                    self.log("Repository cloned successfully.")
                else:
                    self.log(f"Failed to clone repository: {result.stderr}", level="error")
            else:
                self.log("Repository directory exists. Pulling latest changes...")
                result = subprocess.run(["git", "-C", self.local_path, "pull"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if result.returncode == 0:
                    self.log("Repository updated successfully via git pull.")
                else:
                    self.log(f"Failed to pull latest changes: {result.stderr}", level="error")
        except Exception as e:
            self.log(f"Error during cloning/pulling repository: {str(e)}", level="error")

    def _sync_changes(self):
        try:
            self.log("Synchronizing changes with system environment...")
            workspace_src = os.getenv("SYSTEM_WORKSPACE_PATH", "./workspace")
            if os.path.exists(workspace_src) and os.path.exists(self.local_path):
                for item in os.listdir(workspace_src):
                    if item == ".git":
                        continue
                    s = os.path.join(workspace_src, item)
                    d = os.path.join(self.local_path, item)
                    if os.path.isdir(s):
                        if os.path.exists(d):
                            shutil.rmtree(d)
                        shutil.copytree(s, d)
                    else:
                        shutil.copy2(s, d)
                self.log("System workspace files synchronized to Git repository path.")
            else:
                self.log("Sync skipped: workspace or local path does not exist.")
        except Exception as e:
            self.log(f"Error synchronizing changes with system environment: {str(e)}", level="error")

    def _add_commit_push(self):
        try:
            self.log("Checking for local changes to commit and push...")
            status = subprocess.run(["git", "-C", self.local_path, "status", "--porcelain"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if not status.stdout.strip():
                self.log("No changes detected in the repository. Nothing to push.")
                return

            subprocess.run(["git", "-C", self.local_path, "add", "-A"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            commit_msg = "Auto-update by github_integration_manager agent"
            commit = subprocess.run(["git", "-C", self.local_path, "commit", "-m", commit_msg], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if commit.returncode != 0:
                self.log(f"Failed to commit changes: {commit.stderr}", level="error")
                return
            
            self.log("Pushing changes to GitHub...")
            push = subprocess.run(["git", "-C", self.local_path, "push", "origin", "main"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if push.returncode == 0:
                self.log("Changes successfully pushed to GitHub.")
            else:
                self.log("Push to main failed. Trying master branch...", level="warning")
                push_master = subprocess.run(["git", "-C", self.local_path, "push", "origin", "master"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if push_master.returncode == 0:
                    self.log("Changes successfully pushed to GitHub (master branch).")
                else:
                    self.log(f"Failed to push changes to GitHub: {push_master.stderr}", level="error")
        except Exception as e:
            self.log(f"Error in Git commit and push pipeline: {str(e)}", level="error")