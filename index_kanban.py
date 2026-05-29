import sys
import os
import json
import sqlite3

# Add the project directory to path
sys.path.append('/home/madarmutaz/Nexum-Core')

from nexum.memory.store import SovereignMemoryStore

def index_kanban():
    db_path = "/home/madarmutaz/.hermes/state.db"
    store = SovereignMemoryStore(db_path=db_path)
    
    kanban_file = "/home/madarmutaz/Nexum-Core/storage/kanban/boards.json"
    
    if os.path.exists(kanban_file):
        print(f"Indexing {kanban_file}...")
        with open(kanban_file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                # Assuming standard board structure
                store.add_memory(role="kanban_history", content=json.dumps(data))
                print(f"Finished indexing {kanban_file}")
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")

if __name__ == "__main__":
    index_kanban()
