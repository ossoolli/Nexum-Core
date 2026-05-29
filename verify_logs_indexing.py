import sys
import sqlite3

def verify_indexed_logs():
    db_path = "/home/madarmutaz/Nexum-Core/storage/sovereign_memory.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check count of log entries
    cursor.execute("SELECT count(*) FROM memories WHERE role = 'system_log'")
    count = cursor.fetchone()[0]
    print(f"Total system_log entries indexed: {count}")
    
    # Check some samples
    cursor.execute("SELECT content FROM memories WHERE role = 'system_log' LIMIT 5")
    samples = cursor.fetchall()
    print("Samples:")
    for sample in samples:
        print(f"- {sample[0][:50]}...")
        
    conn.close()

if __name__ == "__main__":
    verify_indexed_logs()
