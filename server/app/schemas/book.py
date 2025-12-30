from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime


# Base schema
class BookBase(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None
    description: Optional[str] = None
    publication_year: Optional[int] = None
    
    # New genre field - comma-separated list
    genres: Optional[str] = None  # "Science Fiction, Space Opera, Adventure"
    
    # Existing detailed fields
    general_style: Optional[str] = None
    target_audience: Optional[str] = None
    similar_works: Optional[str] = None
    review_content: Optional[str] = None
    author_background: Optional[str] = None
    reception: Optional[str] = None
    
    # New reader-focused fields
    reading_difficulty: Optional[str] = None
    emotional_tone: Optional[str] = None
    pacing: Optional[str] = None
    major_themes: Optional[str] = None
    content_warnings: Optional[str] = None
    series_info: Optional[str] = None
    page_count: Optional[int] = None
    narrative_pov: Optional[str] = None
    setting_time_place: Optional[str] = None
    main_characters: Optional[str] = None
    notable_quotes: Optional[str] = None
    reader_demographics: Optional[str] = None
    frequently_compared_to: Optional[str] = None
    critical_consensus: Optional[str] = None
    discussion_points: Optional[str] = None
    
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
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    description: Optional[str] = None
    publication_year: Optional[int] = None
    genres: Optional[str] = None
    general_style: Optional[str] = None
    target_audience: Optional[str] = None
    similar_works: Optional[str] = None
    review_content: Optional[str] = None
    author_background: Optional[str] = None
    reception: Optional[str] = None
    reading_difficulty: Optional[str] = None
    emotional_tone: Optional[str] = None
    pacing: Optional[str] = None
    major_themes: Optional[str] = None
    content_warnings: Optional[str] = None
    series_info: Optional[str] = None
    page_count: Optional[int] = None
    narrative_pov: Optional[str] = None
    setting_time_place: Optional[str] = None
    main_characters: Optional[str] = None
    notable_quotes: Optional[str] = None
    reader_demographics: Optional[str] = None
    frequently_compared_to: Optional[str] = None
    critical_consensus: Optional[str] = None
    discussion_points: Optional[str] = None
    
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
    
    class Config:
        from_attributes = True


# Helper schema for working with genre lists
class BookWithGenreList(BookResponse):
    """Book response with genres parsed as a list"""
    genre_list: List[str] = []
    
    @validator('genre_list', pre=True, always=True)
    def parse_genres(cls, v, values):
        if 'genres' in values and values['genres']:
            return [genre.strip() for genre in values['genres'].split(',') if genre.strip()]
        return []


# Schema for book list with pagination
class BookListResponse(BaseModel):
    items: List[BookResponse]
    total: int
    page: int
    size: int
    pages: int