import os
import subprocess
import shutil
from typing import List, Dict, Any
from core.base_agent import BaseAgent

class GitIntegrationAgentAgent(BaseAgent):
    """
    GitIntegrationAgentAgent is an autonomous agent designed to securely connect 
    to GitHub repositories, manage branches, stage modifications, commit updates,
    and push changes to remote repositories automatically.
    """

    def __init__(self, name: str = "git_integration_agent", *args, **kwargs):
        try:
            super().__init__(name=name, *args, **kwargs)
            self.tools = ['search_web', 'fetch_webpage']
            self.triggers = ['every_hour']
            
            # Secure configurations from environment
            self.github_token = os.getenv("GITHUB_TOKEN")
            self.repo_owner = os.getenv("GITHUB_REPO_OWNER")
            self.repo_name = os.getenv("GITHUB_REPO_NAME")
            self.target_branch = os.getenv("GITHUB_BRANCH", "main")
            self.local_path = os.getenv("LOCAL_REPO_PATH", "./cloned_repo")
            self.git_author_name = os.getenv("GIT_AUTHOR_NAME", "Git Integration Agent")
            self.git_author_email = os.getenv("GIT_AUTHOR_EMAIL", "agent@git-integration.local")
            
            self.log(f"Agent {self.name} initialized with tools {self.tools} and triggers {self.triggers}.")
        except Exception as e:
            if hasattr(self, 'log'):
                self.log(f"Error during initialization: {str(e)}")
            else:
                print(f"Error during initialization: {str(e)}")

    def run(self, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main execution loop triggered hourly. Checks credentials, pulls the repo,
        applies any automated updates, and safely commits/pushes them.
        """
        try:
            self.log("Starting Git Integration execution cycle...")
            
            if not self.github_token or not self.repo_owner or not self.repo_name:
                self.log("Missing GitHub configuration environment variables (GITHUB_TOKEN, GITHUB_REPO_OWNER, GITHUB_REPO_NAME).")
                return {"status": "failed", "reason": "Missing environment credentials"}

            # Step 1: Clone or update the repository
            self.log("Synchronizing repository...")
            sync_success = self._sync_repository()
            if not sync_success:
                return {"status": "failed", "reason": "Repository synchronization failed"}

            # Step 2: Configure Git User Info
            self._configure_git_user()

            # Step 3: Manage local branch
            self.log(f"Setting branch to: {self.target_branch}")
            if not self._checkout_branch(self.target_branch):
                return {"status": "failed", "reason": f"Failed to checkout/create branch {self.target_branch}"}

            # Step 4: Detect changes or perform mock automation updates
            # (In a real scenario, other tasks/agents write files to self.local_path)
            self._apply_pending_updates()

            # Step 5: Stage, Commit and Push changes
            staged = self._stage_changes()
            if staged:
                commit_msg = "Auto-update by Git Integration Agent"
                if self._commit_changes(commit_msg):
                    if self._push_changes(self.target_branch):
                        self.log("Successfully committed and pushed updates to remote repository.")
                        return {"status": "success", "action": "pushed_updates"}
                    else:
                        self.log("Failed to push updates.")
                        return {"status": "failed", "reason": "Push failed"}
                else:
                    self.log("Failed to commit updates.")
                    return {"status": "failed", "reason": "Commit failed"}
            else:
                self.log("No changes detected to stage or push.")
                return {"status": "success", "action": "no_changes"}

        except Exception as e:
            self.log(f"Error in run execution: {str(e)}")
            return {"status": "failed", "error": str(e)}

    def _run_git_command(self, args: List[str], cwd: str = None) -> tuple:
        """Helper to run shell git commands securely."""
        try:
            if cwd is None:
                cwd = self.local_path
            result = subprocess.run(
                args,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.log(f"Git command failed: {' '.join(args)} | Error: {e.stderr.strip()}")
            return False, e.stderr.strip()
        except Exception as e:
            self.log(f"Unexpected error running git command: {str(e)}")
            return False, str(e)

    def _sync_repository(self) -> bool:
        """Clones the repo if not exists, or pulls latest changes."""
        try:
            auth_url = f"https://{self.github_token}@github.com/{self.repo_owner}/{self.repo_name}.git"
            
            if os.path.exists(os.path.join(self.local_path, ".git")):
                self.log("Local repository found. Pulling latest...")
                success, _ = self._run_git_command(["git", "fetch", "--all"])
                if success:
                    success, _ = self._run_git_command(["git", "reset", "--hard", f"origin/{self.target_branch}"])
                return success
            else:
                self.log("No local repository found. Cloning remotely...")
                if os.path.exists(self.local_path):
                    shutil.rmtree(self.local_path)
                os.makedirs(self.local_path, exist_ok=True)
                
                # Clone command executed in parent directory of self.local_path
                parent_dir = os.path.dirname(os.path.abspath(self.local_path))
                folder_name = os.path.basename(self.local_path)
                
                success, _ = self._run_git_command(
                    ["git", "clone", auth_url, folder_name],
                    cwd=parent_dir
                )
                return success
        except Exception as e:
            self.log(f"Error in _sync_repository: {str(e)}")
            return False

    def _configure_git_user(self):
        """Sets git configurations locally inside the repository."""
        try:
            self._run_git_command(["git", "config", "user.name", self.git_author_name])
            self._run_git_command(["git", "config", "user.email", self.git_author_email])
        except Exception as e:
            self.log(f"Error configuring git user: {str(e)}")

    def _checkout_branch(self, branch_name: str) -> bool:
        """Checks out existing branch or creates a new one if it doesn't exist."""
        try:
            success, _ = self._run_git_command(["git", "checkout", branch_name])
            if not success:
                self.log(f"Branch {branch_name} not found. Creating locally...")
                success, _ = self._run_git_command(["git", "checkout", "-b", branch_name])
            return success
        except Exception as e:
            self.log(f"Error checking out branch {branch_name}: {str(e)}")
            return False

    def _apply_pending_updates(self):
        """Mock method simulating generation of programmatic updates or agent logging."""
        try:
            agent_log_path = os.path.join(self.local_path, "agent_status.json")
            with open(agent_log_path, "w", encoding="utf-8") as f:
                f.write(f'{{"last_checked": "hourly", "agent": "{self.name}", "status": "active"}}')
            self.log("Status log file updated/written to the workspace.")
        except Exception as e:
            self.log(f"Error generating update files: {str(e)}")

    def _stage_changes(self) -> bool:
        """Stages all updated files."""
        try:
            success, _ = self._run_git_command(["git", "add", "-A"])
            if not success:
                return False
            # Check if there are actual modifications staged
            _, status_out = self._run_git_command(["git", "status", "--porcelain"])
            return len(status_out.strip()) > 0
        except Exception as e:
            self.log(f"Error staging changes: {str(e)}")
            return False

    def _commit_changes(self, message: str) -> bool:
        """Commits staged changes."""
        try:
            success, _ = self._run_git_command(["git", "commit", "-m", message])
            return success
        except Exception as e:
            self.log(f"Error committing changes: {str(e)}")
            return False

    def _push_changes(self, branch_name: str) -> bool:
        """Pushes modifications safely to the authenticated remote."""
        try:
            success, _ = self._run_git_command(["git", "push", "-u", "origin", branch_name])
            return success
        except Exception as e:
            self.log(f"Error pushing changes to branch {branch_name}: {str(e)}")
            return False