from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    gemini_api_key: str = Field(default="")
    gemini_model: str = Field(default="gemini-3.6-flash")
    session_secret: str = Field(default="dev-secret-change-in-production")
    api_base_url: str = Field(default="http://localhost:8000")

    model_config = {
        "env_file": [
            str(Path(__file__).parent.parent / ".env"),
            str(Path(__file__).parent.parent.parent.parent / ".env"),
        ],
        "extra": "ignore",
    }


settings = Settings()
