import os
import html
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from core.executor import executor

class DeployAgent:
    def __init__(self):
        self.repo_path = BASE_DIR

    def _run(self, cmd: str) -> str:
        """تشغيل أمر وإرجاع المخرجات كنص آمن"""
        result = executor.execute(cmd, force=True)
        out = result.get('output', '').strip()
        return html.escape(out) if out else "✅ Done."

    def git_status(self) -> str:
        return self._run(f"cd {self.repo_path} && git status")

    def git_pull(self) -> str:
        return self._run(f"cd {self.repo_path} && git pull origin main")

    def deploy_updates(self, commit_msg="🔱 NEXUM Auto-Deploy") -> str:
        safe_msg = commit_msg.replace('"', "'")
        add    = self._run(f"cd {self.repo_path} && git add -A")
        commit = self._run(f'cd {self.repo_path} && git commit -m "{safe_msg}"')
        push   = self._run(f"cd {self.repo_path} && git push origin main")

        return (
            "🚀 <b>بروتوكول النشر التلقائي</b>\n\n"
            f"1️⃣ <b>Add:</b>\n<pre>{add[:500]}</pre>\n"
            f"2️⃣ <b>Commit:</b>\n<pre>{commit[:500]}</pre>\n"
            f"3️⃣ <b>Push:</b>\n<pre>{push[:500]}</pre>"
        )

    def docker_status(self) -> str:
        """حالة حاويات Docker"""
        result = self._run("docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'")
        return f"🐳 <b>حاويات Docker:</b>\n<pre>{result}</pre>"

    def docker_logs(self, container: str) -> str:
        """آخر 30 سطر من logs حاوية معينة"""
        safe = container.replace(';','').replace('&','').replace('|','')
        result = self._run(f"docker logs --tail 30 {safe}")
        return f"📋 <b>Logs [{html.escape(safe)}]:</b>\n<pre>{result[:3000]}</pre>"

deploy_agent = DeployAgent()
