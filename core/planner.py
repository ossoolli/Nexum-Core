"""
🧠 NEXUM AI Planner — المخطط الذكي
====================================
يحول الأهداف النصية إلى مخططات تنفيذ (Execution Graph) قابلة للتشغيل.
"""
import json
import re
import uuid

import os
from core.execution_graph import ExecutionGraph, TaskNode

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AIPlanner:
    def __init__(self, llm):
        self.llm = llm

    def generate_execution_graph(self, goal: str, protocol_id: str) -> ExecutionGraph:
        """يولد مخطط تنفيذ من هدف نصي عبر الذكاء الاصطناعي"""

        prompt = f"""You are a task planner for an autonomous server OS.
Your ONLY job is to return a valid JSON execution plan.

Environment:
- Base directory: {BASE_DIR}
- Apps directory: {BASE_DIR}/registry/apps/
- Available tools: write_file, run_host_terminal, read_file, list_directory, search_web, fetch_webpage, run_in_sandbox

Rules:
1. ORGANIZATIONAL HIERARCHY:
   - Web Apps/Projects: registry/apps/<project_name>/
   - Custom Bots: registry/bots/<bot_name>/
   - Documentation/Notes: storage/docs/
   - Temporary/One-off files: storage/temp/
2. Paths: Prefer Relative paths (e.g., "registry/apps/my-app/main.py").
3. DO NOT create multiple folders for one small request. Be efficient and minimalist.
4. AI CONSCIOUSNESS: You are the OS itself. If a request is vague, organize it logically under one project folder.
5. Return ONLY valid JSON.

User Goal: {goal}

Return format:
{{
  "tasks": [
    {{
      "task_id": "step_1",
      "action": "write_file",
      "params": {{"filepath": "{BASE_DIR}/registry/apps/myapp/app.py", "content": "..."}}
    }},
    {{
      "task_id": "step_2", 
      "action": "run_host_terminal",
      "params": {{"command": "cd {BASE_DIR} && python3 registry/apps/myapp/app.py"}}
    }}
  ]
}}"""

        res, _ = self.llm.ask(prompt)

        # استخراج JSON من الرد
        try:
            # محاولة 1: البحث عن JSON مباشر
            match = re.search(r'\{[\s\S]*"tasks"[\s\S]*\}', res)
            if not match:
                raise ValueError("No JSON found in LLM response")

            data = json.loads(match.group(0))

        except (json.JSONDecodeError, ValueError) as parse_err:
            # محاولة 2: تنظيف وإعادة المحاولة
            try:
                cleaned = res.strip()
                # إزالة markdown code fences
                cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
                cleaned = re.sub(r'\s*```$', '', cleaned)
                data = json.loads(cleaned)
            except Exception:
                raise Exception(f"Failed to parse plan: {parse_err}\nRaw: {res[:500]}")

        # بناء الـ Execution Graph
        graph = ExecutionGraph(protocol_id=protocol_id)
        tasks = data.get('tasks', [])

        if not tasks:
            raise Exception("Plan contains no tasks")

        for t in tasks:
            tid = t.get('task_id', f"task_{uuid.uuid4().hex[:4]}")
            action = t.get('action', 'run_host_terminal')
            params = t.get('params', {})

            node = TaskNode(
                task_id=tid,
                agent_id='agent_master',
                action=action,
                params=params
            )

            # إضافة التبعيات إذا وجدت
            deps = t.get('depends_on', [])
            for dep in deps:
                node.add_dependency(dep)

            graph.add_node(node)

        return graph
