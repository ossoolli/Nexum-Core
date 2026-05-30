import os
import sys
import dotenv

# Load .env
dotenv.load_dotenv("/home/madarmutaz/Nexum-Core/.env")

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

import json

# Assuming /home/madarmutaz/.hermes/state.db is the target
DB_PATH = "/home/madarmutaz/.hermes/state.db"

def recall_memory(query: str):
    """
    Retrieves and summarizes the top 3 relevant past interactions from the database.
    """
    try:
        if not os.path.exists(DB_PATH):
            return "Memory database not found."

        conn = sqlite3.connect(DB_PATH)
        if _use_cipher and db_key:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA key = '{db_key}';")
            try:
                cursor.execute("PRAGMA cipher_compatibility = 3;")
                cursor.execute("SELECT 1 FROM sqlite_master LIMIT 1;")
            except Exception:
                cursor.execute("PRAGMA cipher_compatibility = 4;")
        cursor = conn.cursor()

        # FTS5 search (assuming a table 'memory' exists, will try to adapt)
        # We search for the query in the 'content' field if it's an FTS5 table
        # Searching generic 'state' table if FTS structure unknown
        
        query_sql = """
            SELECT snippet(memories_fts, 0, '<b>', '</b>', '...', 10) as match
            FROM memories_fts 
            WHERE memories_fts MATCH ?
            ORDER BY rank
            LIMIT 3
        """
        
        cursor.execute(query_sql, (query,))
        results = cursor.fetchall()
        
        if not results:
            return "No relevant memories found."
            
        summary = "Here are the top findings from your memory:\n"
        for i, row in enumerate(results, 1):
            summary += f"{i}. {row[0]}\n"
            
        conn.close()
        return summary
    except Exception as e:
        return f"Error accessing memory: {e}"
