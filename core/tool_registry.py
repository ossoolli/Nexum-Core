"""
Tool Registry & MCP (Model Context Protocol) Integration 🛠️
===========================================================
هذا السجل يحتفظ بالأدوات المحلية التي يمتلكها النظام،
ويدعم دمج أدوات خارجية عبر (MCP) لكي تُستخدم كـ Function Calling داخل نماذج الذكاء الاصطناعي.
"""
from typing import Dict, Any, Callable, List
import inspect

class MCPClientMock:
    """محاكاة مبسطة لعميل MCP لجلب القدرات من سيرفر خارجي (يمكن استبداله لاحقاً بعميل MCP حقيقي)"""
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self._external_tools = {}

    def fetch_tools(self) -> Dict[str, dict]:
        # في الواقع هنا يقوم بالاتصال عبر WebSocket أو HTTP وجلب هيكل الأدوات
        # كمثال:
        return {
            "fetch_weather": {
                "description": "جلب حالة الطقس",
                "parameters": {"location": "string"}
            }
        }
        
    def execute(self, tool_name: str, params: dict):
        # في الواقع: يرسل طلب التنفيذ للسيرفر الخارجي عبر MCP ويعيد النتيجة
        return f"[MCP: {self.endpoint}] executed {tool_name} with {params}"


def validate_schema(func: Callable) -> dict:
    """استخراج مخطط أداة (Schema) تلقائياً من الـ Type Hints في البايثون لدعمه بـ Function Calling"""
    sig = inspect.signature(func)
    schema = {
        "description": func.__doc__ or "No description provided.",
        "parameters": {}
    }
    for name, param in sig.parameters.items():
        param_type = "string" # Default
        if param.annotation == int: param_type = "integer"
        elif param.annotation == bool: param_type = "boolean"
        elif param.annotation == dict: param_type = "object"
        schema["parameters"][name] = param_type
    return schema


class ToolRegistry:
    def __init__(self):
        # { "tool_name": {"schema": dict, "executor": Callable} }
        self._local_tools = {}
        self._mcp_clients: List[MCPClientMock] = []
        
    def register_local_tool(self, name: str, func: Callable):
        """تسجيل أداة محلية. (يجب أن تحتوي على TypeHints و Docstring جيد)"""
        schema = validate_schema(func)
        self._local_tools[name] = {
            "schema": schema,
            "executor": func
        }

    def register_mcp_server(self, endpoint: str):
        """ربط سيرفر MCP لتمكين الوكلاء من استخدام أدواته"""
        client = MCPClientMock(endpoint)
        self._mcp_clients.append(client)
        print(f"🔗 [ToolRegistry] Linked MCP Server: {endpoint}")

    def get_all_tools_schema(self) -> dict:
        """جلب Schema لجميع الأدوات (محلية + MCP) لتمريرها للـ Agent (Function Calling)"""
        tools_schema = {}
        # Local
        for t_name, t_data in self._local_tools.items():
            tools_schema[t_name] = t_data["schema"]
            
        # MCP
        for mcp in self._mcp_clients:
            ext_tools = mcp.fetch_tools()
            for t_name, schema in ext_tools.items():
                tools_schema[f"mcp::{t_name}"] = schema
                
        return tools_schema

    def execute_tool(self, tool_name: str, params: dict) -> Any:
        """تنفيذ أداة بناءً على اسمها"""
        if tool_name in self._local_tools:
            func = self._local_tools[tool_name]["executor"]
            # استخراج المعايير التي تقبلها الدالة فقط لمنع أخطاء TypeError
            import inspect
            sig = inspect.signature(func)
            valid_params = {k: v for k, v in params.items() if k in sig.parameters}
            return func(**valid_params)
            
        if tool_name.startswith("mcp::"):
            # ابحث عن السيرفر الذي يملك الأداة ونفذها
            real_name = tool_name.replace("mcp::", "")
            for mcp in self._mcp_clients:
                tools = mcp.fetch_tools()
                if real_name in tools:
                    return mcp.execute(real_name, params)
                    
        raise Exception(f"Tool {tool_name} not found in Registry.")

# Singleton
tool_registry = ToolRegistry()

# تسجيل الأدوات المتقدمة (Pillar 3)
try:
    from core.tools.semantic_browser import semantic_search_web, advanced_scrape
    tool_registry.register_local_tool("semantic_search_web", semantic_search_web)
    tool_registry.register_local_tool("advanced_scrape", advanced_scrape)
except ImportError:
    pass
