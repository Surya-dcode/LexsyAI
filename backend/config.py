# backend/config.py
import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    # Required settings
    openai_api_key: str
    
    # Database settings
    database_url: str = "sqlite:///./lexsy.db"
    chroma_persist_dir: str = "./chroma"
    
    # Gmail OAuth settings (optional)
    google_client_id: str = ""
    google_client_secret: str = ""
    
    # CORS settings for production
    cors_origins: str = "*"  # Change to specific domains in production
    
    # App settings
    app_name: str = "Lexsy Legal Assistant"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS origins string to list"""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]

@lru_cache()
def get_settings():
    return Settings()