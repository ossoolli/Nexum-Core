import sqlite3

import os
db_path = os.path.join(os.path.expanduser("~"), ".hermes", "state.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f"Tables: {tables}")

# Check schema for memories_fts
if ('memories_fts',) in tables:
    cursor.execute("PRAGMA table_info(memories_fts);")
    print(f"memories_fts columns: {cursor.fetchall()}")
else:
    print("memories_fts not found")

conn.close()
