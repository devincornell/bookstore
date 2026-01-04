from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import Optional


from app.core.config import app_settings
from .book_research import BookResearch
from .research_task import ResearchTask

async def init_beanie_models(db_name: str = app_settings.MONGODB_DB_NAME) -> None:
    """Initialize Beanie with all document models for the specified database."""
    client = await get_database_client()
        
    await init_beanie(
        database=client[db_name],
        document_models=[BookResearch, ResearchTask],  # Add more models here as you create them
    )

async def close_database_connection():
    """Close the MongoDB connection. Call this on app shutdown."""
    global _client
    if _client:
        _client.close()
        _client = None

# Store client as module-level variable for reuse
_client: Optional[AsyncIOMotorClient] = None

async def get_database_client() -> AsyncIOMotorClient:
    """Get or create the MongoDB client singleton."""
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(app_settings.MONGODB_URL)
    return _client

