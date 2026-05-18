import os
import yaml
from datetime import datetime

def _graph_to_dict(graph):
    """Convert ExecutionGraph (custom class) to a plain dict suitable for YAML serialization.
    Expected attributes on graph:
        - protocol_id (str)
        - nodes (list of TaskNode)
    Each TaskNode is expected to have:
        - task_id
        - action
        - params (dict)
        - dependencies (list of task_id)
    """
    result = {
        "protocol_id": getattr(graph, "protocol_id", "unknown"),
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "tasks": [],
    }
    for node in getattr(graph, "nodes", []):
        task_dict = {
            "task_id": getattr(node, "task_id", None),
            "action": getattr(node, "action", None),
            "params": getattr(node, "params", {}),
            "dependencies": getattr(node, "dependencies", []),
        }
        result["tasks"].append(task_dict)
    return result

def compile_graph_to_yaml(graph, protocol_name: str):
    """Serialize an ExecutionGraph to a YAML file under the `protocols/` directory.
    The file will be named `<protocol_name>.yaml`.
    """
    # Ensure the protocols directory exists
    base_dir = os.path.dirname(os.path.abspath(__file__))
    protocols_dir = os.path.join(base_dir, "..", "protocols")
    os.makedirs(protocols_dir, exist_ok=True)

    yaml_content = _graph_to_dict(graph)
    file_path = os.path.join(protocols_dir, f"{protocol_name}.yaml")
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(yaml_content, f, allow_unicode=True, sort_keys=False)
    print(f"📄 [Protocol Compiler] Saved YAML blueprint to {file_path}")
