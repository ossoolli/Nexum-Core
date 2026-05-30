import sqlite3

def create_system_memory_index():
    import os
    db_path = os.path.join(os.path.expanduser("~"), ".hermes", "state.db")
    project_dir = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create the card in the memory store
    index_summary = f"""
    # System Memory Index - Nexum-Core
    
    This memory contains indexed project files, documentation, and logs to provide context-aware recall for the Nexum-Core agent.
    
    - Workspace: {project_dir}
    - Core Logic: /core/ and /nexum/ directories
    - Documentation: /docs/ and README.md
    - Memory Engine: FTS5 integrated via SovereignMemory
    - Logs: /storage/logs/ (evolution.log tracks indexing history)
    """
    
    cursor.execute("INSERT OR REPLACE INTO memory (key, content) VALUES (?, ?)", 
                   ("system_memory_index", index_summary))
    conn.commit()
    conn.close()
    print("System Memory Index card created.")

if __name__ == "__main__":
    create_system_memory_index()
