import asyncio
from typing import Dict, Any

class RuntimeMessageBus:
    """
    Asynchronous Message Queue Layer (Event-Driven Runtime)
    يربط النواة بالوكلاء ويدير طوابير المهام والأحداث والأعطال.
    """
    def __init__(self):
        # طابور المهام العام للتنفيذ
        self.task_queue: asyncio.Queue = asyncio.Queue()
        # بريد خاص بكل وكيل (Mailboxes)
        self.agent_mailboxes: Dict[str, asyncio.Queue] = {}
        # الأحداث التي لم تكتمل بنجاح
        self.dead_letter_queue: asyncio.Queue = asyncio.Queue()
        # قناة بث للأحداث الحية للـ UI
        self.event_stream: asyncio.Queue = asyncio.Queue()

    def get_mailbox(self, agent_id: str) -> asyncio.Queue:
        """يسترجع أو ينشئ بريداً خاصاً لوكيل محدد"""
        if agent_id not in self.agent_mailboxes:
            self.agent_mailboxes[agent_id] = asyncio.Queue()
        return self.agent_mailboxes[agent_id]

    async def route_task(self, agent_id: str, payload: Dict[str, Any]):
        """توجيه مهمة للوكيل المناسب (Agent Coordination)"""
        if not agent_id:
            # إذا لم يُحدد وكيل يتم إلقاؤه في الطابور العام للـ Swarm لالتقاطه
            await self.task_queue.put(payload)
        else:
            queue = self.get_mailbox(agent_id)
            await queue.put(payload)

    async def emit_event(self, event_type: str, data: Dict[str, Any]):
        """بث حدث للـ React UI والـ Websocket Gateway"""
        event = {"type": event_type, "data": data}
        await self.event_stream.put(event)

    async def send_to_dead_letter(self, task: Dict[str, Any], reason: str):
        """المهام التي تفشل نهائياً تُرسل هنا لتحليلها لاحقاً"""
        await self.dead_letter_queue.put({"task": task, "reason": reason})

message_bus = RuntimeMessageBus()
