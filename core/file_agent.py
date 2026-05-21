"""
core/file_agent.py
وكيل الملفات الحقيقي — يقرأ ويكتب ويتحقق
"""
import os
import shutil
import difflib
from datetime import datetime
from core.env_config import WORKSPACE_DIR, PROJECT_ROOT

class FileAgent:
    def __init__(self):
        self.workspace = WORKSPACE_DIR
        self.project_root = PROJECT_ROOT

    def _resolve_path(self, path: str) -> str:
        """
        يحوّل المسار النسبي لمسار حقيقي مطلق.
        إذا بدأ بـ '/' يُعامل كمطلق.
        إذا بدأ بـ 'workspace/' يُوضع في مجلد workspace.
        غير ذلك يُوضع في جذر المشروع.
        """
        if os.path.isabs(path):
            return path
        if path.startswith("workspace/") or not "/" in path:
            return os.path.join(self.workspace, path.replace("workspace/", ""))
        return os.path.join(self.project_root, path)

    def read_file(self, path: str) -> dict:
        """يقرأ ملفاً ويعيد محتواه مع metadata"""
        real_path = self._resolve_path(path)
        if not os.path.exists(real_path):
            return {
                "success": False,
                "error": f"الملف غير موجود: {real_path}",
                "content": None
            }
        try:
            with open(real_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {
                "success": True,
                "path": real_path,
                "content": content,
                "lines": len(content.splitlines()),
                "size_kb": round(os.path.getsize(real_path) / 1024, 2)
            }
        except Exception as e:
            return {"success": False, "error": str(e), "content": None}

    def write_file(self, path: str, content: str, backup: bool = True) -> dict:
        """
        يكتب ملفاً جديداً أو يستبدل موجوداً.
        إذا backup=True يحفظ نسخة احتياطية قبل الكتابة.
        يتحقق بعد الكتابة أن المحتوى صحيح.
        """
        real_path = self._resolve_path(path)
        os.makedirs(os.path.dirname(real_path), exist_ok=True)

        # نسخة احتياطية
        backup_path = None
        if backup and os.path.exists(real_path):
            backup_path = real_path + f".bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(real_path, backup_path)

        try:
            with open(real_path, "w", encoding="utf-8") as f:
                f.write(content)

            # تحقق فوري
            with open(real_path, "r", encoding="utf-8") as f:
                written = f.read()

            if written != content:
                return {
                    "success": False,
                    "error": "التحقق فشل — المحتوى المكتوب لا يطابق المطلوب",
                    "path": real_path
                }

            return {
                "success": True,
                "path": real_path,
                "lines": len(content.splitlines()),
                "size_kb": round(os.path.getsize(real_path) / 1024, 2),
                "backup": backup_path
            }
        except Exception as e:
            return {"success": False, "error": str(e), "path": real_path}

    def edit_file(self, path: str, old_text: str, new_text: str) -> dict:
        """
        يعدّل جزءاً محدداً من ملف موجود (مثل str_replace).
        يتحقق أن النص القديم موجود قبل التعديل.
        يُبلّغ بـ diff واضح بعد التعديل.
        """
        read_result = self.read_file(path)
        if not read_result["success"]:
            return read_result

        original = read_result["content"]
        if old_text not in original:
            return {
                "success": False,
                "error": f"النص المطلوب تعديله غير موجود في الملف.",
                "hint": "تأكد من النص بالضبط كما هو في الملف"
            }

        if original.count(old_text) > 1:
            return {
                "success": False,
                "error": f"النص موجود {original.count(old_text)} مرات — يجب أن يكون فريداً"
            }

        new_content = original.replace(old_text, new_text, 1)
        write_result = self.write_file(path, new_content)

        if write_result["success"]:
            diff = list(difflib.unified_diff(
                original.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile=f"{path} (قبل)",
                tofile=f"{path} (بعد)",
                n=2
            ))
            write_result["diff"] = "".join(diff[:30])  # أول 30 سطر من الـ diff
        return write_result

    def create_python_module(self, name: str, content: str) -> dict:
        """
        ينشئ ملف Python في workspace مع __init__ تلقائي
        """
        path = f"workspace/{name}.py"
        result = self.write_file(path, content)
        # أنشئ __init__.py إذا لم يكن موجوداً
        init_path = os.path.join(self.workspace, "__init__.py")
        if not os.path.exists(init_path):
            open(init_path, "w").close()
        return result

    def list_workspace(self) -> dict:
        """يعرض محتويات workspace الحالية"""
        files = []
        for root, dirs, filenames in os.walk(self.workspace):
            for fn in filenames:
                fp = os.path.join(root, fn)
                rel = os.path.relpath(fp, self.workspace)
                files.append({
                    "name": rel,
                    "size_kb": round(os.path.getsize(fp) / 1024, 2),
                    "modified": datetime.fromtimestamp(os.path.getmtime(fp)).strftime("%Y-%m-%d %H:%M")
                })
        return {"success": True, "files": files, "count": len(files)}

    def delete_file(self, path: str) -> dict:
        """يحذف ملفاً مع تأكيد"""
        real_path = self._resolve_path(path)
        if not os.path.exists(real_path):
            return {"success": False, "error": "الملف غير موجود"}
        os.remove(real_path)
        return {"success": True, "deleted": real_path, "exists_after": os.path.exists(real_path)}


file_agent = FileAgent()
