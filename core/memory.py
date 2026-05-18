import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv(dotenv_path="/home/madarmutaz/Mutaz-dev/.env")

class NexumMemory:
    def __init__(self):
        self.db_url = os.getenv("DB_CONNECTION")
        self.local_db_path = "/home/madarmutaz/Mutaz-dev/storage/database.json"
        self.conn = None
        self.connect()

    def connect(self):
        """إنشاء اتصال آمن مع قاعدة بيانات Supabase"""
        try:
            self.conn = psycopg2.connect(self.db_url)
            self.init_db()
            print("🟢 [Memory] Connected to Supabase Successfully.")
        except Exception as e:
            print(f"⚠️ [Memory] Supabase Connection Failed: {e}. Falling back to local storage.")
            self.conn = None

    def init_db(self):
        """إنشاء جدول الذاكرة إذا لم يكن موجوداً"""
        if not self.conn: return
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS nexum_memory (
                        user_id BIGINT PRIMARY KEY,
                        session_data JSONB,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                self.conn.commit()
        except Exception as e:
            print(f"⚠️ [Memory] Init DB failed: {e}")
            self.conn.rollback()

    def save_context(self, user_id: int, context_data: dict):
        """حفظ ذاكرة الجلسة في Supabase مع نظام استرجاع احتياطي محلي"""
        if self.conn:
            try:
                with self.conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO nexum_memory (user_id, session_data, updated_at)
                        VALUES (%s, %s, CURRENT_TIMESTAMP)
                        ON CONFLICT (user_id) DO UPDATE
                        SET session_data = EXCLUDED.session_data, updated_at = CURRENT_TIMESTAMP;
                    """, (user_id, json.dumps(context_data)))
                    self.conn.commit()
                    return True
            except Exception as e:
                print(f"⚠️ [Memory] Supabase save failed: {e}")
                self.conn.rollback()
        
        return self._save_local(user_id, context_data)

    def get_context(self, user_id: int) -> dict:
        """استرجاع ذاكرة الجلسة"""
        if self.conn:
            try:
                with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT session_data FROM nexum_memory WHERE user_id = %s;", (user_id,))
                    row = cur.fetchone()
                    if row:
                        return row['session_data']
            except Exception as e:
                print(f"⚠️ [Memory] Supabase fetch failed: {e}")
                self.conn.rollback()
        
        return self._get_local(user_id)

    def _save_local(self, user_id: int, context_data: dict):
        try:
            data = {}
            if os.path.exists(self.local_db_path):
                with open(self.local_db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            data[str(user_id)] = context_data
            with open(self.local_db_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"❌ [Memory] Local save failed: {e}")
            return False

    def _get_local(self, user_id: int) -> dict:
        try:
            if os.path.exists(self.local_db_path):
                with open(self.local_db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get(str(user_id), {})
        except Exception as e:
            print(f"❌ [Memory] Local fetch failed: {e}")
        return {}

db_memory = NexumMemory()
