import sys
import os
import sqlite3
import glob

# Add the project directory to path
sys.path.append('/home/madarmutaz/Nexum-Core')

from nexum.memory.store import SovereignMemoryStore

def index_logs():
    # Use the persistent database
    db_path = "/home/madarmutaz/Nexum-Core/storage/sovereign_memory.db"
    store = SovereignMemoryStore(db_path=db_path)
    
    log_files = [
        'evolution.log', 'sentinel.log', 'watchdog.log', 
        'out.log', 'api_out.log', 'api_err.log', 'err.log', 
        'terminal.log', 'recovery.log'
    ]
    
    log_dir = "/home/madarmutaz/Nexum-Core/storage/logs/"
    
    for log_filename in log_files:
        path = os.path.join(log_dir, log_filename)
        if os.path.exists(path):
            print(f"Indexing {log_filename}...")
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if line:
                        # Index as system role
                        store.add_memory(role="system_log", content=line)
            print(f"Finished indexing {log_filename}")

if __name__ == "__main__":
    index_logs()
