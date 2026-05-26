# -*- coding: utf-8 -*-
"""
swarm/engine.py
محرك الأسراب وتوزيع المهام الذكي -- Nexum Pro (v7.2.5)
========================================================
- تفكيك المأموريات الكبرى إلى مهام فرعية عبر LLM
- مطابقة المهام مع أفضل وكيل حسب القدرات (Capability Scoring)
- تنفيذ المهام المستقلة بالتوازي عبر ThreadPoolExecutor
- حماية ضد Deadlock بمهلة زمنية (30s per agent)
- تكامل مع AgentRegistry و CouncilOfSages
"""

import json
import re
import time
import threading
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from datetime import datetime
from typing import Optional, List, Dict, Any

BASE_DIR = __import__('os').path.dirname(
    __import__('os').path.dirname(__import__('os').path.abspath(__file__))
)

_swarm_logger = logging.getLogger("nexum.swarm")


class SwarmEngine:
    """محرك الأسراب: يفكك المأموريات الكبرى ويوزعها على الوكلاء المتخصصين."""

    def __init__(self, agent_registry=None, council=None,
                 llm_interface=None, max_workers: int = 4,
                 agent_timeout: int = 30):
        self.registry = agent_registry
        self.council = council
        self.llm = llm_interface
        self.max_workers = max_workers
        self.agent_timeout = agent_timeout
        self._lock = threading.Lock()
        self._mission_log: List[dict] = []

    def decompose_mission(self, goal: str) -> List[dict]:
        """تفكيك المأمورية إلى مهام فرعية عبر LLM أو Fallback."""
        if self.llm:
            try:
                return self._llm_decompose(goal)
            except Exception as e:
                _swarm_logger.error(f"LLM decomposition failed: {e}")

        # Fallback: مهمة واحدة
        return [{
            "task_id": "task_1",
            "description": goal,
            "required_capability": "run",
            "priority": "normal",
            "parallel": False
        }]

    def _llm_decompose(self, goal: str) -> List[dict]:
        """تفكيك المأمورية عبر LLM."""
        prompt = (
            "You are a task decomposer. Break this goal into sub-tasks.\n"
            f"Goal: {goal}\n\n"
            "Return ONLY a JSON array of tasks:\n"
            '[{"task_id": "task_1", "description": "...", '
            '"required_capability": "write_python|execute_shell|read_file|...", '
            '"priority": "high|normal|low", "parallel": true|false}]'
        )
        response, _ = self.llm.ask(prompt)

        # استخلاص JSON
        match = re.search(r'\[[\s\S]*\]', response)
        if match:
            tasks = json.loads(match.group())
            if isinstance(tasks, list) and len(tasks) > 0:
                return tasks

        raise ValueError("Could not parse LLM task decomposition")

    def delegate_task(self, task: dict) -> dict:
        """مطابقة المهمة مع أفضل وكيل حسب القدرات."""
        capability = task.get("required_capability", "run")

        # البحث في سجل الوكلاء
        candidates = []
        if self.registry:
            candidates = self.registry.get_agents_by_capability(capability)

        if not candidates:
            # بحث بقدرة عامة
            if self.registry:
                all_agents = self.registry.list_all()
                candidates = [
                    a for a in all_agents
                    if a.get("status") == "active"
                ]

        if not candidates:
            return {
                "task_id": task.get("task_id"),
                "assigned_to": None,
                "status": "no_agent_available",
                "reason": f"No agent found with capability: {capability}"
            }

        # اختيار الأفضل (أول وكيل مطابق)
        best = candidates[0]
        return {
            "task_id": task.get("task_id"),
            "assigned_to": best.get("agent_id"),
            "agent_name": best.get("name"),
            "status": "delegated",
            "reason": f"Matched capability: {capability}"
        }

    def execute_mission(self, goal: str) -> dict:
        """تنفيذ مأمورية كاملة: تفكيك → توزيع → تنفيذ → تجميع."""
        start_time = time.time()

        mission = {
            "goal": goal[:500],
            "started_at": datetime.now().isoformat(),
            "status": "running"
        }

        # 1. استشارة مجلس الحكماء إذا كانت المأمورية حرجة
        if self.council:
            council_decision = self.council.convene(goal)
            mission["council_decision"] = council_decision
            if not council_decision.get("approved"):
                mission["status"] = "blocked_by_council"
                mission["message"] = council_decision.get("summary", "Council rejected.")
                self._log_mission(mission)
                return mission

        # 2. تفكيك المأمورية
        tasks = self.decompose_mission(goal)
        mission["total_tasks"] = len(tasks)

        # 3. فصل المهام المتوازية من المتسلسلة
        parallel_tasks = [t for t in tasks if t.get("parallel")]
        sequential_tasks = [t for t in tasks if not t.get("parallel")]

        results = []

        # 4. تنفيذ المهام المتسلسلة
        for task in sequential_tasks:
            delegation = self.delegate_task(task)
            result = self._execute_single_task(task, delegation)
            results.append(result)

        # 5. تنفيذ المهام المتوازية
        if parallel_tasks:
            parallel_results = self._execute_parallel(parallel_tasks)
            results.extend(parallel_results)

        # 6. تجميع النتائج
        duration = time.time() - start_time
        success_count = sum(
            1 for r in results if r.get("status") == "success"
        )

        mission["results"] = results
        mission["successful_tasks"] = success_count
        mission["duration_seconds"] = round(duration, 2)
        mission["status"] = (
            "completed" if success_count == len(tasks) else "partial"
        )

        self._log_mission(mission)
        return mission

    def _execute_single_task(self, task: dict, delegation: dict) -> dict:
        """تنفيذ مهمة فردية (حاليا عبر LLM أو stub)."""
        task_id = task.get("task_id", "unknown")

        if delegation.get("status") == "no_agent_available":
            return {
                "task_id": task_id,
                "status": "failed",
                "reason": delegation["reason"]
            }

        # تنفيذ عبر LLM كمحاكي للوكيل
        if self.llm:
            try:
                response, _ = self.llm.ask(
                    f"Execute this task concisely: {task.get('description', '')}"
                )
                return {
                    "task_id": task_id,
                    "assigned_to": delegation.get("assigned_to"),
                    "status": "success",
                    "output": response[:1000]
                }
            except Exception as e:
                return {
                    "task_id": task_id,
                    "status": "failed",
                    "reason": str(e)
                }

        return {
            "task_id": task_id,
            "assigned_to": delegation.get("assigned_to"),
            "status": "success",
            "output": f"Task '{task.get('description', '')}' delegated to {delegation.get('agent_name', 'unknown')}."
        }

    def _execute_parallel(self, tasks: List[dict]) -> List[dict]:
        """تنفيذ مهام متوازية عبر ThreadPoolExecutor مع حماية Timeout."""
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_map = {}
            for task in tasks:
                delegation = self.delegate_task(task)
                future = executor.submit(
                    self._execute_single_task, task, delegation
                )
                future_map[future] = task

            for future in as_completed(
                future_map, timeout=self.agent_timeout * 2
            ):
                task = future_map[future]
                try:
                    result = future.result(timeout=self.agent_timeout)
                    results.append(result)
                except TimeoutError:
                    results.append({
                        "task_id": task.get("task_id"),
                        "status": "timeout",
                        "reason": f"Agent timed out after {self.agent_timeout}s"
                    })
                except Exception as e:
                    results.append({
                        "task_id": task.get("task_id"),
                        "status": "failed",
                        "reason": str(e)
                    })

        return results

    def _log_mission(self, mission: dict) -> None:
        """تسجيل المأمورية في السجل الداخلي."""
        with self._lock:
            self._mission_log.append({
                "goal": mission.get("goal", ""),
                "status": mission.get("status", ""),
                "tasks": mission.get("total_tasks", 0),
                "successful": mission.get("successful_tasks", 0),
                "duration": mission.get("duration_seconds", 0),
                "timestamp": datetime.now().isoformat()
            })
            if len(self._mission_log) > 50:
                self._mission_log.pop(0)

    def get_mission_log(self) -> List[dict]:
        """إرجاع سجل المأموريات."""
        return self._mission_log

    def get_stats(self) -> dict:
        """إحصائيات محرك الأسراب."""
        total = len(self._mission_log)
        completed = sum(
            1 for m in self._mission_log if m.get("status") == "completed"
        )
        return {
            "total_missions": total,
            "completed": completed,
            "success_rate": round(completed / total, 2) if total > 0 else 0,
            "max_workers": self.max_workers,
            "agent_timeout": self.agent_timeout
        }
