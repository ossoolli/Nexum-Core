import os
import json
import base64
import requests
from typing import Dict, Any, List, Optional
from core.base_agent import BaseAgent

class GithubIntegrationManagerAgent(BaseAgent):
    """
    عامل ذكاء اصطناعي سيادي ومستقل للاتصال الحقيقي والآمن بمستودعات GitHub.
    يقوم بعمليات الرفع (Push) والتحديث الفعلي للأكواد البرمجية مباشرة.
    """

    def __init__(self, agent_id: str = "github_integration_manager", config: Dict[str, Any] = None):
        try:
            super().__init__(agent_id=agent_id, config=config)
            self.name = "github_integration_manager"
            self.tools = ['search_web', 'fetch_webpage']
            self.triggers = ['every_hour']
            
            # إعدادات GitHub الأمنية من البيئة المحيطة
            self.github_token = os.getenv("GITHUB_TOKEN")
            self.github_api_url = "https://api.github.com"
            
            self.log("info", "تم تهيئة وكيل إدارة تكامل GitHub بنجاح.")
        except Exception as e:
            if hasattr(self, 'log'):
                self.log("error", f"فشل في تهيئة الوكيل: {str(e)}")
            else:
                print(f"Error initializing agent: {str(e)}")

    def _get_headers(self) -> Dict[str, str]:
        """توليد الترويسات الأمنية للاتصال بواجهة GitHub API."""
        try:
            if not self.github_token:
                raise ValueError("مفتاح GITHUB_TOKEN غير متوفر في متغيرات البيئة.")
            return {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            }
        except Exception as e:
            self.log("error", f"خطأ أثناء تجهيز ترويسات الطلب: {str(e)}")
            raise e

    def get_file_sha(self, repo_owner: str, repo_name: str, path: str, branch: str = "main") -> Optional[str]:
        """جلب معرف SHA الخاص بملف معين للتحديث."""
        try:
            url = f"{self.github_api_url}/repos/{repo_owner}/{repo_name}/contents/{path}"
            headers = self._get_headers()
            params = {"ref": branch}
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                return response.json().get("sha")
            elif response.status_code == 404:
                return None  # الملف غير موجود بعد (سيتم إنشاؤه جديداً)
            else:
                self.log("warning", f"فشل التحقق من وجود الملف {path}. رمز الاستجابة: {response.status_code}")
                return None
        except Exception as e:
            self.log("error", f"خطأ أثناء جلب SHA للملف {path}: {str(e)}")
            return None

    def push_file(self, repo_owner: str, repo_name: str, path: str, content: str, commit_message: str, branch: str = "main") -> bool:
        """رفع أو تحديث ملف برمجياً بشكل فعلي ومباشر على GitHub."""
        try:
            url = f"{self.github_api_url}/repos/{repo_owner}/{repo_name}/contents/{path}"
            headers = self._get_headers()
            
            # تشفير المحتوى بصيغة Base64 المطلوبة من GitHub API
            encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
            
            sha = self.get_file_sha(repo_owner, repo_name, path, branch)
            
            data = {
                "message": commit_message,
                "content": encoded_content,
                "branch": branch
            }
            
            if sha:
                data["sha"] = sha
                self.log("info", f"سيتم تحديث الملف الموجود مسبقاً: {path} (SHA: {sha})")
            else:
                self.log("info", f"سيتم إنشاء ملف جديد بالكامل: {path}")

            response = requests.put(url, headers=headers, json=data)
            
            if response.status_code in [200, 201]:
                self.log("info", f"تم رفع وتحديث الملف {path} بنجاح على المستودع {repo_owner}/{repo_name} في الفرع {branch}.")
                return True
            else:
                self.log("error", f"فشل رفع الملف. رمز الاستجابة: {response.status_code} - الاستجابة: {response.text}")
                return False
        except Exception as e:
            self.log("error", f"حدث خطأ غير متوقع أثناء دفع التعديلات إلى GitHub: {str(e)}")
            return False

    def execute_github_workflow_pipeline(self) -> bool:
        """إدارة دورة حياة الرفع التلقائي والتأكد من مطابقة الكود."""
        try:
            self.log("info", "بدء تشغيل خط تجميع ومزامنة الأكواد البرمجية الفعلي...")
            
            # جلب تفاصيل المستودع المستهدف من الإعدادات
            target_owner = self.config.get("target_owner") if self.config else None
            target_repo = self.config.get("target_repo") if self.config else None
            
            if not target_owner or not target_repo:
                # محاولة القراءة الافتراضية من متغيرات البيئة إذا غابت من الإعدادات ديناميكياً
                target_owner = os.getenv("GITHUB_REPO_OWNER")
                target_repo = os.getenv("GITHUB_REPO_NAME")
            
            if not target_owner or not target_repo:
                self.log("warning", "لم يتم العثور على إعدادات المستودع المستهدف (target_owner / target_repo). تم إيقاف العملية.")
                return False

            # مثال لملف تحديث الحالة التلقائي للوكيل
            file_path = "status_reports/agent_heartbeat.json"
            import datetime
            report_data = {
                "agent_id": self.agent_id,
                "status": "ACTIVE",
                "last_run": datetime.datetime.now().isoformat(),
                "sovereign_operations_enabled": True
            }
            content_to_push = json.dumps(report_data, indent=4, ensure_ascii=False)
            commit_msg = "system(bot): تحديث نبضات الوكيل الذاتي وإعدادات المزامنة"

            success = self.push_file(
                repo_owner=target_owner,
                repo_name=target_repo,
                path=file_path,
                content=content_to_push,
                commit_message=commit_msg,
                branch="main"
            )
            return success
        except Exception as e:
            self.log("error", f"فشل في تنفيذ دورة عمل GitHub التلقائية: {str(e)}")
            return False

    def run(self) -> Dict[str, Any]:
        """نقطة انطلاق الوكيل عند الاستدعاء أو تفعيل المشغّل."""
        try:
            self.log("info", f"بدء تنفيذ مهمة الوكيل: {self.name} بناءً على المشغل الدوري.")
            
            if not self.github_token:
                self.log("error", "فشل التشغيل: لم يتم العثور على GITHUB_TOKEN كمتغير بيئي آمن.")
                return {"status": "failed", "error": "Missing GITHUB_TOKEN"}
                
            success = self.execute_github_workflow_pipeline()
            
            if success:
                return {"status": "success", "message": "تمت مزامنة المستودع الفعلي ودفع الأكواد بنجاح."}
            else:
                return {"status": "failed", "message": "فشلت عملية مزامنة ودفع الأكواد الفعلية."}
        except Exception as e:
            self.log("error", f"خطأ جسيم أثناء تشغيل الوكيل: {str(e)}")
            return {"status": "error", "message": str(e)}