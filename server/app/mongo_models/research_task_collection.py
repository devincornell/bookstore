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


class ResearchTaskCollection(CollectionBase):
    """Document model for tracking asynchronous research tasks"""

    async def create_indexes(self):
        '''Create a unique index on title to speed up upserts.'''
        await self._collection.create_index("title", unique=True)

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
