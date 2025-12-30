from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://username:password@localhost/bookstore_db"
    SECRET_KEY: str = "your-secret-key-here"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Google Cloud Vertex AI
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    GOOGLE_CLOUD_REGION: str = "us-central1"
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    
    class Config:
        env_file = ".env"


settings = Settings()