from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
import math
import dataclasses
import typing

from app.ai import BookResearchOutput, BookResearchInfo

from .book_infos import BookInfo
from .research_sources import ResearchSource

@dataclasses.dataclass
class BookStoreDB:
    db: Session

    @classmethod
    def from_orm_session(cls, db: Session) -> typing.Self:
        return cls(db=db)
    
    def add_book_research(self, research_output: BookResearchOutput) -> BookInfo:
        '''Add a book and its research sources to the database.        
        '''
        book_info = BookInfo.from_research_info(research_output.info)
        self.db.add(book_info)
        self.db.flush()  # To get book_info.id
        
        # Add associated sources
        for source in research_output.sources:
            research_source = ResearchSource.from_name_url(
                book_id=book_info.id, 
                name=source['name'], 
                url=source['url']
            )
            self.db.add(research_source)
        self.db.commit()
        return book_info
    
    def add_book_info(self, book_info: BookInfo) -> BookInfo:
        '''Add a BookInfo instance to the database.'''
        self.db.add(book_info)
        self.db.commit()
        self.db.refresh(book_info)
        return book_info
    
