import os
from typing import Dict
from core.executor import executor

class FrontendAgent:
    """
    Frontend Developer Agent
    متخصص في إنشاء مشاريع الـ Frontend (React, Vite, Tailwind).
    ويعمل وفق قدراته المحددة ضمن الـ Registry.
    """
    
    def __init__(self, workspace_path: str = None):
        self.workspace_path = workspace_path or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def bootstrap_vite_react(self, base_path: str = "webapp_frontend") -> Dict[str, str]:
        """
        ينشئ تطبيق React جديد مبني على Vite (التقنية الأسرع والمفضلة لمعماريتك)
        """
        full_path = os.path.join(self.workspace_path, base_path)
        
        cmd = (
            f"cd {self.workspace_path} && "
            f"npm create vite@latest {base_path} -- --template react && "
            f"cd {base_path} && npm install && npm install -D tailwindcss postcss autoprefixer && "
            f"npx tailwindcss init -p"
        )
        
        res = executor.execute(cmd, force=True)
        if res.get('status') == 'success':
            return {"status": "success", "path": full_path, "output": "React/Vite App bootstrapped successfully."}
        else:
            return {"status": "error", "output": res.get('output')}

    def build_dashboard_ui(self, target_path: str) -> Dict[str, str]:
        """
        مهمة مستقبلية: يولد الكود الفعلي لواجهة Dashboard متطورة 
        ويكتبها في target_path/src/App.jsx.
        (يتم توفير الكود من خلال الـ LLM)
        """
        # Temporary Stub for Orchestrator traversal validation
        return {"status": "success", "message": "Mock: Dashboard fully styled with Tailwind and Shadcn."}

frontend_agent = FrontendAgent()
