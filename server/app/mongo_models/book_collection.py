from __future__ import annotations
from typing import List, Optional
from datetime import datetime
import typing
import pydantic
import pymongo
import asyncio
import os
import typing
import tqdm
import random
import pydantic
import pathlib
import dataclasses

from app.core.config import app_settings
from app.ai import BookResearchInfo, ResearchSource, BookResearchOutput, BookResearchService

from .collection_base import CollectionBase

class SearchResult(pydantic.BaseModel):
    text: str
    source_url: str
    score: float  # Automatically mapped from vectorSearchScore

class BookCollection(CollectionBase):
        
    async def create_indexes(self, vector_index_name: str = "vector_index"):
        '''Create a unique index on title to speed up upserts.'''
        await self._collection.create_index(
            [("title", pymongo.ASCENDING), ("publication_year", pymongo.DESCENDING)], 
            unique=True
        )
        
        existing_coroutine = await self._collection.list_search_indexes()
        existing = await existing_coroutine.to_list(length=10)
        print("Existing search indexes:", existing)

        if not any(i['name'] == vector_index_name for i in existing):
            await self._collection.create_search_index({
                "name": vector_index_name,
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
    async def find_all(cls) -> list[BookDoc]:
        '''Retrieve all book documents from the collection.'''
        return await cls._collection.find().to_list()

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
                }
            },
            {
                "$project": BookResearchWithSimilarity.project()
            }
        ]
        # The 'projection_model' makes this elegant by returning Pydantic objects
        return await cls.aggregate(pipeline, projection_model=BookResearchWithSimilarity).to_list()


    async def insert_book(self, 
        provided_title: str, 
        provided_other_info: str|None, 
        research_output: BookResearchOutput, 
        embedding: list[float]
    ) -> BookDoc:
        research = BookDoc(
            title = research_output.info.title,
            authors = research_output.info.authors,
            publication_year = research_output.info.publication_year,
            provided_title=provided_title,
            provided_other_info=provided_other_info,
            research_output=research_output,
            embedding=embedding,
        )
        await self._collection.insert_one(research.model_dump())
        return research
    
    

    

class BookDoc(pydantic.BaseModel):
    title: str = pydantic.Field(description="The full standard title of the book, not including subtitle or information about the series.")
    authors: list[str] = pydantic.Field(description="The authors' names. Not pen initials, and names should be in order - don't do 'last name, first name' format)")
    publication_year: int = pydantic.Field(description="The year the book was published")

    provided_title: str = pydantic.Field(description="The title of the book as provided in the research request")
    provided_other_info: str|None = pydantic.Field(description="Other information about the book that could be used to identify the correct book. Could include author, publication date, etc.")
    
    research_output: BookResearchOutput = pydantic.Field(description="Comprehensive researched information about the book")
    embedding: list[float] = pydantic.Field(description="Embedding vector representing the book information")


class BookResearchWithSimilarity(pydantic.BaseModel):
    book: BookDoc = pydantic.Field(description="The researched book document")
    similarity: float = pydantic.Field(description="Similarity score from vector search")

    @staticmethod
    def project() -> dict[str,str|int|list[float]]:
        '''Projection definition for MongoDB aggregation to return this model.'''
        return {
            "_id": 0,
            "book": "$research_output.info",
            "similarity": {"$meta": "vectorSearchScore"}
        }



