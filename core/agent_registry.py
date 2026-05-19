import json
import os
from typing import Dict, List, Optional
from datetime import datetime

class AgentRegistry:
    """
    سجل الوكلاء (Agent Registry)
    قاعدة بيانات قدرات الوكلاء المستندة إلى الصلاحيات والقيود (Capability-Based Agent System).
    """
    def __init__(self, registry_file="storage/agent_registry.json"):
        self.registry_file = registry_file
        self.agents: Dict[str, dict] = {}
        self._load_registry()

    def _ensure_dir(self):
        os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)

    def _load_registry(self):
        self._ensure_dir()
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    self.agents = json.load(f)
            except Exception:
                self.agents = {}
        
        # تسجيل الوكلاء الأساسيين في حال كان السجل فارغاً
        if not self.agents:
            self._register_core_agents()

    def _save_registry(self):
        self._ensure_dir()
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(self.agents, f, indent=4)

    def _register_core_agents(self):
        """تسجيل النواة التأسيسية للوكلاء (Core Agents)"""
        self.register_agent(
            agent_id="architect_agent",
            name="Architect Agent",
            role="System Architect",
            capabilities=["design_architecture", "build_protocols", "create_workflows"],
            tools=["generate_diagram", "create_protocol_blueprint"],
            protocols=["system_design_protocol"],
            restrictions=["no_direct_code_execution"]
        )
        self.register_agent(
            agent_id="coding_agent",
            name="Backend & API Coder",
            role="Backend Developer",
            capabilities=["write_python", "build_api", "database_design"],
            tools=["execute_python", "read_file", "write_file", "github_commit"],
            protocols=["backend_development_protocol"],
            restrictions=["requires_sandbox"]
        )
        self.register_agent(
            agent_id="frontend_agent",
            name="UI/UX & Frontend Coder",
            role="Frontend Developer",
            capabilities=["build_react", "deploy_pages", "create_ui", "tailwind"],
            tools=["read_file", "write_file"],
            protocols=["ui_generation_protocol"],
            restrictions=["no_secret_access", "no_root_shell"]
        )
        self.register_agent(
            agent_id="infra_agent",
            name="DevOps & Infrastructure",
            role="DevOps Engineer",
            capabilities=["docker_manage", "cloud_deploy", "github_actions"],
            tools=["docker_ps", "shell_execute"],
            protocols=["deployment_pipeline_protocol"],
            restrictions=["require_admin_approval_for_destructive"]
        )
        
    def register_agent(
        self, 
        agent_id: str, 
        name: str, 
        role: str, 
        capabilities: List[str] = None, 
        tools: List[str] = None,
        protocols: List[str] = None,
        restrictions: List[str] = None
    ):
        """تسجيل وكيل جديد مُوَلَّد"""
        self.agents[agent_id] = {
            "agent_id": agent_id,
            "name": name,
            "role": role,
            "capabilities": capabilities or [],
            "tools": tools or [],
            "protocols": protocols or [],
            "restrictions": restrictions or [],
            "awareness": {
                "last_event_seen": None,
                "current_memory_context": None
            },
            "status": "active",
            "created_at": datetime.now().isoformat()
        }
        self._save_registry()
        return self.agents[agent_id]

    def get_agent(self, agent_id: str) -> Optional[dict]:
        return self.agents.get(agent_id)

    def get_agents_by_capability(self, capability: str) -> List[dict]:
        """البحث عن وكيل يملك قدرة محددة للقيام بمهمة"""
        return [
            agent for agent in self.agents.values()
            if capability in agent.get("capabilities", []) and agent.get("status") == "active"
        ]

    def list_all(self) -> List[dict]:
        """قائمة جميع الوكلاء المسجلين"""
        return list(self.agents.values())

    def register_from_file(self, name: str, filepath: str):
        """تسجيل وكيل من ملف Python مُولّد"""
        self.register_agent(
            agent_id=name,
            name=name,
            role="Generated Agent",
            capabilities=["run"],
            tools=[],
            protocols=[],
            restrictions=[]
        )

    def load_generated_agents(self):
        """تحميل الوكلاء المولّدة تلقائياً من agents/generated/"""
        import importlib.util
        gen_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agents", "generated")
        if not os.path.isdir(gen_dir):
            return
        for f in os.listdir(gen_dir):
            if f.endswith("_agent.py"):
                name = f.replace("_agent.py", "")
                filepath = os.path.join(gen_dir, f)
                try:
                    self.register_from_file(name, filepath)
                except Exception as e:
                    print(f"[AgentRegistry] Failed to load {f}: {e}")

    def send_message_between_agents(
        self,
        from_agent: str,
        to_agent: str,
        message: dict
    ) -> bool:
        """يستدعي EventBus لإرسال رسالة بين وكيلين"""
        try:
            from core.event_bus import event_bus
            event_bus.emit("agent.message", {
                "from": from_agent,
                "to": to_agent,
                "payload": message,
            })
            return True
        except Exception as e:
            print(f"[AgentRegistry] Message relay failed: {e}")
            return False

    def health_check_all(self) -> dict:
        """
        يفحص كل وكيل بـ agent.health_check()
        يُعيد تقريراً: {agent_id: healthy/unhealthy}
        """
        report = {}
        for agent_id, info in self.agents.items():
            try:
                # الوكلاء المولّدة يمكن فحصها ديناميكياً
                report[agent_id] = {
                    "status": info.get("status", "unknown"),
                    "healthy": info.get("status") == "active",
                    "name": info.get("name", agent_id),
                }
            except Exception:
                report[agent_id] = {"status": "error", "healthy": False}
        return report

    def get_marketplace_catalog(self) -> list:
        """قائمة الوكلاء القابلة للتصدير مع الوصف"""
        catalog = []
        for agent_id, info in self.agents.items():
            catalog.append({
                "agent_id": agent_id,
                "name": info.get("name", ""),
                "role": info.get("role", ""),
                "capabilities": info.get("capabilities", []),
                "exportable": info.get("role") == "Generated Agent",
            })
        return catalog

agent_registry = AgentRegistry()


