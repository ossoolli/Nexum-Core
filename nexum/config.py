from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

class NexumConfig(BaseSettings):
    # Required
    telegram_token: str = Field(alias="BOT_TOKEN")
    admin_id: int
    google_api_key: str

    # Optional
    log_channel_id: str = Field(default="", alias="TELEGRAM_CHANNEL_ID")
    openrouter_api_key: str = ""
    openai_api_key: str = ""
    db_connection: str = ""
    master_key: str = ""
    redis_url: str = "redis://localhost:6379"

    # Internal
    storage_dir: Path = BASE_DIR / "storage"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

config = NexumConfig()
