import json
import os

MEMORY_FILE = "/home/madarmutaz/Mutaz-dev/registry/system_memory.json"

def save_memory(data):
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"indicators": {}, "apps": []}
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)
