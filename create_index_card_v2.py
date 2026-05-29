import sqlite3

def create_system_memory_index():
    # Use the database identified in the storage directory
    db_path = "/home/madarmutaz/Nexum-Core/storage/sovereign_memory.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check table name
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables: {tables}")
    
    # Assuming 'memories' or similar based on context
    index_summary = """
    # System Memory Index - Nexum-Core
    
    This memory contains indexed project files, documentation, and logs to provide context-aware recall for the Nexum-Core agent.
    
    - Workspace: /home/madarmutaz/Nexum-Core
    - Core Logic: /core/ and /nexum/ directories
    - Documentation: /docs/ and README.md
    - Memory Engine: FTS5 integrated via SovereignMemory
    - Logs: /storage/logs/ (evolution.log tracks indexing history)
    """
    
    # Try inserting into a likely table name based on 'sovereign_memory'
    try:
        cursor.execute("INSERT OR REPLACE INTO memories (role, content) VALUES (?, ?)", 
                       ("system_memory_index", index_summary))
        conn.commit()
        print("System Memory Index card created in 'memories' table.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_system_memory_index()
