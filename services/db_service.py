import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

class DBSyncService:
    def __init__(self):
        self.conn_str = os.getenv("DB_CONNECTION")
        self.enabled = bool(self.conn_str)
        if self.enabled:
            self.init_db()

    def get_connection(self):
        if not self.enabled:
            return None
        return psycopg2.connect(self.conn_str, cursor_factory=RealDictCursor)

    def init_db(self):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # جدول الذاكرة (Memory)
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS chat_memory (
                            user_id VARCHAR(50) PRIMARY KEY,
                            history_json JSONB NOT NULL,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """)
                    # جدول سجلات النظام (Audit Logs)
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS audit_logs (
                            id SERIAL PRIMARY KEY,
                            event_type VARCHAR(50),
                            payload JSONB,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """)
                conn.commit()
            print("✅ [DB Sync] PostgreSQL Database initialized successfully.")
        except Exception as e:
            print(f"❌ [DB Sync] Init Error: {e}")
            self.enabled = False

    def save_chat_history(self, user_id: str, history: list):
        if not self.enabled: return
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO chat_memory (user_id, history_json, updated_at) 
                        VALUES (%s, %s, CURRENT_TIMESTAMP)
                        ON CONFLICT (user_id) DO UPDATE 
                        SET history_json = EXCLUDED.history_json, updated_at = CURRENT_TIMESTAMP;
                    """, (str(user_id), json.dumps(history)))
                conn.commit()
        except Exception as e:
            print(f"❌ [DB Sync] Save Chat Error: {e}")

    def load_chat_history(self, user_id: str) -> list:
        if not self.enabled: return []
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT history_json FROM chat_memory WHERE user_id = %s;", (str(user_id),))
                    row = cur.fetchone()
                    if row and row.get('history_json'):
                        return row['history_json']
                    return []
        except Exception as e:
            print(f"❌ [DB Sync] Load Chat Error: {e}")
            return []

    def save_audit_log(self, event_type: str, payload: dict):
        if not self.enabled: return
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO audit_logs (event_type, payload) VALUES (%s, %s);
                    """, (str(event_type), json.dumps(payload)))
                conn.commit()
        except Exception as e:
            print(f"❌ [DB Sync] Audit Log Error: {e}")


# Singleton
db_service = DBSyncService()
