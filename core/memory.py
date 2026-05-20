import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_FILE = os.path.join(BASE_DIR, "registry", "system_memory.json")

def save_memory(data):
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"indicators": {}, "apps": []}
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)
