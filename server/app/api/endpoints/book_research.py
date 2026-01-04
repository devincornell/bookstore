"""
API endpoints for book research functionality using pydantic-ai
"""
import typing
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
import pydantic
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, Field

from dotenv import load_dotenv
import os
load_dotenv()

from app.core.config import app_settings
#from app.database import get_db
#from app.models import BookStoreDB
from app.mongo_models import BookResearch, init_beanie_models
from app.ai import (
    BookResearchService, 
    BookResearchOutput, 
    BookResearchInfo,
    BookRecommendService,
    BookRecommendOutput,
    BookExtractionService,
    BookExtractionOutput,
)

research_service = BookResearchService.from_api_key(app_settings.GOOGLE_API_KEY)
recommend_service = BookRecommendService.from_api_key(app_settings.GOOGLE_API_KEY)
extraction_service = BookExtractionService.from_api_key(app_settings.GOOGLE_API_KEY)
router = APIRouter()

class BookResearchRequest(BaseModel):
    title: str = Field(..., description="Book title to research")
    other_info: Optional[str] = Field(None, description="Other information about the book that may be helpful for researching")
    #save_to_database: bool = Field(False, description="Whether to save the research result to the database")

class BookResearchResponse(BaseModel):
    id: str = pydantic.Field(description="The MongoDB document ID")
    provided_title: str = pydantic.Field(description="The title of the book as provided in the research request")
    provided_other_info: str|None = pydantic.Field(description="Other information about the book that could be used to identify the correct book. Could include author, publication date, etc.")
    research_output: BookResearchOutput = pydantic.Field(description="Comprehensive researched information about the book")
    
    @classmethod
    def from_mongo_model(cls, model: BookResearch) -> typing.Self:
        return cls(
            id=str(model.id),
            provided_title=model.provided_title,
            provided_other_info=model.provided_other_info,
            research_output=model.research_output,
        )
    
@router.post("/research_and_insert", response_model=BookResearchResponse)
async def research_and_insert(
    request: BookResearchRequest,
) -> BookResearchResponse:
    research_output = research_service.research_book(
        title=request.title,
        other_info=request.other_info,
    )
    await init_beanie_models()
    new_book = await BookResearch.insert_book(
        provided_title=request.title,
        provided_other_info=request.other_info,
        research_output=research_output,
    )
    return BookResearchResponse.from_mongo_model(new_book)

@router.get("/research", response_model=BookResearchOutput)
async def research(
    title: str = Query(..., description="Book title to research"),
    other_info: Optional[str] = Query(None, description="Other information about the book"),
):
    '''Perform book research without saving to database.'''
    research_output = research_service.research_book(
        title=title,
        other_info=other_info,
    )
    return research_output
    


class BookListResponse(BaseModel):
    books: list[BookResearchResponse] = pydantic.Field(description="List of researched books")

@router.get("/list_books", response_model=BookListResponse)
async def list_books(
) -> BookListResponse:
    await init_beanie_models()
    books = await BookResearch.find_all().to_list()
    return BookListResponse(
        books=[BookResearchResponse.from_mongo_model(book) for book in books]
    )

@router.get("/recommend_books", response_model=BookRecommendOutput)
async def recommend_books(
    recommend_criteria: Optional[str] = Query(None, description="Criteria for recommending books")
) -> BookRecommendOutput:
    await init_beanie_models()
    books = await BookResearch.find_all().to_list()
    return recommend_service.recommend_books(
        recommend_criteria=recommend_criteria,
        book_info=[br.research_output.info for br in books],
    )

@router.delete("/delete_book/{book_id}")
async def delete_book(
    book_id: str
):
    """Delete a book by its MongoDB document ID."""
    await init_beanie_models()
    try:
        book = await BookResearch.get(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        await book.delete()
        return {"message": "Book deleted successfully", "deleted_id": book_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error deleting book: {str(e)}")

@router.get("/extract_books", response_model=BookExtractionOutput)
async def extract_books(
    book_list_unstructured: str = Query(..., description="Unstructured list of books + metadata to extract")
) -> BookExtractionOutput:
    return extraction_service.extract_books(
        book_list_unstructured=book_list_unstructured,
    )

@router.post("/extract_books_from_image", response_model=BookExtractionOutput)
async def extract_books_from_image(
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
        return extraction_service.extract_books_from_image(
            image_data=image_data,
            mime_type=image.content_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
