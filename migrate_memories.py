import sys
import sqlite3
import os

# Merge sovereign_memory.db into ~/.hermes/state.db
project_dir = os.path.dirname(os.path.abspath(__file__))
source_db = os.path.join(project_dir, "storage", "sovereign_memory.db")
target_db = os.path.expanduser("~/.hermes/state.db")

src = sqlite3.connect(source_db)
dst = sqlite3.connect(target_db)

cursor_src = src.cursor()
cursor_src.execute("SELECT role, content FROM memories")

for row in cursor_src.fetchall():
    dst.execute("INSERT INTO memories (role, content) VALUES (?, ?)", row)

dst.commit()
dst.close()
src.close()
print("Migration complete.")
