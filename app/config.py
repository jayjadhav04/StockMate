import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_ENV: str = "development"
    SECRET_KEY: str = "supersecretkeychangeinproduction123!@#"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./stockmate.db"

    model_config = SettingsConfigDict(
        # Look for .env in the parent directory of this file's directory (i.e. the project root)
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
