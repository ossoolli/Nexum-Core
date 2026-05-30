import os
import subprocess
import shutil
from core.base_agent import BaseAgent

class GithubConnectorAgent(BaseAgent):
    def __init__(self, agent_id=None, name="github_connector", config=None):
        try:
            super().__init__(agent_id=agent_id, name=name, config=config)
            self.tools = ['search_web', 'fetch_webpage']
            self.triggers = ['every_hour']
            
            # Fetch authentication credentials from config or environment
            self.github_token = os.environ.get("GITHUB_TOKEN") or (config.get("github_token") if config else None)
            self.github_user = os.environ.get("GITHUB_USER") or (config.get("github_user") if config else None)
            self.github_email = os.environ.get("GITHUB_EMAIL") or (config.get("github_email") if config else "agent@autonomous.ai")
            
            self.log(f"GithubConnectorAgent successfully initialized. Tools: {self.tools}, Triggers: {self.triggers}")
        except Exception as e:
            if hasattr(self, 'log'):
                self.log(f"Error initializing GithubConnectorAgent: {str(e)}", level="error")
            else:
                print(f"Error initializing GithubConnectorAgent: {str(e)}")

    def configure_git_credentials(self):
        try:
            self.log("Configuring Git user credentials...")
            subprocess.run(["git", "config", "--global", "user.name", self.github_user or "GithubConnectorAgent"], check=True)
            subprocess.run(["git", "config", "--global", "user.email", self.github_email], check=True)
            self.log("Git user configuration updated successfully.")
        except Exception as e:
            self.log(f"Failed configuring local git client settings: {str(e)}", level="error")

    def clone_repository(self, repo_url, clone_path):
        try:
            self.log(f"Cloning repository {repo_url} into {clone_path}...")
            if os.path.exists(clone_path):
                shutil.rmtree(clone_path)
            
            # Incorporate authentication token if present
            authenticated_url = repo_url
            if self.github_token and "github.com" in repo_url and "@" not in repo_url:
                authenticated_url = repo_url.replace("https://", f"https://{self.github_token}@")
                
            subprocess.run(["git", "clone", authenticated_url, clone_path], check=True)
            self.log(f"Successfully cloned repository to {clone_path}")
            return True
        except Exception as e:
            self.log(f"Failed to clone repository: {str(e)}", level="error")
            return False

    def stage_commit_and_push(self, repo_dir, commit_message="Autonomous commit via GithubConnectorAgent", branch="main"):
        try:
            self.log(f"Staging modifications inside {repo_dir}...")
            subprocess.run(["git", "-C", repo_dir, "add", "."], check=True)
            
            status_check = subprocess.run(["git", "-C", repo_dir, "status", "--porcelain"], capture_output=True, text=True)
            if not status_check.stdout.strip():
                self.log("Workspace is clean. No active changes found to push.")
                return True
                
            self.log(f"Creating local commit: '{commit_message}'")
            subprocess.run(["git", "-C", repo_dir, "commit", "-m", commit_message], check=True)
            
            self.log(f"Pushing current state upstream to branch {branch}...")
            subprocess.run(["git", "-C", repo_dir, "push", "origin", branch], check=True)
            self.log("Successfully finalized repository transfer operations.")
            return True
        except Exception as e:
            self.log(f"Failed staging or pushing operations: {str(e)}", level="error")
            return False

    def execute_file_transfer(self, repo_url, branch, file_path, repo_dest_path, commit_message):
        try:
            temp_workspace = os.path.join("/tmp", "github_connector_workspace")
            if self.clone_repository(repo_url, temp_workspace):
                self.configure_git_credentials()
                
                target_filepath = os.path.join(temp_workspace, repo_dest_path)
                os.makedirs(os.path.dirname(target_filepath), exist_ok=True)
                shutil.copy2(file_path, target_filepath)
                self.log(f"Injected requested files into local worktree at {target_filepath}")
                
                success = self.stage_commit_and_push(temp_workspace, commit_message, branch)
                
                if os.path.exists(temp_workspace):
                    shutil.rmtree(temp_workspace)
                return success
            return False
        except Exception as e:
            self.log(f"Error handling automated execution file transfer: {str(e)}", level="error")
            return False

    def run(self, *args, **kwargs):
        try:
            self.log("Starting active execution phase for GithubConnectorAgent...")
            
            # Fetch variables from operational configs or triggers
            repo_url = kwargs.get("repo_url") or (self.config.get("repo_url") if self.config else None)
            branch = kwargs.get("branch") or (self.config.get("branch") if self.config else "main")
            file_path = kwargs.get("file_path") or (self.config.get("file_path") if self.config else None)
            repo_dest_path = kwargs.get("repo_dest_path") or (self.config.get("repo_dest_path") if self.config else None)
            commit_message = kwargs.get("commit_message") or "Autonomous synchronization from connector agent"
            
            if repo_url and file_path and repo_dest_path:
                self.log(f"Incoming file transfer task detected for: {repo_url}")
                success = self.execute_file_transfer(repo_url, branch, file_path, repo_dest_path, commit_message)
                if success:
                    self.log("Successfully uploaded and merged code payload.")
                else:
                    self.log("Payload synchronization failed during upload pipeline.", level="error")
            else:
                self.log("Active request not found. Checking web context for potential remote updates...")
                # Fallback to search_web and fetch_webpage logic to fetch latest code versions if config indicates
                self.log("No explicit repository action parameters found. Cycle terminated in standby.")
                
        except Exception as e:
            self.log(f"Critical execution error inside Agent main loop: {str(e)}", level="error")