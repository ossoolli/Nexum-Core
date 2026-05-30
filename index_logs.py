import sqlite3
import os

log_dir = "/home/madarmutaz/Nexum-Core/storage/logs/"
db_path = "/home/madarmutaz/.hermes/state.db"

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
