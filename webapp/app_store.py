import os
import json
from fastapi import APIRouter, HTTPException
from core.tool_registry import tool_registry

router = APIRouter(prefix="/apps")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISCOVERED_FILE = os.path.join(BASE_DIR, "storage", "discovered_tools.json")
PLUGINS_DIR = os.path.join(BASE_DIR, "plugins", "active")

@router.get("/")
def list_installed_apps():
    """عرض الأدوات المثبتة حالياً"""
    return tool_registry.get_all_tools_schema()

@router.get("/discovered")
def list_discovered_apps():
    """عرض الأدوات المكتشفة التي لم تثبت بعد"""
    if os.path.exists(DISCOVERED_FILE):
        with open(DISCOVERED_FILE, 'r') as f:
            return json.load(f)
    return []

@router.post("/install/{tool_name}")
def install_app(tool_name: str):
    """
    تثبيت أداة. في هذا النموذج، التثبيت يعني نقل الكود 
    أو تفعيل الربط. للتبسيط، سنحاكي النجاح.
    """
    # البحث في القائمة المكتشفة
    discovered = list_discovered_apps()
    tool = next((t for t in discovered if t["name"] == tool_name), None)
    
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found in discovery list")
    
    # محاكاة إنشاء ملف بلجن
    plugin_path = os.path.join(PLUGINS_DIR, f"{tool_name.replace('/', '_')}.py")
    with open(plugin_path, 'w') as f:
        f.write(f'# Auto-installed tool: {tool["name"]}\n')
        f.write(f'# URL: {tool["url"]}\n')
        f.write('def tool_action(params): return "Executed tool from App Store"\n')
        
    return {"status": "success", "message": f"Installed {tool_name}"}

@router.delete("/uninstall/{tool_name}")
def uninstall_app(tool_name: str):
    plugin_path = os.path.join(PLUGINS_DIR, f"{tool_name.replace('/', '_')}.py")
    if os.path.exists(plugin_path):
        os.remove(plugin_path)
        return {"status": "success", "message": f"Uninstalled {tool_name}"}
    raise HTTPException(status_code=404, detail="Plugin file not found")
