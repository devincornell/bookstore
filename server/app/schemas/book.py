from pydantic import BaseModel, validator
from decimal import Decimal
from typing import Optional
from datetime import datetime


# Base schema
class BookBase(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None
    description: Optional[str] = None
    price: Decimal
    stock_quantity: int = 0
    genre: Optional[str] = None
    publication_year: Optional[int] = None
    
    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v
    
    @validator('stock_quantity')
    def stock_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError('Stock quantity must be non-negative')
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
    price: Optional[Decimal] = None
    stock_quantity: Optional[int] = None
    genre: Optional[str] = None
    publication_year: Optional[int] = None
    
    @validator('price')
    def price_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price must be positive')
        return v
    
    @validator('stock_quantity')
    def stock_must_be_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError('Stock quantity must be non-negative')
        return v


# Schema for returning book data
class BookResponse(BookBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Schema for book list with pagination
class BookListResponse(BaseModel):
    items: list[BookResponse]
    total: int
    page: int
    size: int
    pages: int