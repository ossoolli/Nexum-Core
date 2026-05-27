from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from typing import Optional
import os

# تحديد المجلد الرئيسي للمشروع بدقة
BASE_DIR = Path(__file__).resolve().parent.parent

# قائمة بالملفات الممكنة للمفاتيح
POSSIBLE_FILES = [
    BASE_DIR / ".env",
    BASE_DIR / "credentials.txt",
    Path.cwd() / ".env",
    Path.cwd() / "credentials.txt"
]

selected_file = None
for pf in POSSIBLE_FILES:
    if pf.exists():
        selected_file = str(pf)
        break

print(f"[Config] Loading credentials from: {selected_file}")

class NexumConfig(BaseSettings):
    # Required
    telegram_token: str = Field(alias="TELEGRAM_TOKEN")
    admin_id: int = Field(alias="ADMIN_ID")
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")

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

    # Gemini Enterprise Agent Platform (Vertex AI)
    google_cloud_project: str = Field(default="", alias="GOOGLE_CLOUD_PROJECT")
    google_cloud_location: str = Field(default="global", alias="GOOGLE_CLOUD_LOCATION")
    google_genai_use_vertexai: bool = Field(default=False, alias="GOOGLE_GENAI_USE_VERTEXAI")
    gemini_model: str = Field(default="gemini-3.5-flash", alias="GEMINI_MODEL")
    gemini_image_model: str = Field(default="gemini-3.5-flash", alias="GEMINI_IMAGE_MODEL")

    # Internal paths & configs
    storage_dir: Path = Field(default=BASE_DIR / "storage")
    log_level: str = Field(default="INFO")

    class Config:
        env_file = selected_file
        env_file_encoding = "utf-8"
        extra = "ignore"
        populate_by_name = True

try:
    config = NexumConfig()
    _auth_mode = "ADC/VertexAI" if config.google_genai_use_vertexai else (
        "API Key" if config.google_api_key else "None"
    )
    print(f"[Config] Auth mode: {_auth_mode} | Model: {config.gemini_model}")
    if config.google_genai_use_vertexai:
        print(f"[Config] GCP Project: {config.google_cloud_project} | Location: {config.google_cloud_location}")
except Exception as e:
    print(f"[Config] Error loading config: {e}")
    # Fallback to empty config to prevent crash if not critical
    config = None
