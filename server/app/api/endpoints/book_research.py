"""
API endpoints for book research functionality using pydantic-ai
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, Field

from dotenv import load_dotenv
import os
load_dotenv()

from app.core import settings
from app.database import get_db
from app.ai import (
    BookResearchService, 
    BookResearchOutput, 
    BookResearchInfo
)

research_service = BookResearchService.from_api_key(os.environ["GOOGLE_API_KEY"])

router = APIRouter()

class BookResearchRequest(BaseModel):
    title: str = Field(..., description="Book title to research")
    author: Optional[str] = Field(None, description="Author name")
    save_to_database: bool = Field(False, description="Whether to save the research result to the database")


@router.post("/", response_model=BookResearchOutput)
async def research_book(
    request: BookResearchRequest,
    db: Session = Depends(get_db)
) -> BookResearchOutput:
    research_output = research_service.research_book(
        title=request.title,
        author=request.author,
    )
    return research_output

    try:
        
        # Perform comprehensive research
        research_output = research_service.research_book(
            title=request.title,
            author=request.author or "Unknown Author"
        )
        
        book_record = None
        message = f"Research completed for '{request.title}' using {request.provider or 'google'} provider"
        
        # Save to database if requested
        if request.save_to_database:
            try:
                book_record = research_service._save_book_to_database(
                    research_data=research_data,
                    db=db
                )
                message += f" and saved to database (ID: {book_record.id})"
            except Exception as e:
                message += f" but failed to save to database: {str(e)}"
        
        return research_output
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Research failed: {str(e)}"
        )

@router.get("/quick", response_model=BookResearchOutput)
async def quick_book_lookup(
    title: str = Query(..., description="Book title to research"),
    author: Optional[str] = Query(None, description="Author name"),
    db: Session = Depends(get_db)
):
    """
    Quick book research without saving to database - returns essential info only
    """
    research_output = research_service.research_book(
        title=title,
        author=author or "Unknown Author"
    )
    return research_output
    
