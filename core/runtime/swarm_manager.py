import asyncio
import uuid
from typing import Dict, Any, List

from core.agent_registry import agent_registry
from core.runtime.message_bus import message_bus


class SwarmManager:
    """
    Swarm Manager (Actual Implementation)
    المسؤول الحقيقي عن توليد وإدارة وإنهاء الوكلاء وتوزيع المهام
    """
    def __init__(self):
        self.active_swarms: Dict[str, Dict[str, Any]] = {}

    async def spawn_agent(self, role: str, capabilities: List[str] = None, parent_id: str = None) -> Dict[str, Any]:
        """توليد وكيل جديد وإدراجه في السجل والبث الحي"""
        new_id = f"ag_{uuid.uuid4().hex[:6]}"
        agent_def = agent_registry.register_agent(
            agent_id=new_id,
            name=f"Worker {new_id[:4]}",
            role=role,
            capabilities=capabilities or [],
            tools=["shell_execute", "read_file"],  # Default safe tools
        )
        
        # ربطه بوالد إذا لزم الأمر
        if parent_id:
            agent_def["parent_id"] = parent_id
            
        self.active_swarms[new_id] = agent_def
        
        # بث حدث حي للبوابة
        await message_bus.emit_event("AGENT_SPAWNED", {"agent": agent_def})
        print(f"🧬 [Swarm] Spawned new agent: {new_id} ({role})")
        return agent_def

    async def terminate_agent(self, agent_id: str) -> bool:
        """إنهاء وكيل وإزالته من الـ runtime"""
        if agent_id in self.active_swarms:
            del self.active_swarms[agent_id]
            # تحديث الحالة في Registry
            if agent_id in agent_registry.agents:
                agent_registry.agents[agent_id]["status"] = "terminated"
                agent_registry._save_registry()
                
            await message_bus.emit_event("AGENT_TERMINATED", {"agent_id": agent_id})
            print(f"💀 [Swarm] Terminated agent: {agent_id}")
            return True
        return False

    async def assign_task(self, agent_id: str, task_payload: Dict[str, Any]) -> bool:
        """إرسال مهمة تحديداً لهذا الوكيل عبر الـ message_bus"""
        if agent_id not in self.active_swarms and agent_id not in agent_registry.agents:
            return False
        
        await message_bus.route_task(agent_id, task_payload)
        await message_bus.emit_event("TASK_ASSIGNED", {
            "agent_id": agent_id,
            "task": task_payload
        })
        return True

    def get_children(self, parent_id: str) -> List[Dict[str, Any]]:
        """جلب جميع الوكلاء الفرعيين لوكيل أب"""
        return [ag for ag in self.active_swarms.values() if ag.get("parent_id") == parent_id]


swarm_manager = SwarmManager()
