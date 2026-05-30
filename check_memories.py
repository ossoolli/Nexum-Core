import sqlite3

import os
db_path = os.path.join(os.path.expanduser("~"), ".hermes", "state.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(memories);")
print(f"memories columns: {cursor.fetchall()}")

conn.close()
