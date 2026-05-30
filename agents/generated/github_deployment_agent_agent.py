import os
import subprocess
import shutil
from typing import Dict, Any, Optional
from core.base_agent import BaseAgent

class GithubDeploymentAgentAgent(BaseAgent):
    def __init__(self, agent_id: str, name: str = "github_deployment_agent", config: Optional[Dict[str, Any]] = None):
        try:
            super().__init__(agent_id=agent_id, name=name, config=config)
            self.tools = ['search_web', 'fetch_webpage']
            self.triggers = ['every_hour']
            self.log(f"Agent {self.name} initialized successfully.")
        except Exception as e:
            if hasattr(self, 'log'):
                self.log(f"Error initializing agent: {str(e)}", level="error")
            else:
                print(f"Error initializing agent: {str(e)}")

    def run(self, task_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main execution method for the agent. Connects to the external GitHub repository,
        updates the code files dynamically, commits and pushes changes.
        """
        self.log("Starting run execution for GithubDeploymentAgentAgent.")
        result = {"status": "failed", "message": ""}
        
        try:
            task_data = task_data or {}
            repo_url = task_data.get("repo_url") or os.environ.get("GITHUB_REPO_URL")
            github_token = task_data.get("github_token") or os.environ.get("GITHUB_TOKEN")
            branch = task_data.get("branch", "main")
            files_to_update = task_data.get("files", {})  # Expects dict: {"filepath/name.py": "code content"}
            commit_message = task_data.get("commit_message", "Automated deployment by GithubDeploymentAgentAgent")
            author_name = task_data.get("author_name", "Github Deployment Agent")
            author_email = task_data.get("author_email", "agent@deployment-automations.local")

            if not repo_url:
                raise ValueError("Repository URL (repo_url) is required but missing.")
            if not github_token:
                raise ValueError("GitHub Personal Access Token (github_token) is required but missing.")

            # Prepare auth URL safely hiding token
            auth_url = self._get_authenticated_url(repo_url, github_token)
            
            # Temporary workspaces directory
            workspace_dir = os.path.join("/tmp", f"git_deployment_{self.agent_id}")
            if os.path.exists(workspace_dir):
                shutil.rmtree(workspace_dir)
            os.makedirs(workspace_dir, exist_ok=True)

            # Execution Pipeline
            self._clone_repo(auth_url, workspace_dir, branch)
            self._apply_file_changes(workspace_dir, files_to_update)
            self._git_commit_and_push(workspace_dir, branch, commit_message, author_name, author_email)

            # Cleanup workspace local files
            if os.path.exists(workspace_dir):
                shutil.rmtree(workspace_dir)

            result["status"] = "success"
            result["message"] = f"Successfully pushed updates to {repo_url} on branch '{branch}'."
            self.log(result["message"])

        except Exception as e:
            error_msg = f"Execution failed: {str(e)}"
            self.log(error_msg, level="error")
            result["message"] = error_msg
            
        return result

    def _get_authenticated_url(self, repo_url: str, token: str) -> str:
        try:
            if repo_url.startswith("https://"):
                clean_url = repo_url.replace("https://", "")
                return f"https://oauth2:{token}@{clean_url}"
            return repo_url
        except Exception as e:
            self.log(f"Error creating authenticated repository URL: {str(e)}", level="error")
            raise e

    def _clone_repo(self, auth_url: str, path: str, branch: str) -> None:
        try:
            self.log(f"Cloning repository target branch: {branch}...")
            cmd = ["git", "clone", "-b", branch, auth_url, path]
            # Redact token from logs by executing securely and catching subprocess returns
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            self.log("Repository clone completed successfully.")
        except subprocess.CalledProcessError as e:
            err_output = e.stderr.replace(auth_url, "[REDACTED_GITHUB_URL]")
            self.log(f"Git clone failed: {err_output}", level="error")
            raise RuntimeError(f"Git Clone operation failed: {err_output}")
        except Exception as e:
            self.log(f"Error during repository cloning step: {str(e)}", level="error")
            raise e

    def _apply_file_changes(self, repo_path: str, files: Dict[str, str]) -> None:
        try:
            if not files:
                # Fallback verification file if no payload files are defined
                self.log("No specific source code files provided. Generating deployment heartbeat log.")
                files = {"agent_heartbeat.txt": f"Autonomous Deployment Pulse Verified. Agent ID: {self.agent_id}"}

            for filepath, content in files.items():
                full_path = os.path.join(repo_path, filepath)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.log(f"Staged content changes in file: {filepath}")
        except Exception as e:
            self.log(f"Error preparing and writing source code files: {str(e)}", level="error")
            raise e

    def _git_commit_and_push(self, path: str, branch: str, commit_msg: str, author_name: str, author_email: str) -> None:
        try:
            self.log("Configuring git authentication identities...")
            subprocess.run(["git", "-C", path, "config", "user.name", author_name], check=True)
            subprocess.run(["git", "-C", path, "config", "user.email", author_email], check=True)

            self.log("Adding and staging files to Git index...")
            subprocess.run(["git", "-C", path, "add", "."], check=True)

            # Check if there is anything to commit
            status = subprocess.run(["git", "-C", path, "status", "--porcelain"], stdout=subprocess.PIPE, text=True, check=True)
            if not status.stdout.strip():
                self.log("No workspace differences detected. Commit skipped.")
                return

            self.log(f"Committing active changes with message: '{commit_msg}'")
            subprocess.run(["git", "-C", path, "commit", "-m", commit_msg], check=True)

            self.log(f"Pushing commit sequences securely to origin/{branch}...")
            subprocess.run(["git", "-C", path, "push", "origin", branch], check=True)
            self.log("Push actions updated successfully on GitHub.")
        except subprocess.CalledProcessError as e:
            self.log(f"Subprocess git execution error: {e.stderr if e.stderr else str(e)}", level="error")
            raise RuntimeError(f"Failed git sequence actions: {str(e)}")
        except Exception as e:
            self.log(f"Error pushing deployments to GitHub core: {str(e)}", level="error")
            raise e