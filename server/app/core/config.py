from pydantic_settings import BaseSettings
from typing import Optional
import pathlib
import typing
import dataclasses

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://username:password@localhost/bookstore_db"
    SECRET_KEY: str = "your-secret-key-here"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Google Cloud Vertex AI
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_CLOUD_REGION: str = "us-central1"
    GOOGLE_APPLICATION_CREDENTIALS: str
    GOOGLE_API_KEY: str
    
    class Config:
        env_file = ".env"


app_settings = Settings()

@dataclasses.dataclass
class VertexAPIConfig:
    """Configuration class for Vertex AI services"""
    project_id: str
    location: str
    credentials_path: pathlib.Path

    @classmethod
    def from_settings(cls, settings: Settings) -> typing.Self:
        return cls(
            project_id=settings.GOOGLE_CLOUD_PROJECT,
            location=settings.GOOGLE_CLOUD_REGION,
            credentials_path=pathlib.Path(settings.GOOGLE_APPLICATION_CREDENTIALS)
        )

vertex_config = VertexAPIConfig.from_settings(app_settings)
