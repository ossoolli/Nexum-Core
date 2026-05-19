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
        
        # حقن قاعدة "العزل" في عقل النظام
        prompt = f"""
        Objective: {goal}
        SYSTEM RULE: Always place new applications in subdirectories under: /home/madarmutaz/Mutaz-dev/registry/apps/
        
        Available Tools:
        {json.dumps(tools_schema, ensure_ascii=False)}
        
        Return ONLY a JSON object:
        {{
          "tasks": [
            {{
              "task_id": "t1",
              "action": "write_file",
              "params": {{"filepath": "registry/apps/[app-name]/app.py", "content": "..."}},
              "dependencies": []
            }}
          ]
        }}
        """
        
        res_text, _ = self.llm.ask(prompt)
        try:
            match = re.search(r'(\{.*\})', res_text, re.DOTALL)
            json_str = match.group(1) if match else res_text
            plan_data = json.loads(json_str)
        except:
            raise Exception(f"Failed to parse plan")

        graph = ExecutionGraph(protocol_id=protocol_id)
        for t in plan_data.get("tasks", []):
            node = TaskNode(
                task_id=t.get("task_id", "step"),
                agent_id="agent_docker",
                action=t.get("action", ""),
                params=t.get("params", {}),
                retries=2
            )
            graph.add_node(node)
        return graph
