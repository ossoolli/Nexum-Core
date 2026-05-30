import os
import sys
import dotenv

# Load .env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv.load_dotenv(os.path.join(BASE_DIR, ".env"))

db_key = os.getenv("NEXUM_DB_ENCRYPTION_KEY")
if db_key:
    try:
        from pysqlcipher3 import dbapi2 as sqlite3
        _use_cipher = True
    except ImportError:
        import sqlite3
        _use_cipher = False
else:
    import sqlite3
    _use_cipher = False

log_dir = os.path.join(BASE_DIR, "storage", "logs")
db_path = os.path.join(BASE_DIR, "storage", "sovereign_memory", "memory.db")

# Logs to index (found via search_files)
log_files = [
    "err.log", "out.log", "evolution.log", "terminal.log", "sentinel.log", "watchdog.log", "recovery.log"
]

conn = sqlite3.connect(db_path)
if _use_cipher and db_key:
    cursor = conn.cursor()
    escaped_key = db_key.replace("'", "''")
    cursor.execute(f"PRAGMA key = '{escaped_key}';")
    try:
        cursor.execute("PRAGMA cipher_compatibility = 3;")
        cursor.execute("SELECT 1 FROM sqlite_master LIMIT 1;")
    except Exception:
        cursor.execute("PRAGMA cipher_compatibility = 4;")
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
