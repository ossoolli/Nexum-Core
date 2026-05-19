import os, json, re, uuid # تمت إضافة uuid هنا
from core.execution_graph import ExecutionGraph, TaskNode

class AIPlanner:
    def __init__(self, llm): self.llm = llm
    def generate_execution_graph(self, goal, protocol_id):
        prompt = f"""
        Objective: {goal}
        Return ONLY valid JSON:
        {{
          "tasks": [
            {{
              "task_id": "step_1",
              "action": "run_host_terminal",
              "params": {{"command": "python3 core/search_engine.py 'سعر الدولار اليوم'"}}
            }}
          ]
        }}
        """
        res, _ = self.llm.ask(prompt)
        try:
            match = re.search(r'(\{.*\})', res, re.DOTALL)
            data = json.loads(match.group(1))
            graph = ExecutionGraph(protocol_id=protocol_id)
            for t in data.get('tasks', []):
                # الأن لن يحدث خطأ name 'uuid'
                tid = t.get('task_id', f"task_{uuid.uuid4().hex[:4]}")
                graph.add_node(TaskNode(task_id=tid, agent_id='master', action=t.get('action'), params=t.get('params')))
            return graph
        except Exception as e:
            raise Exception(f"خطأ في معالجة المخطط: {str(e)}")
