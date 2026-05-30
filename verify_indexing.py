import sqlite3

import os
project_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(project_dir, "storage", "sovereign_memory.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM memories")
count = cursor.fetchone()[0]
print(f"Total memories: {count}")
cursor.execute("SELECT * FROM memories LIMIT 5")
for row in cursor.fetchall():
    print(row)
conn.close()
