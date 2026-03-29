import typing
import dataclasses
import fastapi
import pymongo
from pymongo.asynchronous.database import AsyncDatabase
import contextlib

from .book_collection import BookCollection, BookDoc
from .research_task_collection import ResearchTaskCollection, ResearchTaskDoc, TaskStatus


@dataclasses.dataclass
class BookManager:
    _db: AsyncDatabase
    _books: BookCollection
    _tasks: ResearchTaskCollection

    @classmethod
    def from_database(cls, db: AsyncDatabase) -> typing.Self:
        '''Create a BookManager from a MongoDB database.'''
        return cls(
            _db=db,
            _books=BookCollection.from_database(db, collection_name="books"),
            _tasks=ResearchTaskCollection.from_database(db, collection_name="research_tasks")
        )

    @property
    def books(self) -> BookCollection:
        '''Get the BookCollection for managing book research documents.'''
        return self._books
    
    @property
    def tasks(self) -> ResearchTaskCollection:
        '''Get the ResearchTaskCollection for managing research tasks.'''
        return self._tasks
