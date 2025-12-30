from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate
import math


class BookCRUD:
    def get_book(self, db: Session, book_id: int) -> Optional[Book]:
        """Get a single book by ID"""
        return db.query(Book).filter(Book.id == book_id).first()
    
    def get_books(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        genre: Optional[str] = None,
        author: Optional[str] = None
    ) -> tuple[List[Book], int]:
        """Get books with optional filtering and pagination"""
        query = db.query(Book)
        
        # Apply filters
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                Book.title.ilike(search_filter) | 
                Book.author.ilike(search_filter) |
                Book.description.ilike(search_filter) |
                Book.genres.ilike(search_filter) |
                Book.general_style.ilike(search_filter) |
                Book.target_audience.ilike(search_filter) |
                Book.similar_works.ilike(search_filter) |
                Book.review_content.ilike(search_filter) |
                Book.author_background.ilike(search_filter) |
                Book.reception.ilike(search_filter)
            )
        
        if genre:
            # Search within comma-separated genres list
            query = query.filter(Book.genres.ilike(f"%{genre}%"))
            
        if author:
            query = query.filter(Book.author.ilike(f"%{author}%"))
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination
        books = query.offset(skip).limit(limit).all()
        
        return books, total
    
    def create_book(self, db: Session, book: BookCreate) -> Book:
        """Create a new book"""
        db_book = Book(**book.dict())
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        return db_book
    
    def update_book(self, db: Session, book_id: int, book_update: BookUpdate) -> Optional[Book]:
        """Update an existing book"""
        db_book = self.get_book(db, book_id)
        if not db_book:
            return None
        
        # Update only provided fields
        update_data = book_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_book, field, value)
        
        db.commit()
        db.refresh(db_book)
        return db_book
    
    def delete_book(self, db: Session, book_id: int) -> bool:
        """Delete a book"""
        db_book = self.get_book(db, book_id)
        if not db_book:
            return False
        
        db.delete(db_book)
        db.commit()
        return True
    
    def get_book_by_isbn(self, db: Session, isbn: str) -> Optional[Book]:
        """Get a book by ISBN"""
        return db.query(Book).filter(Book.isbn == isbn).first()
    
    def search_books(self, db: Session, query: str, limit: int = 20) -> List[Book]:
        """Search books by title, author, description, and all other text fields"""
        search_filter = f"%{query}%"
        return db.query(Book).filter(
            Book.title.ilike(search_filter) | 
            Book.author.ilike(search_filter) |
            Book.description.ilike(search_filter) |
            Book.genres.ilike(search_filter) |
            Book.general_style.ilike(search_filter) |
            Book.target_audience.ilike(search_filter) |
            Book.similar_works.ilike(search_filter) |
            Book.review_content.ilike(search_filter) |
            Book.author_background.ilike(search_filter) |
            Book.reception.ilike(search_filter)
        ).limit(limit).all()


# Create instance to be used in endpoints
book_crud = BookCRUD()