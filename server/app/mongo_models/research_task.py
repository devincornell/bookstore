from typing import List, Optional, Any
from datetime import datetime, timedelta
import typing
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
import enum
import uuid

from app.core.config import app_settings
from app.ai import BookResearchOutput



class ResearchTask(beanie.Document):
    """Document model for tracking asynchronous research tasks"""
    
    class Settings:
        name = "research_tasks"  # The collection name in MongoDB
    
    title: str = Field(description="Descriptive title for the research task")
    other_info: Optional[str] = Field(default=None, description="Additional information about the task")
    started_at: datetime = Field(default_factory=datetime.now, description="Task creation timestamp")
    
    @classmethod
    async def insert_research_task(
        cls, 
        title: str, 
        other_info: Optional[str] = None
    ) -> typing.Self:
        """Create a new single book research task"""        
        task = cls(
            title=title,
            other_info=other_info,
        )
        await task.insert()
        return task
    
