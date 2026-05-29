import os
import sys
from nexum.memory.store import SovereignMemoryStore

# Set path to the memory database
db_path = "/home/madarmutaz/Nexum-Core/storage/sovereign_memory/memory.db"
store = SovereignMemoryStore(db_path=db_path)

def index_files(directory, role_name):
    print(f"Indexing files in {directory} as {role_name}...")
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    indexed_content = f"Filename: {file_path}\nContent:\n{content}"
                    store.add_memory(role_name, indexed_content)
                    print(f"Indexed: {file_path}")
            except Exception as e:
                print(f"Failed to index {file_path}: {e}")

# Index logs
log_dir = "/home/madarmutaz/Nexum-Core/storage/logs"
index_files(log_dir, "log_entry")

# Index docs
doc_dir = "/home/madarmutaz/Nexum-Core/docs"
index_files(doc_dir, "documentation")

print("Indexing complete.")
