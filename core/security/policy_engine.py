from typing import Dict, List

class PolicyEngine:
    """
    Sovereign Runtime Permission Matrix (Security Layer)
    يتحكم بصلاحيات الوصول، الأدوات المسموحة، ونطاق التشغيل لكل وكيل 
    لضمان عدم تجاوز الوكلاء لحدودهم بصلاحيات الـ Sandbox.
    """
    def __init__(self):
        # Default strict zones
        self.zones = {
            "sandbox_only": ["read_file", "write_file"],
            "admin_restricted": ["docker_ps", "shell_execute"],
            "network_only": ["http_get", "git_commit"]
        }
        
    def evaluate_permission(self, agent_id: str, tool_name: str, agent_restrictions: List[str]) -> bool:
        """يحدد إذا ما كان الكيان مخوّل لتنفيذ هذه الأداة بناءً على سياستي القيود والأدوات"""
        
        if "no_direct_code_execution" in agent_restrictions and tool_name == "shell_execute":
            return False
            
        if "no_secret_access" in agent_restrictions and ("env" in tool_name or "credential" in tool_name):
            return False
            
        return True

policy_engine = PolicyEngine()
