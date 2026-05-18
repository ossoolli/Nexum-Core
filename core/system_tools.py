"""
System Tools Plugin 🛠️
======================
يقوم بتسجيل أدوات النظام الأساسية (Terminal و Sandbox و File System) 
في الـ Tool Registry لتكون متوفرة للوكلاء بصيغة (Function Calling).
"""
import os
from typing import Dict, Any

from core.tool_registry import tool_registry
from core.sandbox import sandbox
from core.executor import executor

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
        files = os.listdir(path)
        return {"status": "success", "files": files}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def read_file(filepath: str) -> Dict[str, Any]:
    """
    يقرأ محتويات ملف نصي. استخدم هذا لفحص الكود البرمجي الحالي أو قراءة السجلات (Logs).
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return {"status": "success", "content": content[:5000]} # تقليل حجم البيانات للـ LLM
    except Exception as e:
        return {"status": "error", "message": str(e)}


def register_all_system_tools():
    """يسجل جميع أدوات النظام في السجل المركزي"""
    tool_registry.register_local_tool("run_in_sandbox", run_in_sandbox)
    tool_registry.register_local_tool("run_host_terminal", run_host_terminal)
    tool_registry.register_local_tool("write_file", write_file)
    tool_registry.register_local_tool("read_file", read_file)
    tool_registry.register_local_tool("list_directory", list_directory)
    print("✅ [System Tools] تم تسجيل أدوات Sandbox، Terminal، File System وأدوات الاستكشاف بنجاح.")
