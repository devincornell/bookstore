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
from .errors import ResearchTaskDoesNotExist, ResearchTaskAlreadyExists

ResearchTaskID = str

class TaskStatus(str, enum.Enum):
    """Enum for research task status"""
    WORKING = "working"
    SUCCESS = "success"
    FAILURE = "failure"

class ResearchTaskCollection(CollectionBase):
    """Document model for tracking asynchronous research tasks"""

    async def create_indexes(self):
        '''Create a unique index on title to speed up upserts.'''
        await self._collection.create_index("title", unique=True)

    async def find_all(self) -> list[tuple[ResearchTaskID, ResearchTaskDoc]]:
        '''Retrieve all research task documents from the collection.'''
        return await self.find_tasks({})
    
    async def find_tasks_by_status(self, status: TaskStatus) -> list[tuple[ResearchTaskID, ResearchTaskDoc]]:
        """Find research tasks matching the given status."""
        return await self.find_tasks({"status": status.value})
    
    async def find_tasks(self, filter: dict[str, Any]) -> list[tuple[ResearchTaskID, ResearchTaskDoc]]:
        """Find research tasks matching the given filter."""
        cursor = await self._collection.find(filter).to_list()
        return [(str(doc["_id"]), ResearchTaskDoc.model_validate(doc)) for doc in cursor]
    
    async def find_task_by_title(self, title: str) -> tuple[ResearchTaskID, ResearchTaskDoc]:
        """Retrieve a research task by its title."""
        return await self.find_task({"title": title})

    async def find_task_by_id(self, task_id: str) -> tuple[ResearchTaskID, ResearchTaskDoc]:
        """Retrieve a research task by its ID."""
        return await self.find_task({"_id": task_id})
    
    async def find_task(self, filter: dict[str, Any]) -> tuple[ResearchTaskID, ResearchTaskDoc]:
        """Find a research task matching the given filter."""
        data = await self._collection.find_one(filter)
        if data is None:
            raise ResearchTaskDoesNotExist(f"Research task matching {filter} does not exist.")
        return str(data["_id"]), ResearchTaskDoc.model_validate(data)

    async def delete_task_by_id(self, task_id: ResearchTaskID) -> bool:
        """Delete a research task by its ID. Returns True if deleted, False if not found."""
        result = await self._collection.delete_one({"_id": task_id})
        return result.deleted_count > 0
    
    async def delete_all(self) -> int:
        """Delete all research tasks from the collection."""
        result = await self._collection.delete_many({})
        return result.deleted_count
    
    async def update_task_success(self, task_id: str) -> ResearchTaskDoc:
        """Mark a research task as successful by its ID."""
        return await self.update_task_status(task_id, TaskStatus.SUCCESS)
    
    async def update_task_failure(self, task_id: str, reason: str) -> ResearchTaskDoc:
        """Mark a research task as failed by its ID, with an optional reason."""
        return await self.update_task_status(task_id, TaskStatus.FAILURE, reason=reason)

    async def update_task_status_by_title(self, title: str, new_status: TaskStatus, reason: str|None = None) -> ResearchTaskDoc:
        """Update the status of a research task by its title."""
        update_data = {"status": new_status}
        if reason is not None:
            update_data["reason"] = reason
        result = await self._collection.update_one({"title": title}, {"$set": update_data})
        if result.matched_count == 0:
            raise ResearchTaskDoesNotExist(f"Research task with title '{title}' does not exist.")
        return await self.find_task_by_title(title)
    
    async def update_task_status(self, task_id: str, new_status: TaskStatus, reason: str|None = None) -> ResearchTaskDoc:
        """Update the status of a research task by its ID."""
        update_data = {"status": new_status}
        if reason is not None:
            update_data["reason"] = reason
        result = await self._collection.update_one({"_id": task_id}, {"$set": update_data})
        if result.matched_count == 0:
            raise ResearchTaskDoesNotExist(f"Research task with ID {task_id} does not exist.")
        return await self.find_task_by_id(task_id)

    async def insert_new_research_task(
        self, 
        title: str, 
        other_info: str|None = None,
        status: TaskStatus = TaskStatus.WORKING,
        reason: str|None = None,
    ) -> tuple[str, ResearchTaskDoc]:
        """Create a new single book research task"""
        task = ResearchTaskDoc(
            title=title,
            other_info=other_info,
            status=status,
            started_at=datetime.now(),
            reason=reason,
        )
        inserted_id = await self.insert_task(task)
        return inserted_id, task
    
    async def upsert_task(self, doc: ResearchTaskDoc) -> str:
        """Update existing record by title or insert a new one."""
        await self._collection.replace_one(
            filter={"title": doc.title},
            replacement=doc.model_dump(), # Pydantic v2 dict conversion
            upsert=True
        )
        inserted_doc = await self._collection.find_one({"title": doc.title}, {"_id": 1})
        return inserted_doc['_id']
    
    async def insert_task(self, doc: ResearchTaskDoc) -> str:
        """Insert a new research task document into the collection."""
        try:
            result = await self._collection.insert_one(doc.model_dump())
        except pymongo.errors.DuplicateKeyError:
            raise ResearchTaskAlreadyExists(f"A research task with title '{doc.title}' already exists.")
        return result.inserted_id


class ResearchTaskDoc(pydantic.BaseModel):
    title: str = Field(description="Descriptive title for the research task")
    other_info: str|None = Field(default=None, description="Additional information about the task")
    status: TaskStatus = Field(default=TaskStatus.WORKING, description="Current status of the research task")
    started_at: datetime = Field(default_factory=datetime.now, description="Task creation timestamp")
    reason: str|None = Field(default=None, description="Reason for failure, if applicable")
