import yaml
import re
from typing import Any, Dict, List
import core.sovereign_execution_gateway as gateway

class YAMLProtocolEngine:
    def __init__(self):
        self.variables = {}

    def load_protocol(self, yaml_path: str) -> Dict[str, Any]:
        with open(yaml_path, 'r') as f:
            return yaml.safe_load(f)

    def _replace_variables(self, command: str) -> str:
        # Pattern to find {{variable_name}}
        pattern = re.compile(r"\{\{(.*?)\}\}")
        
        def replacer(match):
            var_name = match.group(1).strip()
            return str(self.variables.get(var_name, match.group(0)))
        
        return pattern.sub(replacer, command)

    def execute_workflow(self, workflow_data: Dict[str, Any]):
        steps = workflow_data.get('steps', {})
        results = {}

        # Basic sequential execution for now
        for step_id, step_info in steps.items():
            command = self._replace_variables(step_info.get('command', ''))
            print(f"Executing {step_id}: {command}")
            
            # Secure execution via Gateway
            try:
                result = gateway.execute_command(command)
                results[step_id] = result
                # Store stdout in variables
                if 'stdout' in result:
                    self.variables[f"result_{step_id}"] = result['stdout'].strip()
            except Exception as e:
                print(f"Error executing {step_id}: {e}")
                raise e

        return results
