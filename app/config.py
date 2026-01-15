"""Configuration management for VanVani AI."""
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """System settings loaded from environment variables."""
    
    # Core Application
    app_name: str = "VanVani AI"
    environment: str = "production"
    debug: bool = False
    
    # Twilio Integration
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""
    
    # AI Providers
    google_gemini_api_key: str = ""
    sarvam_api_key: str = ""
    google_application_credentials: str = ""
    
    # Telephony & Session Management
    max_call_duration: int = 300
    session_timeout: int = 120
    host: str = ""
    ngrok_auth_token: str = ""
    
    # Storage Paths
    database_url: str = "sqlite:///./vanvani.db"
    vector_db_path: str = "./data/vector_store"
    
    # User Preferences
    supported_languages: list = ["hi", "en", "chhattisgarhi", "gondi", "halbi"]
    default_language: str = "hi"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
