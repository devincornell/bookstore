#from motor.motor_asyncio import AsyncIOMotorClient depricated
from beanie import init_beanie
from typing import Optional
import pymongo

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
    await BookResearch.add_search_index(client[db_name])  # Ensure vector search index is created

async def close_database_connection():
    """Close the MongoDB connection. Call this on app shutdown."""
    global _client
    if _client:
        _client.close()
        _client = None

# Store client as module-level variable for reuse
_client: Optional[pymongo.AsyncMongoClient] = None

async def get_database_client() -> pymongo.AsyncMongoClient:
    """Get or create the MongoDB client singleton."""
    global _client
    if _client is None:
        _client = pymongo.AsyncMongoClient(app_settings.MONGODB_URL)
    return _client

