import os
import yaml
from datetime import datetime

class ProtocolCompiler:
    """
    Autonomous Protocol Compiler (Layer 3)
    يحول مسارات التنفيذ (Execution Graphs) العابرة التي يولدها الذكاء الاصطناعي
    إلى بروتوكولات دائمة بصيغة YAML يمكن إعادة تدويرها وتحليلها وعرضها كنظام تشغيلي.
    """
    def __init__(self):
        self.protocols_dir = os.path.join(os.path.dirname(__file__), "..", "protocols")
        os.makedirs(self.protocols_dir, exist_ok=True)
        
    def compile_graph_to_yaml(self, graph, goal: str):
        """
        The Blueprint of Sovereign Execution.
        """
        protocol = {
            "api_version": "nexum/v1alpha",
            "kind": "Protocol",
            "metadata": {
                "id": graph.protocol_id,
                "created_at": datetime.now().isoformat(),
                "goal": goal,
                "status": "compiled"
            },
            "spec": {
                "tasks": []
            }
        }
        
        for task in graph.nodes.values():
            task_dict = {
                "id": task.task_id,
                "agent": task.agent_id,
                "action": task.action,
                "params": task.params,
                "retries": task.max_retries,
                "depends_on": task.dependencies
            }
            protocol["spec"]["tasks"].append(task_dict)
            
        yaml_path = os.path.join(self.protocols_dir, f"{graph.protocol_id}.yaml")
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(protocol, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            
        return yaml_path
        
    def load_protocol_from_yaml(self, yaml_path: str):
        with open(yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

# Singleton
protocol_compiler = ProtocolCompiler()
