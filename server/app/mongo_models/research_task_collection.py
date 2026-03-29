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

from .collection_base import CollectionBase

class TaskStatus(str, enum.Enum):
    """Enum for research task status"""
    WORKING = "working"
    SUCCESS = "success"
    FAILURE = "failure"


class ResearchTaskDoesNotExist(Exception):
    """Custom exception for when a research task is not found in the database."""
    pass

class ResearchTaskCollection(CollectionBase):
    """Document model for tracking asynchronous research tasks"""

    async def create_indexes(self):
        '''Create a unique index on title to speed up upserts.'''
        await self._collection.create_index("title", unique=True)

    async def find_all(self) -> list[ResearchTaskDoc]:
        '''Retrieve all research task documents from the collection.'''
        cursor = await self._collection.find().to_list()
        return [ResearchTaskDoc.model_validate(doc) for doc in cursor]
    
    async def find_by_status(self, status: TaskStatus) -> list[ResearchTaskDoc]:
        """Find research tasks matching the given status."""
        cursor = await self._collection.find({"status": status}).to_list()
        return [ResearchTaskDoc.model_validate(doc) for doc in cursor]

    async def find_task_by_id(self, task_id: str) -> ResearchTaskDoc | None:
        """Retrieve a research task by its ID."""
        data = await self._collection.find_one({"_id": task_id})
        if data is None:
            raise ResearchTaskDoesNotExist(f"Research task with ID {task_id} does not exist.")
        return ResearchTaskDoc.model_validate(data)

    async def delete_task_by_id(self, task_id: str) -> bool:
        """Delete a research task by its ID. Returns True if deleted, False if not found."""
        result = await self._collection.delete_one({"_id": task_id})
        return result.deleted_count > 0
    
    async def delete_all(self) -> int:
        """Delete all research tasks from the collection."""
        result = await self._collection.delete_many({})
        return result.deleted_count

    async def insert_new_research_task(
        self, 
        title: str, 
        other_info: str|None = None,
        status: TaskStatus = TaskStatus.WORKING,
        reason: str|None = None,
    ) -> typing.Self:
        """Create a new single book research task"""        
        task = ResearchTaskDoc(
            title=title,
            other_info=other_info,
            status=status,
            started_at=datetime.now(),
            reason=reason,
        )
        return await self.upsert_research_task(task)
    
    async def upsert_research_task(self, doc: ResearchTaskDoc):
        """Update existing record by title or insert a new one."""
        await self._collection.replace_one(
            filter={"title": doc.title},
            replacement=doc.model_dump(), # Pydantic v2 dict conversion
            upsert=True
        )


class ResearchTaskDoc(pydantic.BaseModel):
    title: str = Field(description="Descriptive title for the research task")
    other_info: str|None = Field(default=None, description="Additional information about the task")
    status: TaskStatus = Field(default=TaskStatus.WORKING, description="Current status of the research task")
    started_at: datetime = Field(default_factory=datetime.now, description="Task creation timestamp")
    reason: str|None = Field(default=None, description="Reason for failure, if applicable")
