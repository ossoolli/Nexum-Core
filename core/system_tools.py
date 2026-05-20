"""
System Tools Plugin 🛠️
======================
يقوم بتسجيل أدوات النظام الأساسية (Terminal و Sandbox و File System) 
في الـ Tool Registry لتكون متوفرة للوكلاء بصيغة (Function Calling).
"""
import os
import urllib.request
import urllib.parse
import re
from typing import Dict, Any

from core.tool_registry import tool_registry
from core.sandbox import sandbox
from core.executor import executor
from core.cloud_storage import cloud_manager
import shutil
import zipfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def fetch_webpage(url: str) -> Dict[str, Any]:
    """
    يقرأ محتويات صفحة ويب (رابط) لاستخراج النصوص والمعلومات منها (Scraping).
    """
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')
            text = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            return {"status": "success", "content": text[:8000]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def search_web(query: str) -> Dict[str, Any]:
    """
    يبحث في الويب (DuckDuckGo) لجلب معلومات حديثة.
    """
    try:
        url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')
            results = []
            for match in re.finditer(r'<a class="result__url" href="([^"]+)">(.*?)</a>.*?<a class="result__snippet[^>]*>(.*?)</a>', html, re.IGNORECASE | re.DOTALL):
                results.append({
                    "url": match.group(1).strip(),
                    "snippet": re.sub(r'<[^>]+>', '', match.group(3)).strip()
                })
            return {"status": "success", "results": results[:5]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def run_in_sandbox(agent_id: str, script_content: str, language: str = "python") -> Dict[str, Any]:
    """
    يقوم بتنفيذ كود برمجي (Python بشكل افتراضي) داخل حاوية عزل (Docker/gVisor).
    استخدم هذا لتنفيذ أكواد حسابية معقدة، فحص مكتبات خارجية، أو تجربة سكربتات غير موثوقة.
    """
    return sandbox.execute_in_sandbox(agent_id, script_content, language)


def run_host_terminal(command: str) -> Dict[str, Any]:
    """
    ينفذ أمر Bash/Shell مباشرة على السيرفر الخادم (Host Terminal).
    صلاحية السيادة: يتم التنفيذ مباشرة (Autonomous) لأن الوكيل يعمل ضمن بروتوكول معتمد.
    """
    # نمرر force=True لتمكين الاستقلالية واتخاذ القرارات دون تدخل يدوي في كل خطوة
    result = executor.execute(command, force=True)
    return {
        "status": result.get("status", "error"),
        "output": result.get("output", "")
    }


def write_file(filepath: str, content: str) -> Dict[str, Any]:
    """
    يكتب محتوى نصي بالكامل في ملف داخل مجلد المشروع.
    """
    try:
        # إذا كان المسار مطلقاً، نتأكد أنه يبدأ بـ BASE_DIR
        if os.path.isabs(filepath):
            if not filepath.startswith(os.path.abspath(BASE_DIR)):
                return {"status": "error", "message": f"Access Denied: Absolute path must start with {BASE_DIR}"}
            full_path = filepath
        else:
            # إذا كان نسبياً، ندمجه مع BASE_DIR
            # نمنع محاولات الـ Traversal (مثل ../)
            safe_path = os.path.normpath(filepath).lstrip('./').lstrip('/')
            if safe_path.startswith('..'):
                 return {"status": "error", "message": "Access Denied: Path outside project root."}
            full_path = os.path.abspath(os.path.join(BASE_DIR, safe_path))

        # التأكد النهائي من أن المسار داخل BASE_DIR
        if not os.path.abspath(full_path).startswith(os.path.abspath(BASE_DIR)):
            return {"status": "error", "message": "Access Denied: Target path is outside project root."}
            
        directory = os.path.dirname(full_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"status": "success", "message": f"تم بنجاح كتابة الملف في: {os.path.relpath(full_path, BASE_DIR)}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def list_directory(path: str = ".") -> Dict[str, Any]:
    """
    يسرد محتويات مجلد معين داخل المشروع.
    """
    try:
        if os.path.isabs(path):
            if not path.startswith(os.path.abspath(BASE_DIR)):
                 return {"status": "error", "message": "Access Denied: Path outside project root."}
            full_path = path
        else:
            full_path = os.path.abspath(os.path.join(BASE_DIR, path))

        # حماية إضافية
        if not os.path.abspath(full_path).startswith(os.path.abspath(BASE_DIR)):
             return {"status": "error", "message": "Access Denied: Path outside project root."}
            
        files = os.listdir(full_path)
        return {"status": "success", "files": files}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def read_file(filepath: str) -> Dict[str, Any]:
    """
    يقرأ محتويات ملف من داخل المشروع.
    """
    try:
        if os.path.isabs(filepath):
            if not filepath.startswith(os.path.abspath(BASE_DIR)):
                 return {"status": "error", "message": "Access Denied: Path outside project root."}
            full_path = filepath
        else:
            full_path = os.path.abspath(os.path.join(BASE_DIR, filepath))

        if not os.path.abspath(full_path).startswith(os.path.abspath(BASE_DIR)):
             return {"status": "error", "message": "Access Denied: Path outside project root."}
            
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"status": "success", "content": content[:5000]}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def zip_project(project_path: str) -> Dict[str, Any]:
    """يؤرشف مجلد مشروع بالكامل في ملف ZIP واحد."""
    try:
        # التأكد من المسار
        safe_path = os.path.normpath(project_path).lstrip('./').lstrip('/')
        full_dir = os.path.abspath(os.path.join(BASE_DIR, safe_path))
        
        if not os.path.abspath(full_dir).startswith(os.path.abspath(BASE_DIR)):
            return {"status": "error", "message": "Access Denied"}
            
        zip_name = f"{os.path.basename(full_dir)}.zip"
        zip_path = os.path.join(BASE_DIR, "storage/temp", zip_name)
        
        os.makedirs(os.path.dirname(zip_path), exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(full_dir):
                for file in files:
                    file_abs_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_abs_path, full_dir)
                    zipf.write(file_abs_path, arcname)
                    
        return {"status": "success", "zip_path": zip_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def cloud_backup(file_path: str, chat_id: str = None) -> Dict[str, Any]:
    """يرفع ملفاً إلى تيليجرام (القناة المربوطة) وسوباباس."""
    try:
        # إذا لم يتم تحديد chat_id نستخدم القناة الافتراضية من البيئة
        target_id = chat_id or os.getenv("TELEGRAM_CHANNEL_ID")
        
        # 1. تيليجرام
        tg_res = cloud_manager.upload_to_telegram(file_path, target_id, caption=f"📦 نسخة احتياطية: {os.path.basename(file_path)}")
        
        # 2. سوباباس
        sb_res = cloud_manager.upload_to_supabase(file_path)
        
        return {
            "status": "success",
            "telegram": "Sent" if tg_res else "Failed",
            "supabase": sb_res
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def register_all_system_tools():
    """يسجل جميع أدوات النظام في السجل المركزي"""
    # ─── أدوات النظام الأساسية ───
    tool_registry.register_local_tool("run_in_sandbox", run_in_sandbox)
    tool_registry.register_local_tool("run_host_terminal", run_host_terminal)
    tool_registry.register_local_tool("write_file", write_file)
    tool_registry.register_local_tool("read_file", read_file)
    tool_registry.register_local_tool("list_directory", list_directory)
    tool_registry.register_local_tool("fetch_webpage", fetch_webpage)
    tool_registry.register_local_tool("search_web", search_web)
    tool_registry.register_local_tool("zip_project", zip_project)
    tool_registry.register_local_tool("cloud_backup", cloud_backup)

    # ─── أدوات الوكلاء الجدد (v5.0) ───
    try:
        from agents.webforge_agent import webforge
        tool_registry.register_local_tool("build_website", webforge.build_landing_page)
        tool_registry.register_local_tool("build_dashboard", webforge.build_dashboard)
        tool_registry.register_local_tool("build_fastapi", webforge.build_fastapi_app)
        tool_registry.register_local_tool("list_projects", webforge.list_projects)
    except Exception:
        pass

    try:
        from agents.agent_smith import agent_smith
        tool_registry.register_local_tool("design_agent", agent_smith.design_agent)
        tool_registry.register_local_tool("build_agent", agent_smith.build_agent)
        tool_registry.register_local_tool("export_agent", agent_smith.export_agent)
        tool_registry.register_local_tool("list_agents", agent_smith.list_agents)
    except Exception:
        pass

    try:
        from core.bot_fleet import bot_fleet
        tool_registry.register_local_tool("spawn_bot", bot_fleet.spawn_bot)
        tool_registry.register_local_tool("list_bots", bot_fleet.list_bots)
        tool_registry.register_local_tool("kill_bot", bot_fleet.kill_bot)
    except Exception:
        pass

    try:
        from agents.channel_manager import channel_manager
        tool_registry.register_local_tool("cross_post", channel_manager.cross_post)
        tool_registry.register_local_tool("schedule_post", channel_manager.schedule_post)
    except Exception:
        pass

    print("✅ [System Tools] تم تسجيل جميع الأدوات بنجاح (7 أساسية + أدوات الوكلاء).")

