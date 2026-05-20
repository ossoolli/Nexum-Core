import json
import os
from pathlib import Path

# Placeholder for future multi-layered memory
class MemoryManager:
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
    def save(self, data):
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self):
        if not self.storage_path.exists():
            return {}
        with open(self.storage_path, "r", encoding="utf-8") as f:
            return json.load(f)
