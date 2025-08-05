# backend/config.py
import os
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    # Required settings
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    
    # Database settings
    database_url: str = Field(default="sqlite:///./lexsy.db", env="DATABASE_URL")
    chroma_persist_dir: str = Field(default="./chroma", env="CHROMA_PERSIST_DIR")
    
    # Gmail OAuth settings (optional)
    google_client_id: str = Field(default="", env="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(default="", env="GOOGLE_CLIENT_SECRET")
    
    # CORS settings for production
    cors_origins: str = Field(default="*", env="CORS_ORIGINS")  # Change to specific domains in production
    
    # App settings
    app_name: str = Field(default="Lexsy Legal Assistant", env="APP_NAME")
    debug: bool = Field(default=False, env="DEBUG")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS origins string to list"""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]

@lru_cache()
def get_settings():
    return Settings()
