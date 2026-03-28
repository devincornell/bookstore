from __future__ import annotations
import dataclasses
from typing import List, Optional, Any
from datetime import datetime, timedelta
import typing
from pydantic import Field, BaseModel
import pydantic
import pymongo
import pymongo.errors
import asyncio
import os
import typing
import enum
import uuid

from app.core.config import app_settings
from app.ai import BookResearchOutput
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase


class TaskStatus(str, enum.Enum):
    """Enum for research task status"""
    WORKING = "working"
    SUCCESS = "success"
    FAILURE = "failure"


@dataclasses.dataclass
class CollectionBase:
    """Base class for MongoDB collections"""
    _collection: AsyncCollection
    collection_name: str

    @classmethod
    def from_database(cls, db: AsyncDatabase, collection_name: str) -> typing.Self:
        '''Create a ResearchTaskCollection from a MongoDB database.'''
        return cls.from_collection(collection=db[collection_name])

    @classmethod
    def from_collection(cls, collection: AsyncCollection) -> typing.Self:
        '''Create a ResearchTaskCollection from a MongoDB collection.'''
        return cls(_collection=collection, collection_name=collection.name)

    async def create_indexes(self):
        '''Create a unique index on path_str to speed up prefix searches and upserts.'''
        #await self._collection.create_index("path_str", unique=True)
        raise NotImplementedError("create_indexes must be implemented by subclass")

