import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self, config: Any):
        # Expecting config to have thinker_model and executor_model
        # or defaults if not provided
        self.thinker_model = getattr(config, "thinker_model", "anthropic/claude-3.5-sonnet")
        self.executor_model = getattr(config, "executor_model", "gpt-4o-mini")
        
        # Simple keywords for routing classification
        self.thinking_keywords = [
            'plan', 'strategy', 'architecture', 'research', 'design', 
            'complex', 'analyze', 'explain', 'improve'
        ]

    def route_task(self, task_description: str) -> str:
        """
        Classify task as 'THINKING' or 'EXECUTING' and return the model
        """
        task_lower = task_description.lower()
        
        # Basic heuristic for classification
        is_thinking = any(kw in task_lower for kw in self.thinking_keywords)
        
        if is_thinking:
            logger.info(f"Task classified as THINKING: {task_description[:50]}...")
            return self.thinker_model
        else:
            logger.info(f"Task classified as EXECUTING: {task_description[:50]}...")
            return self.executor_model

# Singleton instance for general use
# In production this would be initialized with loaded config
# from config_loader import get_config
# orchestrator = Orchestrator(get_config())
