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
    يكتب محتوى نصي بالكامل في ملف. إذا كان الملف موجوداً سيتم الكتابة فوقه. 
    يستخدم لإنشاء ملفات Dockerfile، Python، أو ملفات Configuration.
    """
    try:
        # تحويل المسار إلى مسار مطلق يبدأ من BASE_DIR إذا كان نسبياً
        if not os.path.isabs(filepath):
            filepath = os.path.abspath(os.path.join(BASE_DIR, filepath))
            
        # التأكد من وجود المجلد
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return {"status": "success", "message": f"تم بنجاح كتابة {len(content)} حرف في {filepath}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def list_directory(path: str = ".") -> Dict[str, Any]:
    """
    يسرد محتويات مجلد معين. استخدم هذا 'لرؤية' هيكل المشروع والملفات الموجودة.
    """
    try:
        if not os.path.isabs(path):
            path = os.path.abspath(os.path.join(BASE_DIR, path))
            
        files = os.listdir(path)
        return {"status": "success", "files": files}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def read_file(filepath: str) -> Dict[str, Any]:
    """
    يقرأ محتويات ملف نصي. استخدم هذا لفحص الكود البرمجي الحالي أو قراءة السجلات (Logs).
    """
    try:
        if not os.path.isabs(filepath):
            filepath = os.path.abspath(os.path.join(BASE_DIR, filepath))
            
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return {"status": "success", "content": content[:5000]} # تقليل حجم البيانات للـ LLM
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

