from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime


# Schema for book sources
class BookSourceBase(BaseModel):
    name: str
    url: str


class BookSourceCreate(BookSourceBase):
    pass


class BookSourceResponse(BookSourceBase):
    id: int
    book_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Base schema for books - matches BookResearchInfo structure
class BookBase(BaseModel):
    # Basic information
    title: str
    author: str
    publication_year: Optional[int] = None
    isbn: Optional[str] = None
    
    # Series information
    series_title: Optional[str] = None
    series_description: Optional[str] = None
    series_entry_number: Optional[str] = None
    other_series_entries: Optional[List[str]] = None
    
    # Reception
    awards: Optional[List[str]] = None
    ratings: Optional[List[str]] = None
    bestseller_lists: Optional[List[str]] = None
    review_quotes: Optional[List[str]] = None
    critical_consensus: Optional[str] = None
    reception_overview: Optional[str] = None
    
    # Content
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    description: Optional[str] = None
    emotional_tone: Optional[str] = None
    spicy_rating: Optional[str] = None
    content_warnings: Optional[str] = None
    target_audience: Optional[str] = None
    reader_demographics: Optional[str] = None
    setting_time_place: Optional[str] = None
    
    # Narrative and writing style
    general_style: Optional[str] = None
    pacing: Optional[str] = None
    reading_difficulty: Optional[str] = None
    narrative_pov: Optional[str] = None
    
    # Literary context
    genres: Optional[List[str]] = None
    similar_works: Optional[List[str]] = None
    frequently_compared_to: Optional[List[str]] = None
    
    # Author information
    author_other_series: Optional[List[str]] = None
    author_other_works: Optional[List[str]] = None
    author_background: Optional[str] = None
    
    @validator('publication_year')
    def publication_year_reasonable(cls, v):
        if v is not None and (v < 1000 or v > 2100):
            raise ValueError('Publication year must be reasonable')
        return v


# Schema for creating a book
class BookCreate(BookBase):
    pass


# Schema for updating a book
class BookUpdate(BaseModel):
    # Basic information
    title: Optional[str] = None
    author: Optional[str] = None
    publication_year: Optional[int] = None
    isbn: Optional[str] = None
    
    # Series information
    series_title: Optional[str] = None
    series_description: Optional[str] = None
    series_entry_number: Optional[str] = None
    other_series_entries: Optional[List[str]] = None
    
    # Reception
    awards: Optional[List[str]] = None
    ratings: Optional[List[str]] = None
    bestseller_lists: Optional[List[str]] = None
    review_quotes: Optional[List[str]] = None
    critical_consensus: Optional[str] = None
    reception_overview: Optional[str] = None
    
    # Content
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    description: Optional[str] = None
    emotional_tone: Optional[str] = None
    spicy_rating: Optional[str] = None
    content_warnings: Optional[str] = None
    target_audience: Optional[str] = None
    reader_demographics: Optional[str] = None
    setting_time_place: Optional[str] = None
    
    # Narrative and writing style
    general_style: Optional[str] = None
    pacing: Optional[str] = None
    reading_difficulty: Optional[str] = None
    narrative_pov: Optional[str] = None
    
    # Literary context
    genres: Optional[List[str]] = None
    similar_works: Optional[List[str]] = None
    frequently_compared_to: Optional[List[str]] = None
    
    # Author information
    author_other_series: Optional[List[str]] = None
    author_other_works: Optional[List[str]] = None
    author_background: Optional[str] = None
    
    @validator('publication_year')
    def publication_year_reasonable(cls, v):
        if v is not None and (v < 1000 or v > 2100):
            raise ValueError('Publication year must be reasonable')
        return v


# Schema for returning book data
class BookResponse(BookBase):
    id: int
    created_at: datetime
    updated_at: datetime
    sources: List[BookSourceResponse] = []
    
    class Config:
        from_attributes = True


# Schema for book list with pagination
class BookListResponse(BaseModel):
    items: List[BookResponse]
    total: int
    page: int
    size: int
    pages: int