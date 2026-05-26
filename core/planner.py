# -*- coding: utf-8 -*-
"""
core/planner.py
NEXUM AI Planner -- المخطط الذكي والسيادي (v7.2.5)
=====================================================
يحول الأهداف النصية إلى مخططات تنفيذ (Execution Graph) قابلة للتشغيل:
- معالج تنظيف وتفكيك JSON متقدم لمنع هفوات الـ LLM
- ترسيخ للمسارات (Path Grounding) مع حماية ضد ثغرات التخطي
- دمج خوارزمية DFS لكشف الحلقات التكرارية (Cycle Detection)
- التكامل مع الذاكرة السيادية وأولويات المطور
"""

import os
import json
import re
import uuid
from typing import Optional, List, Dict, Any
from core.execution_graph import ExecutionGraph, TaskNode

# تحديد مسار جذر المشروع الفعلي
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AIPlanner:
    """مخطط المهام السيادي. يحول الأهداف النصية إلى خطط تنفيذ مدققة."""

    def __init__(self, llm, sovereign_memory=None):
        self.llm = llm
        self.memory = sovereign_memory

        # مصفوفة المسارات المسموح بها
        self.ALLOWED_BASE_PATHS = {
            "apps":    os.path.realpath(os.path.join(BASE_DIR, "registry", "apps")),
            "bots":    os.path.realpath(os.path.join(BASE_DIR, "registry", "bots")),
            "agents":  os.path.realpath(os.path.join(BASE_DIR, "registry", "agents")),
            "storage": os.path.realpath(os.path.join(BASE_DIR, "storage")),
            "docs":    os.path.realpath(os.path.join(BASE_DIR, "storage", "docs")),
            "tmp":     os.path.realpath(os.path.join(BASE_DIR, "storage", "temp")),
        }

        for path in self.ALLOWED_BASE_PATHS.values():
            os.makedirs(path, exist_ok=True)

    def generate_execution_graph(self, goal: str, protocol_id: str) -> ExecutionGraph:
        """يولد مخطط تنفيذ ذكي ومترابط لخطوات العمل."""

        # 1. دمج سياق الذاكرة السيادية
        priorities_context = ""
        if self.memory:
            try:
                priorities_context = f"\nCurrent Active Priorities Context:\n{self.memory.get_full_context()}"
            except Exception as e:
                print(f"[Planner Warning] Failed to merge sovereign memory context: {e}")

        prompt = f"""You are the task planner for NEXUM OS v7.2.
Your single job is to analyze the user's request and construct a valid JSON execution plan.

Environment Parameters:
- Base path: {BASE_DIR}
- Project storage paths: {json.dumps(self.ALLOWED_BASE_PATHS)}
- Authorized tools: write_file, execute_bash, read_file, list_directory, search_web, fetch_webpage

Architectural Hierarchy Guide:
1. Applications and web assets MUST be mapped to: registry/apps/<project_name>/
2. Active Custom Bots MUST be stored under: registry/bots/<bot_name>/
3. Internal Documents and System Notes: storage/docs/
4. All temporary actions and intermediate logs: storage/temp/

{priorities_context}

Return structure MUST be a valid JSON representation matching this exact layout:
{{
  "tasks": [
    {{
      "task_id": "step_1",
      "action": "write_file",
      "params": {{"filepath": "registry/apps/my-app/app.py", "content": "..."}}
    }},
    {{
      "task_id": "step_2",
      "action": "execute_bash",
      "params": {{"cmd": "python3 registry/apps/my-app/app.py"}},
      "depends_on": ["step_1"]
    }}
  ]
}}

IMPORTANT: When creating a system command step, ALWAYS name the parameter 'cmd' to match the execution engine framework.
Keep plans flat, clean and minimal. Avoid deeply nested directory structures for simple scripts.
Goal: {goal}
JSON Output:"""

        res, _ = self.llm.ask(prompt)
        parsed_data = self._robust_json_parse(res)

        # بناء هيكل خطة التنفيذ
        graph = ExecutionGraph(protocol_id=protocol_id)
        tasks = parsed_data.get('tasks', [])

        if not tasks:
            raise Exception("Planner Error: Generated plan contains no executable tasks.")

        # 2. فحص الدورة التكرارية (Cycle Detection)
        self._verify_acyclic_dependency(tasks)

        for t in tasks:
            tid = t.get('task_id', f"task_{uuid.uuid4().hex[:4]}")
            action = t.get('action', 'execute_bash')
            params = t.get('params', {})

            # ترسيخ المسارات
            params = self._ground_params(params)

            node = TaskNode(
                task_id=tid,
                agent_id='agent_master',
                action=action,
                params=params
            )

            # تسجيل التبعيات
            for dep in t.get('depends_on', []):
                node.add_dependency(dep)

            graph.add_node(node)

        return graph

    # ─── Backward compatibility alias ───
    def plan(self, goal: str, protocol_id: str) -> ExecutionGraph:
        """اسم مستعار للتوافق الرجعي."""
        return self.generate_execution_graph(goal, protocol_id)

    def _robust_json_parse(self, raw_text: str) -> dict:
        """ينظف ويفكك استجابة الـ LLM لانتشال الـ JSON بشكل مضاد للأخطاء."""
        if not raw_text:
            return {"tasks": []}

        cleaned = raw_text.strip()

        # إزالة علامات الأكواد ومحددات ماركداون
        cleaned = re.sub(r'^```(?:json)?\s*\n?', '', cleaned)
        cleaned = re.sub(r'\n?```\s*$', '', cleaned)
        cleaned = cleaned.strip()

        # محاولة الفك المباشر
        try:
            result = json.loads(cleaned)
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass

        # محاولة استخراج أول كائن JSON من النص
        try:
            match = re.search(r'\{[\s\S]*\}', cleaned)
            if match:
                result = json.loads(match.group())
                if isinstance(result, dict):
                    return result
        except (json.JSONDecodeError, AttributeError):
            pass

        # محاولة استخراج مصفوفة tasks مباشرة
        try:
            match = re.search(r'\[[\s\S]*\]', cleaned)
            if match:
                tasks = json.loads(match.group())
                if isinstance(tasks, list):
                    return {"tasks": tasks}
        except (json.JSONDecodeError, AttributeError):
            pass

        # إصلاح الفاصلات الزائدة (Trailing Commas)
        try:
            fixed = re.sub(r',\s*([}\]])', r'\1', cleaned)
            result = json.loads(fixed)
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass

        print(f"[Planner JSON Error] Failed to parse LLM response. Raw preview: {cleaned[:200]}")
        return {"tasks": []}

    def _ground_params(self, params: dict) -> dict:
        """ترسيخ المسارات وعزلها لحماية البيئة."""
        path_keys = ['filepath', 'file_path', 'path', 'directory', 'output', 'destination']

        for key in path_keys:
            if key in params and isinstance(params[key], str):
                raw_path = params[key]

                # تجاهل المسارات المطلقة التي تشير لخارج المشروع
                if os.path.isabs(raw_path):
                    resolved = os.path.realpath(raw_path)
                else:
                    resolved = os.path.realpath(os.path.join(BASE_DIR, raw_path))

                # فحص الأمان: هل المسار يقع ضمن حدود المشروع؟
                base_realpath = os.path.realpath(BASE_DIR)
                if not resolved.startswith(base_realpath):
                    # إعادة التوجيه إلى مجلد temp
                    safe_name = os.path.basename(raw_path)
                    resolved = os.path.join(self.ALLOWED_BASE_PATHS['tmp'], safe_name)
                    print(f"[Planner Security] Path '{raw_path}' outside project. Redirected to: {resolved}")

                params[key] = resolved

        return params

    def _verify_acyclic_dependency(self, tasks: list) -> None:
        """فحص DFS لكشف الحلقات التكرارية (Cycle Detection) ومنع Deadlocks."""
        # بناء قائمة المجاورة
        graph = {}
        for t in tasks:
            tid = t.get('task_id', '')
            graph[tid] = t.get('depends_on', [])

        visited = set()
        in_stack = set()

        def dfs(node_id: str) -> None:
            visited.add(node_id)
            in_stack.add(node_id)

            for dep in graph.get(node_id, []):
                if dep in in_stack:
                    raise Exception(
                        f"Planner Cycle Detected: {node_id} -> {dep}. "
                        f"This would cause a deadlock."
                    )
                if dep not in visited:
                    dfs(dep)

            in_stack.discard(node_id)

        for tid in graph:
            if tid not in visited:
                dfs(tid)
