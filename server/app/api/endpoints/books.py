from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import math

from app.database import get_db
from app.crud.book import book_crud
from app.schemas.book import BookResponse, BookCreate, BookUpdate, BookListResponse

router = APIRouter()


@router.get("/", response_model=BookListResponse)
def get_books(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search in title, author, description"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    author: Optional[str] = Query(None, description="Filter by author"),
    db: Session = Depends(get_db)
):
    """Get books with pagination and optional filtering"""
    skip = (page - 1) * size
    books, total = book_crud.get_books(
        db=db, 
        skip=skip, 
        limit=size,
        search=search,
        genre=genre,
        author=author
    )
    
    total_pages = math.ceil(total / size) if total > 0 else 1
    
    return BookListResponse(
        items=books,
        total=total,
        page=page,
        size=size,
        pages=total_pages
    )


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    """Get a single book by ID"""
    book = book_crud.get_book(db=db, book_id=book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/", response_model=BookResponse)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    """Create a new book"""
    # Check if book with same ISBN already exists
    if book.isbn:
        existing_book = book_crud.get_book_by_isbn(db=db, isbn=book.isbn)
        if existing_book:
            raise HTTPException(
                status_code=400, 
                detail="Book with this ISBN already exists"
            )
    
    return book_crud.create_book(db=db, book=book)


@router.put("/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int, 
    book_update: BookUpdate, 
    db: Session = Depends(get_db)
):
    """Update an existing book"""
    # Check if ISBN is being updated and if it already exists
    if book_update.isbn:
        existing_book = book_crud.get_book_by_isbn(db=db, isbn=book_update.isbn)
        if existing_book and existing_book.id != book_id:
            raise HTTPException(
                status_code=400, 
                detail="Book with this ISBN already exists"
            )
    
    updated_book = book_crud.update_book(db=db, book_id=book_id, book_update=book_update)
    if not updated_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated_book


@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """Delete a book"""
    success = book_crud.delete_book(db=db, book_id=book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}


@router.get("/search/", response_model=List[BookResponse])
def search_books(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """Search books by title, author, or description"""
    books = book_crud.search_books(db=db, query=q, limit=limit)
    return books