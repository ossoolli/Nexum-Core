import logging
import asyncio
from typing import Dict, Any, List
from core.base_agent import AgentStatus

logger = logging.getLogger(__name__)

class MasterOrchestrator:
    """
    MasterOrchestrator — التنسيق السيادي
    المسؤول عن تقسيم المهام الكبيرة وتفويضها لوكلاء متخصصين.
    """
    def __init__(self, agents_registry: Dict[str, Any] = None):
        self.registry = agents_registry or {}
        self.loop = asyncio.get_event_loop()

    def register_agent(self, name: str, agent_instance: Any):
        self.registry[name] = agent_instance

    async def delegate_task(self, goal: str, context: dict = None) -> dict:
        """
        تقسيم الهدف وتفويضه
        """
        logger.info(f"Delegating master goal: {goal}")
        
        # 1. التخطيط (عبر Gemini)
        # سيقوم Gemini بتقسيم المهمة لخطوات: {'subtasks': [{'agent': 'deployment', 'task': '...'}, ...]}
        # للتبسيط هنا سنحاكي التقسيم أو نطلب من Gemini مباشرة
        
        from services.gemini_service import gemini_service
        prompt = f"""
        أنت المايسترو لنظام Nexum-Core. قم بتقسيم الهدف التالي لمهام فرعية متوازية.
        الهدف: {goal}
        
        الوكلاء المتاحون:
        - deployment: لنشر المواقع
        - content: لتوليد المحتوى التسويقي
        - finance: لتسجيل العمليات المالية
        - tools: للبحث عن أدوات
        
        أعد JSON يحتوي على قائمة 'tasks' بحيث كل مهمة لها: 'agent' و 'input'.
        """
        
        response, _ = gemini_service.ask(prompt)
        try:
            import json, re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            plan = json.loads(json_match.group())
            tasks = plan.get("tasks", [])
        except:
            return {"status": "error", "message": "Failed to generate plan"}

        # 2. التنفيذ المتوازي
        coroutines = []
        for t in tasks:
            agent_name = t.get("agent")
            agent_input = t.get("input", {})
            agent = self.registry.get(agent_name)
            
            if agent:
                # تحويل التشغيل المتزامن لـ coroutine
                coroutines.append(self._run_agent_async(agent, agent_input))
        
        results = await asyncio.gather(*coroutines)
        
        return {
            "status": "completed",
            "goal": goal,
            "results": results
        }

    async def _run_agent_async(self, agent: Any, input_data: dict) -> dict:
        """تشغيل الوكيل في Thread pool لمنع حظر Loop"""
        return await self.loop.run_in_executor(None, agent.run, input_data)

# Singleton
orchestrator = MasterOrchestrator()

# Initialize registry
try:
    from agents.deployment_hand import deployment_hand
    from agents.marketing_agent import marketing_agent
    from agents.accountant_agent import accountant_agent
    from agents.tool_hunter import tool_hunter
    
    orchestrator.register_agent("deployment", deployment_hand)
    orchestrator.register_agent("content", marketing_agent)
    orchestrator.register_agent("finance", accountant_agent)
    orchestrator.register_agent("tools", tool_hunter)
except ImportError:
    pass
