import os
import json
import base64
import urllib.request
import urllib.error
import subprocess
from core.base_agent import BaseAgent

class GithubPublisherAgentAgent(BaseAgent):
    def __init__(self, agent_id, name, config):
        try:
            super().__init__(agent_id, name, config)
            self.tools = ['search_web', 'fetch_webpage']
            self.triggers = ['every_hour']
            self.github_token = self.config.get("github_token") or os.getenv("GITHUB_TOKEN")
            self.repo_owner = self.config.get("repo_owner")
            self.repo_name = self.config.get("repo_name")
            self.branch = self.config.get("branch", "main")
            self.log(f"GithubPublisherAgentAgent successfully initialized for: {self.repo_owner}/{self.repo_name}")
        except Exception as e:
            if hasattr(self, 'log'):
                self.log(f"Error inside __init__: {str(e)}")
            else:
                print(f"Error inside __init__: {str(e)}")

    def run(self, payload=None):
        try:
            self.log("Executing GithubPublisherAgentAgent run cycle...")
            
            if not self.github_token or not self.repo_owner or not self.repo_name:
                self.log("Configuration error: Missing github_token, repo_owner, or repo_name.")
                return {"status": "failed", "error": "Missing essential parameters"}

            # Detect content to publish
            files_to_publish = []
            if payload and "files" in payload:
                files_to_publish = payload["files"]
            else:
                self.log("No dynamic file payload provided. Generating system status heartbeat.")
                files_to_publish = [
                    {
                        "path": "status_heartbeat.json",
                        "content": json.dumps({"status": "active", "agent": self.name, "timestamp": "every_hour"}, indent=2),
                        "commit_message": "chore: automatic status update from github_publisher_agent"
                    }
                ]

            results = []
            for file_info in files_to_publish:
                path = file_info.get("path")
                content = file_info.get("content", "")
                commit_message = file_info.get("commit_message", "Updated automatically by GithubPublisherAgentAgent")
                
                success = self.publish_file_via_api(path, content, commit_message)
                results.append({"path": path, "success": success})

            self.log(f"Completed run cycle. Results: {results}")
            return {"status": "success", "results": results}

        except Exception as e:
            self.log(f"Error in run method: {str(e)}")
            return {"status": "failed", "error": str(e)}

    def get_file_sha(self, path):
        """Retrieves the file SHA if it exists, necessary for making updates via the REST API."""
        try:
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{path}?ref={self.branch}"
            req = urllib.request.Request(url)
            req.add_header("Authorization", f"Bearer {self.github_token}")
            req.add_header("Accept", "application/vnd.github.v3+json")
            req.add_header("User-Agent", "GithubPublisherAgent")

            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data.get("sha")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                self.log(f"File {path} not found. Proceeding as fresh file creation.")
                return None
            self.log(f"HTTP Error code {e.code} during SHA lookup: {e.reason}")
            return None
        except Exception as e:
            self.log(f"Error getting file SHA: {str(e)}")
            return None

    def publish_file_via_api(self, path, content, commit_message):
        """Main functional api method to write code/data files to the target repository."""
        try:
            self.log(f"Preparing upload for: {path}")
            sha = self.get_file_sha(path)
            
            content_encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{path}"
            
            body = {
                "message": commit_message,
                "content": content_encoded,
                "branch": self.branch
            }
            if sha:
                body["sha"] = sha

            req_data = json.dumps(body).encode('utf-8')
            req = urllib.request.Request(url, data=req_data, method="PUT")
            req.add_header("Authorization", f"Bearer {self.github_token}")
            req.add_header("Accept", "application/vnd.github.v3+json")
            req.add_header("Content-Type", "application/json")
            req.add_header("User-Agent", "GithubPublisherAgent")

            with urllib.request.urlopen(req) as response:
                if response.status in [200, 201]:
                    self.log(f"Success: File '{path}' committed successfully to branch '{self.branch}'.")
                    return True
                else:
                    self.log(f"Unexpected status code from API: {response.status}")
                    return False
        except Exception as e:
            self.log(f"Failed to publish file {path} due to exception: {str(e)}")
            return False

    def execute_local_git_command(self, repo_dir, commands):
        """Fallback helper to run native system Git commands on physical paths if needed."""
        try:
            self.log(f"Executing Git sequence inside directory: {repo_dir}")
            results = []
            for cmd in commands:
                process = subprocess.Popen(
                    cmd,
                    cwd=repo_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True,
                    text=True
                )
                stdout, stderr = process.communicate()
                self.log(f"Command '{cmd}' exit code: {process.returncode}")
                results.append({
                    "command": cmd,
                    "exit_code": process.returncode,
                    "stdout": stdout.strip(),
                    "stderr": stderr.strip()
                })
            return results
        except Exception as e:
            self.log(f"Error during physical Git action execution: {str(e)}")
            return []