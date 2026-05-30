import os
import threading
import time
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Load environment variables to ensure we have the DB encryption key
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, ".env"), override=True)

import sqlite3

db_key = os.getenv("NEXUM_DB_ENCRYPTION_KEY")
_use_cipher = False
cipher_sqlite3 = None

if db_key:
    try:
        from pysqlcipher3 import dbapi2 as cipher_sqlite3
        _use_cipher = True
    except ImportError:
        pass

class SovereignMemoryStore:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.path.join(os.path.expanduser("~"), ".hermes", "state.db")
        self.lock = threading.RLock()
        self._init_db()

    def _init_db(self):
        with self.lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS memories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        role TEXT,
                        content TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # Enable FTS5 for efficient text searching
                conn.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
                        content,
                        content='memories',
                        content_rowid='id'
                    )
                """)
                # Create triggers to keep FTS index in sync
                conn.execute("""
                    CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
                      INSERT INTO memories_fts(rowid, content) VALUES (new.id, new.content);
                    END;
                """)
                conn.execute("""
                    CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
                      INSERT INTO memories_fts(memories_fts, rowid, content) VALUES('delete', old.id, old.content);
                    END;
                """)
                conn.execute("""
                    CREATE TRIGGER IF NOT EXISTS memories_au AFTER UPDATE ON memories BEGIN
                      INSERT INTO memories_fts(memories_fts, rowid, content) VALUES('delete', old.id, old.content);
                      INSERT INTO memories_fts(rowid, content) VALUES (new.id, new.content);
                    END;
                """)
                conn.commit()
            finally:
                conn.close()

    def _get_connection(self):
        # Use simple retry-wait for locked database
        while True:
            try:
                # Plaintext databases (like memory.db) should utilize standard sqlite3 directly to support FTS5
                if "memory.db" in self.db_path:
                    return sqlite3.connect(self.db_path, timeout=10)

                if _use_cipher and db_key and cipher_sqlite3:
                    # Try SQLCipher 3 first
                    safe_key = db_key.replace("'", "''")
                    try:
                        conn = cipher_sqlite3.connect(self.db_path, timeout=10)
                        cursor = conn.cursor()
                        cursor.execute(f"PRAGMA key = '{safe_key}';")
                        cursor.execute("PRAGMA cipher_compatibility = 3;")
                        cursor.execute("SELECT 1 FROM sqlite_master LIMIT 1;")
                        return conn
                    except Exception:
                        try:
                            # Try SQLCipher 4
                            conn = cipher_sqlite3.connect(self.db_path, timeout=10)
                            cursor = conn.cursor()
                            cursor.execute(f"PRAGMA key = '{safe_key}';")
                            cursor.execute("PRAGMA cipher_compatibility = 4;")
                            cursor.execute("SELECT 1 FROM sqlite_master LIMIT 1;")
                            return conn
                        except Exception:
                            # Plaintext fallback (operate as standard SQLite without key)
                            return sqlite3.connect(self.db_path, timeout=10)
                else:
                    return sqlite3.connect(self.db_path, timeout=10)
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    time.sleep(0.1)
                else:
                    raise

    def add_memory(self, role: str, content: str):
        with self.lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO memories (role, content) VALUES (?, ?)", (role, content))
                conn.commit()
            finally:
                conn.close()

    def search_memory(self, query: str) -> List[Dict[str, Any]]:
        with self.lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                # FTS5 query syntax: match against the indexed content
                cursor.execute("""
                    SELECT m.role, m.content, m.timestamp 
                    FROM memories m
                    JOIN memories_fts fts ON m.id = fts.rowid
                    WHERE memories_fts MATCH ?
                    ORDER BY m.timestamp DESC
                """, (f'"{query}"',))
                return [{"role": r[0], "content": r[1], "timestamp": r[2]} for r in cursor.fetchall()]
            finally:
                conn.close()

    def summarize_old_memories(self, threshold: int = 1000):
        """Compress older memories into a single entry to save space."""
        with self.lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM memories")
                count = cursor.fetchone()[0]
                if count > threshold:
                    # Very simple compression: keep newest N, summarize oldest
                    # This is just a stub for now as requested
                    pass
            finally:
                conn.close()

    def add_memories_batch(self, memories: List[tuple]):
        """Insert multiple memory entries efficiently in a single batch."""
        if not memories:
            return
        with self.lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.executemany("INSERT INTO memories (role, content) VALUES (?, ?)", memories)
                conn.commit()
            finally:
                conn.close()
