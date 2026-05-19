import os, json, re
from core.execution_graph import ExecutionGraph, TaskNode

class AIPlanner:
    def __init__(self, llm): self.llm = llm
    def generate_execution_graph(self, goal, protocol_id):
        prompt = f"""
        Objective: {goal}
        Return ONLY valid JSON in this format:
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
                # التأكد من وجود المفاتيح المطلوبة لعدم حدوث KeyError
                tid = t.get('task_id', f"task_{uuid.uuid4().hex[:4]}")
                action = t.get('action', 'run_host_terminal')
                params = t.get('params', {})
                graph.add_node(TaskNode(task_id=tid, agent_id='master', action=action, params=params))
            return graph
        except Exception as e:
            raise Exception(f"JSON Parsing Error: {str(e)}")
