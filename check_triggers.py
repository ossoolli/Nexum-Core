import sqlite3

db_path = "/home/madarmutaz/.hermes/state.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger' AND tbl_name='memories';")
triggers = cursor.fetchall()
print(f"Triggers for memories: {triggers}")

conn.close()
