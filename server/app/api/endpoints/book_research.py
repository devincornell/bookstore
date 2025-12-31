"""
API endpoints for book research functionality using pydantic-ai
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.ai.book_research import get_book_research_service
from app.ai.research_service import BookResearchService, BookResearchOutput, BookResearchInfo
from app.schemas.book import BookResponse
from pydantic import BaseModel

from dotenv import load_dotenv
import os
load_dotenv()

research_service = BookResearchService.from_api_key(os.environ["GOOGLE_API_KEY"])

router = APIRouter()

class BookResearchRequest(BaseModel):
    title: str
    author: Optional[str] = None
    save_to_database: bool = True


@router.post("/", response_model=BookResearchOutput)
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
    
    Supports multiple LLM providers: google, openai, anthropic
    """
    
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
    

@router.post("/provider")
async def set_provider(
    provider: str = Query(..., description="LLM provider to use: google, openai, anthropic")
):
    """
    Set the LLM provider for book research
    """
    valid_providers = ["google", "openai", "anthropic"]
    
    if provider not in valid_providers:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider. Must be one of: {', '.join(valid_providers)}"
        )
    
    try:
        research_service = get_book_research_service(provider=provider)
        return {
            "message": f"LLM provider set to: {provider}",
            "provider": provider,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to set provider: {str(e)}"
        )