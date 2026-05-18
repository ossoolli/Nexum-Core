import uuid
import json
from core.agent_registry import agent_registry

class AgentFactory:
    """
    Sub-Agent Factory
    محرك توليد الوكلاء المتخصصين بناءً على المتطلبات.
    (يولد API, Prompt, Capability Profile, and Docker constraints)
    """

    def _generate_agent_prompt(self, role: str, capabilities: list, restrictions: list) -> str:
        """يولد Prompt متقدم يعتمد على قيود وقدرات الوكيل"""
        prompt = (
            f"You are a specialized AI Agent identified as {role}.\n"
            f"Your granted capabilities are: {', '.join(capabilities)}.\n"
            f"Your absolute restrictions are: {', '.join(restrictions)}.\n"
            "You operate within NEXUM PRIME ecosystem. Do not deviate from your capabilities.\n"
            "Emit structured JSON protocols for actions."
        )
        return prompt

    def create_specialized_agent(self, name: str, mission: str, required_skills: list):
        """
        يقوم بتوليد وكيل جديد، يمنحه الصلاحيات ويسجله في قاعدة البيانات.
        """
        agent_id = f"gen_agent_{uuid.uuid4().hex[:8]}"
        
        # تحليل المهارات والمهام لتحديد القيود والقدرات
        capabilities = required_skills
        restrictions = ["run_in_sandbox", "no_root_shell", "log_all_actions"]
        
        system_prompt = self._generate_agent_prompt(name, capabilities, restrictions)
        
        # تسجيل الوكيل في الـ Registry
        agent_profile = agent_registry.register_agent(
            agent_id=agent_id,
            name=name,
            role=mission,
            capabilities=capabilities,
            restrictions=restrictions
        )
        
        agent_profile["system_prompt"] = system_prompt
        return agent_profile

agent_factory = AgentFactory()
