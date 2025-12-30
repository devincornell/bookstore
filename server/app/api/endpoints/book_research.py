"""
API endpoints for book research functionality
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.ai.book_research import get_book_research_service
from app.schemas.book import BookResponse
from pydantic import BaseModel

router = APIRouter()

class BookResearchRequest(BaseModel):
    title: str
    author: Optional[str] = None
    publication_year: Optional[int] = None
    isbn: Optional[str] = None
    save_to_database: bool = True

class BookResearchResponse(BaseModel):
    research_data: dict
    book: Optional[BookResponse] = None
    research_completeness: float
    message: str

@router.post("/research", response_model=BookResearchResponse)
async def research_book(
    request: BookResearchRequest,
    db: Session = Depends(get_db)
):
    """
    Perform comprehensive AI-powered research on a book and optionally save to database
    
    This endpoint will:
    1. Research comprehensive information about the book using AI
    2. Gather reader-focused data (difficulty, tone, themes, etc.)
    3. Collect critical reception and author context
    4. Optionally create a full Book record in the database
    """
    try:
        research_service = get_book_research_service()
        
        # Perform comprehensive research
        research_data = await research_service.research_book_comprehensive(
            title=request.title,
            author=request.author,
            publication_year=request.publication_year,
            isbn=request.isbn
        )
        
        book_record = None
        message = f"Research completed for '{request.title}'"
        
        # Save to database if requested
        if request.save_to_database:
            try:
                book_record = await research_service.create_book_from_research(
                    research_data=research_data,
                    db=db
                )
                message += f" and saved to database (ID: {book_record.id})"
            except Exception as e:
                message += f" but failed to save to database: {str(e)}"
        
        return BookResearchResponse(
            research_data=research_data,
            book=book_record,
            research_completeness=research_data.get("research_completeness", 0.0),
            message=message
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Research failed: {str(e)}"
        )

@router.get("/research/quick")
async def quick_book_lookup(
    title: str = Query(..., description="Book title to research"),
    author: Optional[str] = Query(None, description="Author name"),
    year: Optional[int] = Query(None, description="Publication year"),
    db: Session = Depends(get_db)
):
    """
    Quick book research without saving to database - returns essential info only
    """
    try:
        research_service = get_book_research_service()
        
        # Do basic research only
        research_data = await research_service._research_basic_info(
            title=title, 
            author=author, 
            year=year, 
            isbn=None
        )
        
        # Add quick reader info
        reader_data = await research_service._research_reader_experience(research_data)
        
        return {
            "title": research_data.get("verified_title", title),
            "author": research_data.get("verified_author", author),
            "description": research_data.get("description", "No description available"),
            "genres": research_data.get("genres", "Unknown"),
            "reading_difficulty": reader_data.get("reading_difficulty"),
            "emotional_tone": reader_data.get("emotional_tone"),
            "major_themes": reader_data.get("major_themes"),
            "page_count": research_data.get("page_count"),
            "target_audience": reader_data.get("target_audience")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Quick research failed: {str(e)}"
        )

@router.post("/enhance/{book_id}")
async def enhance_existing_book(
    book_id: int,
    db: Session = Depends(get_db)
):
    """
    Enhance an existing book record with comprehensive AI research
    """
    try:
        # Get existing book
        from app.crud.book import book_crud
        existing_book = book_crud.get_book(db, book_id)
        
        if not existing_book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        research_service = get_book_research_service()
        
        # Research based on existing book data
        research_data = await research_service.research_book_comprehensive(
            title=existing_book.title,
            author=existing_book.author,
            publication_year=existing_book.publication_year,
            isbn=existing_book.isbn
        )
        
        # Update existing book with new research
        update_data = {}
        field_mapping = {
            "description": "description",
            "genres": "genres", 
            "general_style": "general_style",
            "target_audience": "target_audience",
            "similar_works": "similar_works",
            "review_content": "review_content",
            "author_background": "author_background",
            "reception": "reception",
            "reading_difficulty": "reading_difficulty",
            "emotional_tone": "emotional_tone",
            "pacing": "pacing",
            "major_themes": "major_themes",
            "content_warnings": "content_warnings",
            "series_info": "series_info",
            "page_count": "page_count",
            "narrative_pov": "narrative_pov",
            "setting_time_place": "setting_time_place",
            "main_characters": "main_characters",
            "notable_quotes": "notable_quotes",
            "reader_demographics": "reader_demographics",
            "frequently_compared_to": "frequently_compared_to",
            "critical_consensus": "critical_consensus",
            "discussion_points": "discussion_points",
        }
        
        for db_field, research_field in field_mapping.items():
            if research_field in research_data and research_data[research_field]:
                # Only update if current field is empty or research provides better data
                current_value = getattr(existing_book, db_field)
                if not current_value or len(str(current_value)) < 50:
                    update_data[db_field] = research_data[research_field]
        
        # Update the book
        for field, value in update_data.items():
            setattr(existing_book, field, value)
        
        db.commit()
        db.refresh(existing_book)
        
        return {
            "message": f"Enhanced book '{existing_book.title}' with {len(update_data)} updated fields",
            "updated_fields": list(update_data.keys()),
            "research_completeness": research_data.get("research_completeness", 0.0),
            "book": existing_book
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Enhancement failed: {str(e)}"
        )