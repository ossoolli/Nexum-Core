import sqlite3

db_path = "/home/madarmutaz/Nexum-Core/storage/sovereign_memory.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM memories")
count = cursor.fetchone()[0]
print(f"Total memories: {count}")
cursor.execute("SELECT * FROM memories LIMIT 5")
for row in cursor.fetchall():
    print(row)
conn.close()
