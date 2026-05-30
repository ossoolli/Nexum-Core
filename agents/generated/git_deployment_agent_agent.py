import os
import sys
import subprocess
import shutil
import urllib.request
import urllib.parse
import json
import logging
from typing import Dict, Any, List
from core.base_agent import BaseAgent

class GitDeploymentAgentAgent(BaseAgent):
    def __init__(self, agent_id: str = "git_deployment_agent", config: Dict[str, Any] = None):
        try:
            super().__init__(agent_id=agent_id, config=config)
            self.name = "git_deployment_agent"
            self.tools = ['search_web', 'fetch_webpage']
            self.triggers = ['every_hour']
            
            # Configuration settings from environment or config dictionary
            self.config = config or {}
            self.github_token = os.getenv("GITHUB_TOKEN") or self.config.get("github_token")
            self.github_repo = os.getenv("GITHUB_REPO") or self.config.get("github_repo")  # format: 'username/repo'
            self.target_branch = os.getenv("GITHUB_BRANCH") or self.config.get("github_branch", "main")
            self.git_name = os.getenv("GIT_AUTHOR_NAME") or self.config.get("git_author_name", "Git Deployment Agent")
            self.git_email = os.getenv("GIT_AUTHOR_EMAIL") or self.config.get("git_author_email", "agent@deployment.ai")
            
            # Local workspace path for cloning the repository
            self.workspace_dir = os.path.join(os.getcwd(), "workspace", self.name)
            
            self.log("GitDeploymentAgentAgent initialized successfully.")
        except Exception as e:
            if hasattr(self, 'log'):
                self.log(f"Error initializing GitDeploymentAgentAgent: {str(e)}", level="error")
            else:
                print(f"Error initializing GitDeploymentAgentAgent: {str(e)}")

    def run(self, trigger_type: str = "manual", data: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            self.log(f"Agent triggered by: {trigger_type}")
            
            if not self.github_token or not self.github_repo:
                error_msg = "Missing GITHUB_TOKEN or GITHUB_REPO environment variables. Cannot proceed with real deployment."
                self.log(error_msg, level="error")
                return {"status": "error", "message": error_msg}

            # Step 1: Initialize local workspace and setup credentials
            self.setup_workspace()
            
            # Step 2: Clone or update the repository
            self.clone_or_pull_repository()
            
            # Step 3: Check for pending changes or dynamic codebase updates
            has_updates = self.perform_codebase_updates(data)
            
            if has_updates:
                # Step 4: Commit and Push changes
                commit_message = (data or {}).get("commit_message", "Automated deployment update by Git Deployment Agent")
                self.commit_and_push_changes(commit_message)
                return {"status": "success", "message": "Changes deployed and pushed to remote GitHub repository successfully."}
            else:
                self.log("No code changes detected. Deployment not required.")
                return {"status": "success", "message": "No action needed, repository is up to date."}

        except Exception as e:
            self.log(f"Critical failure during agent run execution: {str(e)}", level="error")
            return {"status": "error", "message": str(e)}

    def setup_workspace(self) -> None:
        try:
            if not os.path.exists(self.workspace_dir):
                os.makedirs(self.workspace_dir, exist_ok=True)
                self.log(f"Created deployment workspace at {self.workspace_dir}")
        except Exception as e:
            self.log(f"Failed to setup workspace directory: {str(e)}", level="error")
            raise e

    def execute_git_command(self, command: List[str], cwd: str = None) -> str:
        try:
            cwd = cwd or self.workspace_dir
            self.log(f"Executing git command: {' '.join(command)}")
            result = subprocess.run(
                command,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            error_details = f"Command: {' '.join(command)}\nExit Code: {e.returncode}\nStderr: {e.stderr}\nStdout: {e.stdout}"
            self.log(f"Git execution failure:\n{error_details}", level="error")
            raise RuntimeError(f"Git command failed: {e.stderr}")
        except Exception as e:
            self.log(f"Unexpected error executing git command: {str(e)}", level="error")
            raise e

    def clone_or_pull_repository(self) -> None:
        try:
            # Construct authenticated remote URL safely
            repo_url = f"https://x-access-token:{self.github_token}@github.com/{self.github_repo}.git"
            git_dir = os.path.join(self.workspace_dir, ".git")

            if not os.path.exists(git_dir):
                self.log(f"Repository not found locally. Cloning {self.github_repo} into workspace...")
                # Clear directory to avoid git clone conflicts with existing files
                if os.path.exists(self.workspace_dir):
                    shutil.rmtree(self.workspace_dir)
                os.makedirs(self.workspace_dir, exist_ok=True)
                
                self.execute_git_command(["git", "clone", "-b", self.target_branch, repo_url, "."])
                self.log("Cloning completed successfully.")
            else:
                self.log("Repository exists locally. Fetching latest updates and cleaning status...")
                self.execute_git_command(["git", "fetch", "origin"])
                self.execute_git_command(["git", "reset", "--hard", f"origin/{self.target_branch}"])
                self.log("Repository synchronized with remote branch successfully.")
            
            # Configure Git credentials locally for the repo
            self.execute_git_command(["git", "config", "user.name", self.git_name])
            self.execute_git_command(["git", "config", "user.email", self.git_email])
        except Exception as e:
            self.log(f"Error during cloning/pulling process: {str(e)}", level="error")
            raise e

    def perform_codebase_updates(self, data: Dict[str, Any]) -> bool:
        try:
            self.log("Checking for autonomous file additions or modifications...")
            
            # Example logic: Deploy configuration updates, self-maintenance files, or code payloads from inputs
            payload_files = (data or {}).get("files_to_deploy") # Expected format: {"filename.py": "code content"}
            
            if not payload_files:
                # Self-healing / status updates mock modification to prove write functionality if no file is provided
                status_file_path = os.path.join(self.workspace_dir, "agent_status.json")
                import datetime
                status_data = {
                    "last_run": datetime.datetime.now().isoformat(),
                    "agent_state": "active",
                    "version": "1.0.0"
                }
                
                with open(status_file_path, "w", encoding="utf-8") as f:
                    json.dump(status_data, f, indent=4)
                self.log("Updated 'agent_status.json' inside the workspace.")
                return True
                
            updated = False
            for relative_path, file_content in payload_files.items():
                target_path = os.path.join(self.workspace_dir, relative_path)
                
                # Make parent directories if they don't exist
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                
                # Write file safely
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(file_content)
                self.log(f"Wrote deployment payload file: {relative_path}")
                updated = True
                
            return updated
        except Exception as e:
            self.log(f"Error while updating codebase files: {str(e)}", level="error")
            raise e

    def commit_and_push_changes(self, commit_message: str) -> None:
        try:
            # Stage changes
            self.execute_git_command(["git", "add", "."])
            
            # Check if there is anything to commit
            status = self.execute_git_command(["git", "status", "--porcelain"])
            if not status:
                self.log("No local modifications detected to commit.")
                return
                
            # Commit and push
            self.execute_git_command(["git", "commit", "-m", commit_message])
            self.log("Changes successfully committed locally.")
            
            self.execute_git_command(["git", "push", "origin", self.target_branch])
            self.log(f"Pushed branch changes successfully to remote origin/{self.target_branch}!")
        except Exception as e:
            self.log(f"Failed to push committed modifications to remote repository: {str(e)}", level="error")
            raise e

    def search_web(self, query: str) -> str:
        try:
            self.log(f"Searching web for query: {query}")
            encoded_query = urllib.parse.quote(query)
            # Utilizing DuckDuckGo Lite API
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')
                # Return raw response limited to prevent overflow in logs
                return html[:3000]
        except Exception as e:
            self.log(f"Error using search_web tool: {str(e)}", level="error")
            return f"Error executing search: {str(e)}"

    def fetch_webpage(self, url: str) -> str:
        try:
            self.log(f"Fetching webpage content from: {url}")
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')
                return html[:10000]
        except Exception as e:
            self.log(f"Error using fetch_webpage tool: {str(e)}", level="error")
            return f"Error executing webpage fetch: {str(e)}"