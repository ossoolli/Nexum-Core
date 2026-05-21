from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from typing import Optional
import os

# تحديد المجلد الرئيسي للمشروع بدقة
BASE_DIR = Path(__file__).resolve().parent.parent

# قائمة بالملفات الممكنة للمفاتيح
POSSIBLE_FILES = [
    BASE_DIR / "credentials.txt",
    BASE_DIR / ".env",
    Path.cwd() / "credentials.txt",
    Path.cwd() / ".env"
]

selected_file = None
for pf in POSSIBLE_FILES:
    if pf.exists():
        selected_file = str(pf)
        break

print(f"🔱 [Config] Loading credentials from: {selected_file}")

class NexumConfig(BaseSettings):
    # Required
    telegram_token: str = Field(alias="TELEGRAM_TOKEN")
    admin_id: int = Field(alias="ADMIN_ID")
    google_api_key: str = Field(alias="GOOGLE_API_KEY")

    # Tokens & Services
    github_token: str = Field(default="", alias="GITHUB_TOKEN")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    
    # Optional
    log_channel_id: int = Field(default=0, alias="LOG_CHANNEL_ID")
    db_connection: str = Field(default="", alias="DB_CONNECTION")
    master_key: str = Field(default="", alias="MASTER_KEY")
    webapp_url: str = Field(default="https://ossoolli.github.io/Nexum-Core/", alias="WEBAPP_URL")
    
    supabase_url: Optional[str] = Field(default=None, alias="SUPABASE_URL")
    supabase_key: Optional[str] = Field(default=None, alias="SUPABASE_KEY")

    class Config:
        env_file = selected_file
        env_file_encoding = "utf-8"
        extra = "ignore"
        populate_by_name = True

try:
    config = NexumConfig()
    print(f"✅ [Config] GOOGLE_API_KEY loaded: {'Yes' if config.google_api_key else 'No'}")
except Exception as e:
    print(f"❌ [Config] Error loading config: {e}")
    # Fallback to empty config to prevent crash if not critical
    config = None
