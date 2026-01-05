from __future__ import annotations
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
import motor
#from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie
import os
import typing
import tqdm
import random
import pydantic
import pathlib

from app.core.config import app_settings
from app.ai import BookResearchInfo, ResearchSource, BookResearchOutput, BookResearchService


class SearchResult(BaseModel):
    text: str
    source_url: str
    score: float  # Automatically mapped from vectorSearchScore

class BookResearch(beanie.Document):
    class Settings:
        name = "book_research"  # The collection name in MongoDB
    
    provided_title: str = pydantic.Field(description="The title of the book as provided in the research request")
    provided_other_info: str|None = pydantic.Field(description="Other information about the book that could be used to identify the correct book. Could include author, publication date, etc.")
    research_output: BookResearchOutput = pydantic.Field(description="Comprehensive researched information about the book")
    embedding: list[float] = pydantic.Field(description="Embedding vector representing the book information")

    @classmethod
    async def add_search_index(cls, db: pymongo.AsyncMongoClient) -> None:
        '''Create the vector search index on the embedding field.'''
        collection_name = cls.get_settings().name
        
        try:
            await db.create_collection(collection_name)
        except pymongo.errors.CollectionInvalid:
            pass  # Collection already exists
        
        collection = db[collection_name]

        existing_coroutine = await collection.list_search_indexes()
        existing = await existing_coroutine.to_list(length=10)

        if not any(i['name'] == 'vector_index' for i in existing):
            await collection.create_search_index({
                "name": "vector_index",
                "type": "vectorSearch",
                "definition": {
                    "fields": [
                        {
                            "type": "vector",
                            "path": "embedding",
                            "numDimensions": 768,
                            "similarity": "cosine",
                            "quantization": "scalar"
                        }
                    ]
                }
            })
        
    @classmethod
    async def insert_book(cls, provided_title: str, provided_other_info: str|None, research_output: BookResearchOutput, embedding: list[float]) -> typing.Self:
        research = cls(
            provided_title=provided_title,
            provided_other_info=provided_other_info,
            research_output=research_output,
            embedding=embedding,
        )
        await research.insert()
        return research
    
    @classmethod
    async def vector_similarity(cls, query_vector: List[float], limit: int = 5) -> list[BookResearchWithSimilarity]:
        '''Perform a vector search query to find similar books based on the provided embedding vector.'''
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": limit * 10,
                    "limit": limit,
                    #"filter": { # example showing how to filter on additional attributes
                    #    "$and": [
                    #        {"user_id": user_id},
                    #        {"is_archived": False}
                    #    ]
                    #}
                }
            },
            {
                "$project": {
                    "similarity": {"$meta": "vectorSearchScore"}
                }
            }
        ]
        # The 'projection_model' makes this elegant by returning Pydantic objects
        return await cls.aggregate(pipeline, projection_model=BookResearchWithSimilarity).to_list()
    
class BookResearchWithSimilarity(BookResearch):
    similarity: float = pydantic.Field(description="Similarity score from vector search")



