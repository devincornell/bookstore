from typing import List, Optional
from datetime import datetime
import typing
#from beanie import Document, Indexed, Link
import beanie
import beanie.exceptions
from pydantic import Field, BaseModel
import pydantic
import pymongo
import pymongo.errors
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import os
import typing
import tqdm
import random
import pydantic
import pathlib

from app.core.config import app_settings
from app.ai import BookResearchInfo, ResearchSource, BookResearchOutput, BookResearchService


class BookResearch(beanie.Document):
    class Settings:
        name = "book_research"  # The collection name in MongoDB
    provided_title: str = pydantic.Field(description="The title of the book as provided in the research request")
    provided_other_info: str|None = pydantic.Field(description="Other information about the book that could be used to identify the correct book. Could include author, publication date, etc.")
    research_output: BookResearchOutput = pydantic.Field(description="Comprehensive researched information about the book")

    @classmethod
    async def insert_book(cls, provided_title: str, provided_other_info: str|None, research_output: BookResearchOutput) -> typing.Self:
        research = cls(
            provided_title=provided_title,
            provided_other_info=provided_other_info,
            research_output=research_output,
        )
        await research.insert()
        return research


async def init_beanie_models(db_name: str = app_settings.MONGODB_DB_NAME) -> None:
    """Initialize Beanie with all document models for the specified database."""
    client = await get_database_client()
    await init_beanie(
        database=client[db_name],
        document_models=[BookResearch],  # Add more models here as you create them
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
