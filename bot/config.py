"""Configuration loading from environment variables."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# Find .env.bot.secret in parent directory or current directory
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env.bot.secret"
if not ENV_FILE.exists():
    ENV_FILE = BASE_DIR.parent / ".env.bot.secret"


class Settings(BaseSettings):
    """Bot configuration loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    # Telegram bot token
    bot_token: str
    
    # LMS API configuration
    lms_api_base_url: str
    lms_api_key: str
    
    # LLM API configuration (for Task 3)
    llm_api_key: str = ""
    llm_api_base_url: str = ""
    llm_api_model: str = "coder-model"


settings = Settings()
