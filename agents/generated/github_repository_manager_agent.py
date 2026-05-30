import os
import subprocess
import shutil
import json
from datetime import datetime
from core.base_agent import BaseAgent

class GithubRepositoryManagerAgent(BaseAgent):
    def __init__(self):
        try:
            super().__init__(
                name="github_repository_manager",
                tools=['search_web', 'fetch_webpage'],
                triggers=['every_hour']
            )
            self.github_token = os.getenv("GITHUB_TOKEN")
            self.repo_owner = os.getenv("GITHUB_OWNER")
            self.repo_name = os.getenv("GITHUB_REPO")
            self.working_dir = os.getenv("GITHUB_WORKING_DIR", "/tmp/github_manager")
            self.log("GithubRepositoryManagerAgent initialized successfully.")
        except Exception as e:
            print(f"Error in GithubRepositoryManagerAgent.__init__: {e}")

    def run(self):
        try:
            self.log("Starting GitHub Repository Manager Agent execution cycle...")
            
            if not self._validate_credentials():
                self.log("Validation failed. Missing required environment configuration.")
                return

            # Construct safe authenticated URL
            repo_url = f"https://{self.github_token}@github.com/{self.repo_owner}/{self.repo_name}.git"
            local_path = os.path.join(self.working_dir, self.repo_name)

            # Pull or Clone repository safely
            self._clone_or_pull(repo_url, local_path)

            # Handle branch creation/checkout
            branch_name = "agent/autonomous-status-update"
            self._create_and_checkout_branch(local_path, branch_name)

            # Execute programmatic and safe repository updates
            has_updates = self._perform_safe_file_update(local_path)

            if has_updates:
                commit_message = f"chore: sovereign status update by AI Agent - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
                self._commit_and_push(local_path, branch_name, commit_message)
                self.log("Autonomous git execution cycle finished successfully.")
            else:
                self.log("No updates to commit during this cycle.")

        except Exception as e:
            self.log(f"Error in GithubRepositoryManagerAgent.run: {e}")

    def _validate_credentials(self):
        try:
            if not self.github_token:
                self.log("Error: GITHUB_TOKEN environment variable is missing.")
                return False
            if not self.repo_owner:
                self.log("Error: GITHUB_OWNER environment variable is missing.")
                return False
            if not self.repo_name:
                self.log("Error: GITHUB_REPO environment variable is missing.")
                return False
            return True
        except Exception as e:
            self.log(f"Error in GithubRepositoryManagerAgent._validate_credentials: {e}")
            return False

    def _clone_or_pull(self, repo_url, local_path):
        try:
            if os.path.exists(local_path):
                self.log(f"Repository directory already exists. Fetching latest remote state...")
                subprocess.run(["git", "-C", local_path, "checkout", "main"], check=True, capture_output=True)
                subprocess.run(["git", "-C", local_path, "pull"], check=True, capture_output=True)
            else:
                self.log(f"Cloning repository {self.repo_owner}/{self.repo_name} to local path: {local_path}")
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                subprocess.run(["git", "clone", repo_url, local_path], check=True, capture_output=True)
        except Exception as e:
            self.log(f"Error in GithubRepositoryManagerAgent._clone_or_pull: {e}")

    def _create_and_checkout_branch(self, local_path, branch_name):
        try:
            self.log(f"Checking out autonomous workspace branch: {branch_name}")
            subprocess.run(["git", "-C", local_path, "fetch", "origin"], check=True, capture_output=True)
            
            # Try to switch to existing branch locally
            result = subprocess.run(["git", "-C", local_path, "checkout", branch_name], capture_output=True, text=True)
            if result.returncode != 0:
                # Branch does not exist locally; create it from main
                self.log(f"Branch '{branch_name}' not found locally. Creating new branch...")
                subprocess.run(["git", "-C", local_path, "checkout", "-b", branch_name], check=True, capture_output=True)
            else:
                # Merge main safely to stay up to date
                subprocess.run(["git", "-C", local_path, "merge", "origin/main"], check=True, capture_output=True)
        except Exception as e:
            self.log(f"Error in GithubRepositoryManagerAgent._create_and_checkout_branch: {e}")

    def _perform_safe_file_update(self, local_path):
        try:
            self.log("Generating safe heartbeat telemetry updates...")
            telemetry_file_path = os.path.join(local_path, "agent_telemetry.json")
            
            # Format update payload
            telemetry_payload = {
                "agent_id": "github_repository_manager",
                "last_active_utc": datetime.utcnow().isoformat() + "Z",
                "status": "online",
                "capabilities": {
                    "branch_management": True,
                    "safe_commit_push": True
                }
            }
            
            with open(telemetry_file_path, "w") as f:
                json.dump(telemetry_payload, f, indent=4)
                
            self.log(f"Successfully updated telemetry details in {telemetry_file_path}")
            return True
        except Exception as e:
            self.log(f"Error in GithubRepositoryManagerAgent._perform_safe_file_update: {e}")
            return False

    def _commit_and_push(self, local_path, branch_name, commit_message):
        try:
            self.log("Staging repository file changes...")
            subprocess.run(["git", "-C", local_path, "add", "."], check=True, capture_output=True)

            # Check if differences actually exist to avoid empty git commit failures
            diff_check = subprocess.run(["git", "-C", local_path, "status", "--porcelain"], check=True, capture_output=True, text=True)
            if not diff_check.stdout.strip():
                self.log("Local system environment is fully identical to current git branch state. No commit required.")
                return

            # Configuration setup for sovereign agent Git profile
            subprocess.run(["git", "-C", local_path, "config", "user.name", "github-repository-manager-agent"], check=True, capture_output=True)
            subprocess.run(["git", "-C", local_path, "config", "user.email", "agent@autonomous-system.local"], check=True, capture_output=True)

            self.log(f"Creating git commit with message: {commit_message}")
            subprocess.run(["git", "-C", local_path, "commit", "-m", commit_message], check=True, capture_output=True)

            self.log(f"Pushing updates to origin remote: branch {branch_name}")
            subprocess.run(["git", "-C", local_path, "push", "-u", "origin", branch_name], check=True, capture_output=True)
            self.log("Push operation successfully completed.")
        except Exception as e:
            self.log(f"Error in GithubRepositoryManagerAgent._commit_and_push: {e}")