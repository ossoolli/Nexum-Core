from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).parent.parent

class NexumConfig(BaseSettings):
    # Required
    telegram_token: str = Field(alias="TELEGRAM_TOKEN")
    admin_id: int = Field(alias="ADMIN_ID")
    google_api_key: str = Field(alias="GOOGLE_API_KEY")

    # Optional / Compatibility aliases
    log_channel_id: int = Field(default=0, alias="LOG_CHANNEL_ID")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    db_connection: str = Field(default="", alias="DB_CONNECTION")
    master_key: str = Field(default="", alias="MASTER_KEY")
    webapp_url: str = Field(default="https://ossoolli.github.io/Nexum-Core/", alias="WEBAPP_URL")
    
    supabase_url: Optional[str] = Field(default=None, alias="SUPABASE_URL")
    supabase_key: Optional[str] = Field(default=None, alias="SUPABASE_KEY")

    # Internal
    storage_dir: Path = BASE_DIR / "storage"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
        populate_by_name = True  # يسمح باستخدام الاسم الأصلي أو الـ alias

config = NexumConfig()
