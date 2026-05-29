import sys
import os

# Add the project directory to path
sys.path.append('/home/madarmutaz/Nexum-Core')

from nexum.memory.store import SovereignMemoryStore

def index_all_logs():
    # Use the persistent database
    db_path = "/home/madarmutaz/Nexum-Core/storage/sovereign_memory.db"
    store = SovereignMemoryStore(db_path=db_path)
    
    log_dir = "/home/madarmutaz/Nexum-Core/storage/logs/"
    
    for root, dirs, files in os.walk(log_dir):
        for filename in files:
            if filename.endswith('.log'):
                path = os.path.join(root, filename)
                print(f"Indexing {path}...")
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        for line in lines:
                            line = line.strip()
                            if line:
                                # Index as system role
                                store.add_memory(role="system_log", content=f"[{filename}] {line}")
                    print(f"Finished indexing {filename}")
                except Exception as e:
                    print(f"Error indexing {filename}: {e}")

if __name__ == "__main__":
    index_all_logs()
