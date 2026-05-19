import os
from typing import Dict, Any
from core.runtime.sandbox import sandbox_env

class CoreTools:
    """
    Sovereign Execution Tools
    مجموعة الأدوات التي تُمكن الوكلاء من التأثير الحقيقي على النظام.
    جميع التنفيذات الخطرة معزولة عبر RuntimeSandbox.
    """
    async def shell_execute(self, command: str) -> Dict[str, Any]:
        """تنفيذ أمر طرفية داخل الساندبوكس"""
        # إضافة قيود حماية (Basic Validation)
        dangerous_commands = ["rm -rf /", "mkfs", "dd "]
        if any(cmd in command for cmd in dangerous_commands):
            return {"status": "error", "error": "Command blocked by security policies."}
            
        print(f"🔧 [Tool Execution] Running Shell: {command}")
        return await sandbox_env.execute_isolated(command)

    async def read_file(self, filepath: str) -> Dict[str, Any]:
        """قراءة ملف بأمان"""
        try:
            if not os.path.exists(filepath):
                return {"status": "error", "error": "File not found"}
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"status": "success", "content": content[:10000]} # Limit output
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def write_file(self, filepath: str, content: str) -> Dict[str, Any]:
        """كتابة كود/نصوص في ملف"""
        try:
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return {"status": "success", "msg": f"File {filepath} written successfully."}
        except Exception as e:
            return {"status": "error", "error": str(e)}

core_tools_engine = CoreTools()

async def execute_agent_tool(tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """موزع تنفيذ الأدوات بناءً على الاسم"""
    if hasattr(core_tools_engine, tool_name):
        method = getattr(core_tools_engine, tool_name)
        if tool_name == "shell_execute":
            return await method(params.get("command", ""))
        elif tool_name == "read_file":
            return await method(params.get("filepath", ""))
        elif tool_name == "write_file":
            return await method(params.get("filepath", ""), params.get("content", ""))
        else:
            return {"status": "error", "error": "Tool arguments mapping not defined yet."}
    return {"status": "error", "error": f"Tool '{tool_name}' not found in CoreTools."}
