import os
from typing import Dict
from core.executor import executor

class GithubAgent:
    """
    Infra & Automation Agent (GitHub Sub-Agent)
    مسؤول عن: إدارة المستودعات، إنشاء ملفات GitHub Actions،
    ونشر المواقع عبر GitHub Pages.
    """
    
    def __init__(self, repo_path: str = None):
        # السماح بتحديد المسار الديناميكي، أو الاعتماد على الجذر
        self.repo_path = repo_path or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.workflows_path = os.path.join(self.repo_path, ".github", "workflows")

    def _execute(self, cmd: str) -> str:
        """ينفذ أوامر Git وغيرها في بيئة المستودع"""
        res = executor.execute(f"cd {self.repo_path} && {cmd}", force=True)
        return res.get('output', '')

    def setup_github_pages(self, branch="gh-pages") -> Dict[str, str]:
        """
        تقوم بتوليد ملف Github Action تلقائي لبناء ونشر Static Sites
        مثل Vite أو React إلى Github Pages.
        """
        os.makedirs(self.workflows_path, exist_ok=True)
        workflow_file = os.path.join(self.workflows_path, "deploy_pages.yml")
        
        # بروتوكول بناء CI/CD معياري لـ Static apps
        yaml_content = f"""name: Deploy to GitHub Pages

on:
  push:
    branches: ["main"]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{{{ steps.deployment.outputs.page_url }}}}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 18
      - name: Install dependencies
        run: npm install
      - name: Build Dashboard
        run: npm run build
      - name: Setup Pages
        uses: actions/configure-pages@v4
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: './dist'
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
"""
        try:
            with open(workflow_file, 'w', encoding='utf-8') as f:
                f.write(yaml_content)
            
            # Commit and push
            self._execute("git add .github/workflows/deploy_pages.yml")
            self._execute('git commit -m "Auto-generated: GitHub Pages deployment workflow"')
            
            return {"status": "success", "message": "GitHub Pages CI/CD workflow created."}
        
        except Exception as e:
            return {"status": "error", "message": str(e)}

github_agent = GithubAgent()
