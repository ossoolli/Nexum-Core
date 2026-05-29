import logging
from typing import List
from nexum.gateway.base_adapter import PlatformAdapter

logger = logging.getLogger(__name__)

class GatewayManager:
    def __init__(self):
        self.adapters: List[PlatformAdapter] = []

    def register_adapter(self, adapter: PlatformAdapter):
        self.adapters.append(adapter)
        logger.info(f"Registered adapter: {adapter.__class__.__name__}")

    def run_all(self):
        for adapter in self.adapters:
            # We would likely want to run these in separate threads/tasks
            # For now, this is a skeleton
            try:
                adapter.listen()
            except Exception as e:
                logger.error(f"Error in {adapter.__class__.__name__}: {e}")
