import os
import sys
import dotenv

# Load .env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv.load_dotenv(os.path.join(BASE_DIR, ".env"))

import sqlite3

log_dir = os.path.join(BASE_DIR, "storage", "logs")
db_path = os.path.join(BASE_DIR, "storage", "sovereign_memory", "memory.db")

# Logs to index (found via search_files)
log_files = [
    "err.log", "out.log", "evolution.log", "terminal.log", "sentinel.log", "watchdog.log", "recovery.log"
]

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

for log_file in log_files:
    path = os.path.join(log_dir, log_file)
    if not os.path.exists(path):
        print(f"File not found: {path}")
        continue
    
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        if content:
            print(f"Indexing {path}...")
            # Inserting as memory entries
            cursor.execute("INSERT INTO memories (role, content) VALUES (?, ?)", ("system", f"Log file {log_file} content: {content}"))
            conn.commit()

conn.close()
print("Indexing complete.")
