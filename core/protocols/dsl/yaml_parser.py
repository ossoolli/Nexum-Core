import yaml
from typing import Dict, Any

class ProtocolDSLEngine:
    """
    Sovereign Protocol DSL Engine
    يقوم بتحليل وقراءة بروتوكولات (YAML) لتحويلها إلى Execution Graphs
    تتضمن سياسات الـ Trigger, Agents, Retry, و الـ Rollback
    """
    def parse_protocol(self, yaml_content: str) -> Dict[str, Any]:
        """قراءة وتحليل DSL Protocol"""
        try:
            protocol = yaml.safe_load(yaml_content)
            
            # Validation logic
            if "protocol" not in protocol:
                raise ValueError("Missing 'protocol' root block.")
                
            config = protocol["protocol"]
            return {
                "trigger": config.get("trigger", "manual"),
                "agents": config.get("agents", []),
                "retry_policy": config.get("retry", 0),
                "rollback_enabled": config.get("rollback", False),
                "steps": config.get("steps", [])
            }
        except Exception as e:
            raise ValueError(f"Invalid Protocol DSL: {str(e)}")

dsl_engine = ProtocolDSLEngine()
