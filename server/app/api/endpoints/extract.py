"""
API endpoints for book research functionality using pydantic-ai
"""
import typing
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks
import pydantic
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, Field

from dotenv import load_dotenv
import os
load_dotenv()

from app.core.config import app_settings
#from app.database import get_db
#from app.models import BookStoreDB
from app.mongo_models import BookResearch, init_beanie_models, ResearchTask
from app.ai import (
    BookResearchService, 
    BookResearchOutput, 
    BookRecommendService,
    BookRecommendOutput,
    BookExtractionService,
    BookExtractionOutput,
)

research_service = BookResearchService.from_api_key(app_settings.GOOGLE_API_KEY)
recommend_service = BookRecommendService.from_api_key(app_settings.GOOGLE_API_KEY)
extraction_service = BookExtractionService.from_api_key(app_settings.GOOGLE_API_KEY)


router = APIRouter()

@router.get("/from_text", response_model=BookExtractionOutput)
async def extract_from_text(
    book_list_unstructured: str = Query(..., description="Unstructured list of books + metadata to extract")
) -> BookExtractionOutput:
    return await extraction_service.extract_books(
        book_list_unstructured=book_list_unstructured,
    )

@router.post("/from_image", response_model=BookExtractionOutput)
async def extract_from_image(
    image: UploadFile = File(..., description="Image file containing book information (covers, lists, etc.)")
) -> BookExtractionOutput:
    """Extract book information from an uploaded image."""
    # Validate file type
    allowed_types = {"image/jpeg", "image/jpg", "image/png", "image/webp", "image/heic"}
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: {image.content_type}. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Read image data
    try:
        image_data = await image.read()
        if len(image_data) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading image file: {str(e)}")
    
    # Extract books from image
    try:
        return await extraction_service.extract_books_from_image(
            image_data=image_data,
            mime_type=image.content_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
