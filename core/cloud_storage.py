import os
import requests
from typing import Dict, Any
from telebot import TeleBot
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class CloudStorageManager:
    def __init__(self, bot: TeleBot = None):
        self.bot = bot
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self._supabase: Client = None
        
        if self.supabase_url and self.supabase_key:
            try:
                self._supabase = create_client(self.supabase_url, self.supabase_key)
            except Exception as e:
                print(f"⚠️ [Supabase] Connection failed: {e}")

    def upload_to_telegram(self, file_path: str, chat_id: str, caption: str = "") -> bool:
        """إرسال ملف كوثيقة إلى قناة أو محادثة تيليجرام"""
        if not self.bot or not os.path.exists(file_path):
            return False
        try:
            with open(file_path, 'rb') as f:
                self.bot.send_document(chat_id, f, caption=caption)
            return True
        except Exception as e:
            print(f"❌ [Telegram Backup] Error: {e}")
            return False

    def upload_to_supabase(self, file_path: str, bucket_name: str = "nexum_storage") -> Dict[str, Any]:
        """رفع ملف إلى Supabase Storage"""
        if not self._supabase:
            return {"status": "error", "message": "Supabase not configured"}
        
        try:
            file_name = os.path.basename(file_path)
            with open(file_path, 'rb') as f:
                res = self._supabase.storage.from_(bucket_name).upload(file_name, f.read())
            return {"status": "success", "url": f"{self.supabase_url}/storage/v1/object/public/{bucket_name}/{file_name}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def log_deployment(self, project_name: str, metadata: dict):
        """تسجيل بيانات المشروع في Supabase DB"""
        if not self._supabase:
            return
        try:
            self._supabase.table("deployments").insert({
                "project_name": project_name,
                "metadata": metadata,
                "timestamp": "now()"
            }).execute()
        except Exception:
            pass

cloud_manager = CloudStorageManager()
