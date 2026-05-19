import os
import json
import re
from core.execution_graph import ExecutionGraph, TaskNode

class AIPlanner:
    def __init__(self, llm_service):
        self.llm = llm_service

    def generate_execution_graph(self, goal, protocol_id):
        # القالب الذي يفرضه Claude على السيرفر
        prompt = f"""
        Objective: {goal}
        Environment Root: /home/madarmutaz/Mutaz-dev
        
        Available Tools: write_file, run_host_terminal, list_directory
        
        Instructions: Create a JSON execution graph. 
        Always use absolute paths based on /home/madarmutaz/Mutaz-dev.
        
        Return ONLY valid JSON:
        {{
          "tasks": [
            {{
              "task_id": "T1",
              "action": "write_file",
              "params": {{"filepath": "/home/madarmutaz/Mutaz-dev/agents/registry_manager.py", "content": "import os..."}}
            }}
          ]
        }}
        """
        res, _ = self.llm.ask(prompt)
        
        # استخراج الـ JSON
        try:
            match = re.search(r'(\{.*\})', res, re.DOTALL)
            data = json.loads(match.group(1))
            graph = ExecutionGraph(protocol_id=protocol_id)
            for t in data.get("tasks", []):
                node = TaskNode(task_id=t['task_id'], agent_id="agent_master", action=t['action'], params=t['params'])
                graph.add_node(node)
            return graph
        except Exception as e:
            raise Exception(f"Failed to compile Claude's plan: {str(e)}")

