from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://username:password@localhost/bookstore_db"
    SECRET_KEY: str = "your-secret-key-here"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"


settings = Settings()