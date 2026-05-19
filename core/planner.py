import os
import json
import re
from core.execution_graph import ExecutionGraph, TaskNode

class AIPlanner:
    def __init__(self, gemini_service):
        self.llm = gemini_service

    def generate_execution_graph(self, goal: str, protocol_id: str) -> ExecutionGraph:
        from core.tool_registry import tool_registry
        tools_schema = tool_registry.get_all_tools_schema()
        
        prompt = f"""
        Objective: {goal}
        Base Directory: /home/madarmutaz/Mutaz-dev
        
        Available Tools:
        {json.dumps(tools_schema, ensure_ascii=False)}
        
        Instruction: Create a technical plan to achieve the objective.
        Return ONLY a JSON object:
        {{
          "tasks": [
            {{
              "task_id": "t1",
              "agent_id": "agent_backend",
              "action": "write_file",
              "params": {{"filepath": "agents/mutaz.py", "content": "#code"}},
              "dependencies": []
            }}
          ]
        }}
        """
        
        res_text, _ = self.llm.ask(prompt)
        
        # استخراج الـ JSON بدقة
        try:
            match = re.search(r'(\{.*\})', res_text, re.DOTALL)
            json_str = match.group(1) if match else res_text
            plan_data = json.loads(json_str)
        except:
            raise Exception(f"Failed to parse AI Plan: {res_text[:100]}")

        graph = ExecutionGraph(protocol_id=protocol_id)
        for t in plan_data.get("tasks", []):
            node = TaskNode(
                task_id=t.get("task_id", "step"),
                agent_id=t.get("agent_id", "agent_general"),
                action=t.get("action", ""),
                params=t.get("params", {}),
                retries=2
            )
            for d in t.get("dependencies", []):
                node.add_dependency(d)
            graph.add_node(node)
            
        return graph
