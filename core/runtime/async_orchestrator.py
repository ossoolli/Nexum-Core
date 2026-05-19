import asyncio
import time
from typing import Dict, Any

from core.execution_graph import ExecutionGraph, TaskNode
from core.runtime.message_bus import message_bus
from core.runtime.tools import execute_agent_tool

class AsyncOrchestrator:
    """
    Async Runtime Orchestrator
    نواة التنفيذ اللامركزية عبر AsyncIO Event Loop
    بديل عن الـ Threading، يوفر كفاءة، Swarm Routing، وتعافي من الأخطاء.
    """
    def __init__(self):
        self.active_graphs: Dict[str, ExecutionGraph] = {}
        self.running_tasks = set()

    async def execute_graph(self, graph: ExecutionGraph):
        """تسجيل وإدارة دورة حياة الـ Execution Graph"""
        self.active_graphs[graph.protocol_id] = graph
        await message_bus.emit_event("PROTOCOL_STARTED", {"protocol_id": graph.protocol_id})
        
        # تحفيز الجدولة الأولية
        await self._schedule_ready_nodes(graph)

    async def _schedule_ready_nodes(self, graph: ExecutionGraph):
        """جدولة العقد (Tasks) الجاهزة للتنفيذ"""
        if graph.is_completed() or graph.is_failed():
            await message_bus.emit_event("PROTOCOL_FINISHED", {
                "protocol_id": graph.protocol_id,
                "status": "COMPLETED" if graph.is_completed() else "FAILED"
            })
            return

        ready_tasks = graph.get_executable_nodes()
        for task in ready_tasks:
            # بدء التنفيذ بشكل غير متزامن
            task_task = asyncio.create_task(self._process_task_node(graph, task))
            self.running_tasks.add(task_task)
            task_task.add_done_callback(self.running_tasks.discard)

    async def _process_task_node(self, graph: ExecutionGraph, task: TaskNode):
        """تنفيذ المهمة عبر الوكيل وتسجيل حالتها"""
        task.status = "RUNNING"
        task.attempts += 1
        task.started_at = time.time()
        
        await message_bus.emit_event("TASK_STARTED", {
            "protocol_id": graph.protocol_id,
            "task_id": task.task_id,
            "agent_id": task.agent_id
        })

        try:
            # توجيه المهمة للوكيل عبر الـ Mailbox للحفاظ على تدفق الرسائل
            await message_bus.route_task(task.agent_id, {"task_id": task.task_id, "action": task.action})
            
            # تنفيذ فعلي للأداة
            result = await execute_agent_tool(task.action, task.params)
            
            if result.get("status") == "error":
                raise Exception(result.get("error", "Unknown tool execution error"))
                
            task.result = result
            task.completed_at = time.time()
            task.status = "COMPLETED"
            
            await message_bus.emit_event("TASK_COMPLETED", {
                "task_id": task.task_id,
                "agent_id": task.agent_id,
                "duration": task.completed_at - task.started_at
            })
            
            # جدولة باقي العقد بعد انتهاء هذه
            await self._schedule_ready_nodes(graph)
            
        except Exception as e:
            await self._handle_task_failure(graph, task, str(e))

    async def _handle_task_failure(self, graph: ExecutionGraph, task: TaskNode, error: str):
        """استراتيجية التعافي والـ Retry"""
        task.error = error
        if task.attempts <= task.max_retries:
            task.status = "PENDING"
            await message_bus.emit_event("TASK_RETRY", {
                "task_id": task.task_id,
                "attempts": task.attempts,
                "error": error
            })
            # تأخير الـ Retry عبر Async
            await asyncio.sleep(2 * task.attempts)
            await self._schedule_ready_nodes(graph) # أعطِ فرصة ليعاد التقاطها
        else:
            task.status = "FAILED"
            await message_bus.send_to_dead_letter(task.__dict__, error)
            await message_bus.emit_event("TASK_FAILED", {
                "task_id": task.task_id,
                "error": error
            })
            # إنهاء الـ Graph بحالة فشل
            await self._schedule_ready_nodes(graph)

async_orchestrator = AsyncOrchestrator()
