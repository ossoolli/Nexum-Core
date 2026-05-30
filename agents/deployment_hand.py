import os
import json
import subprocess
import time
import tempfile
import logging
from typing import Dict, Any, List
from core.base_agent import BaseAgent
from services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

class DeploymentHand(BaseAgent):
    """
    DeploymentHand Agent — السيادة البرمجية
    مسؤول عن إنشاء ونشر المواقع تلقائياً على GitHub Pages.
    """

    def __init__(self):
        super().__init__(
            name="deployment_hand",
            description="نظام النشر الآلي للمواقع (Website Deployer Protocol)",
            version="1.0"
        )
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.deployments_file = os.path.join(base_dir, "storage", "deployments.json")
        
    def _execute_shell(self, cmd: str, cwd: str = None, retries: int = 3) -> Dict[str, Any]:
        """تنفيذ أمر shell مع محاولات إعادة"""
        attempt = 0
        while attempt < retries:
            try:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, cwd=cwd, check=True
                )
                return {"success": True, "output": result.stdout, "error": None}
            except subprocess.CalledProcessError as e:
                attempt += 1
                if attempt == retries:
                    return {"success": False, "output": e.stdout, "error": e.stderr}
                time.sleep(2)
        return {"success": False, "error": "Maximum retries reached"}

    def _generate_content(self, description: str, project_type: str) -> Dict[str, str]:
        """استخدام Gemini لتوليد محتوى الموقع"""
        prompt = f"""
        أنت مطور ويب خبير. قم بتوليد محتوى HTML و CSS (Tailwind) لمشروع: {description}
        نوع الموقع: {project_type}
        
        المطلوب هو كود HTML كامل في ملف واحد يحتوي على:
        1. شريط تنقل (Navbar)
        2. قسم بطولي (Hero Section) مع عنوان جذاب
        3. قسم المميزات (Features)
        4. قسم تواصل معنا (Contact)
        5. تذييل (Footer)
        
        استخدم CDN لـ Tailwind CSS.
        اجعل التصميم عصرياً واحترافياً.
        أعد الكود فقط، بدون أي شرح إضافي.
        """
        response, _ = gemini_service.ask(prompt)
        # تنظيف الرد من علامات markdown إذا وجدت
        code = response.replace("```html", "").replace("```", "").strip()
        return {"index.html": code}

    def deploy_site(self, name: str, description: str, project_type: str, bot=None, chat_id=None) -> Dict[str, Any]:
        """البروتوكول الكامل لنشر الموقع"""
        def notify(msg):
            if bot and chat_id:
                bot.send_message(chat_id, f"🚀 <b>[DeploymentHand]:</b> {msg}", parse_mode="HTML")
            self.log(msg)

        notify(f"بدء نشر المشروع: {name}")
        
        repo_path = os.path.join(tempfile.gettempdir(), f"{name}_{int(time.time())}")
        os.makedirs(repo_path, exist_ok=True)

        # 1. GitHub Repo Create
        notify("إنشاء مستودع GitHub جديد...")
        res = self._execute_shell(f"gh repo create {name} --public --confirm", cwd=repo_path)
        if not res["success"]:
             # قد يكون المستودع موجوداً بالفعل، نحاول المتابعة
             notify(f"تنبيه: {res.get('error') or 'المستودع قد يكون موجوداً'}")

        # 2. Scaffold & Gemini Content
        notify("توليد المحتوى عبر Gemini...")
        files = self._generate_content(description, project_type)
        for filename, content in files.items():
            with open(os.path.join(repo_path, filename), 'w', encoding='utf-8') as f:
                f.write(content)

        # 3. Git Ops
        notify("إعداد Git ورفع الملفات...")
        self._execute_shell("git init", cwd=repo_path)
        self._execute_shell(f"git remote add origin https://github.com/$(gh api user -q .login)/{name}.git", cwd=repo_path)
        self._execute_shell("git add .", cwd=repo_path)
        self._execute_shell('git commit -m "Initial scaffold by Nexum DeploymentHand"', cwd=repo_path)
        self._execute_shell("git branch -M main", cwd=repo_path)
        res = self._execute_shell("git push -u origin main --force", cwd=repo_path)
        
        if not res["success"]:
            notify(f"خطأ في الرفع: {res['error']}")
            return res

        # 4. Enable GitHub Pages
        notify("تفعيل GitHub Pages...")
        owner = self._execute_shell("gh api user -q .login")["output"].strip()
        # تفعيل Pages عبر API
        res = self._execute_shell(f"gh api repos/{owner}/{name}/pages --method POST -f source='{{\"branch\":\"main\",\"path\":\"/\"}}'", cwd=repo_path)
        
        site_url = f"https://{owner}.github.io/{name}"
        notify(f"✅ تم النشر بنجاح! الرابط: {site_url}")

        # 5. Logging
        deployment_info = {
            "name": name,
            "description": description,
            "type": project_type,
            "url": site_url,
            "timestamp": time.ctime()
        }
        self._save_deployment(deployment_info)
        
        return {"status": "success", "url": site_url}

    def _save_deployment(self, info: dict):
        try:
            data = []
            if os.path.exists(self.deployments_file):
                with open(self.deployments_file, 'r') as f:
                    data = json.load(f)
            data.append(info)
            with open(self.deployments_file, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            self.log(f"Failed to log deployment: {e}", level="ERROR")

    def run(self, input_data: dict) -> dict:
        """واجهة تشغيل الوكيل"""
        name = input_data.get("name")
        description = input_data.get("description", "")
        project_type = input_data.get("type", "landing")
        bot = input_data.get("bot")
        chat_id = input_data.get("chat_id")
        
        if not name:
            return {"status": "error", "error": "اسم المشروع مطلوب"}
            
        return self.deploy_site(name, description, project_type, bot, chat_id)

deployment_hand = DeploymentHand()
