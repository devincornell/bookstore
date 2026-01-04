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
from app.mongo_models import BookResearch, init_beanie_models, ResearchTask, TaskStatusEnum
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



router = APIRouter()


@router.get("/recommend", response_model=BookRecommendOutput)
async def books_recommend(
    recommend_criteria: Optional[str] = Query(None, description="Criteria for recommending books")
) -> BookRecommendOutput:
    await init_beanie_models()
    books = await BookResearch.find_all().to_list()
    return await recommend_service.recommend_books(
        recommend_criteria=recommend_criteria,
        book_info=[br.research_output.info for br in books],
    )

class BookInfoResponse(BaseModel):
    id: str = pydantic.Field(description="MongoDB document ID of the researched book")
    info: BookResearchInfo = pydantic.Field(description="Detailed information about the researched book")

    @classmethod
    def from_book_research(cls, book_research: BookResearch) -> "BookInfoResponse":
        return cls(
            id=str(book_research.id),
            info=book_research.research_output.info
        )

class BookListResponse(BaseModel):
    books: list[BookInfoResponse] = pydantic.Field(description="List of researched books")

@router.get("/list", response_model=BookListResponse)
async def books_list(
) -> BookListResponse:
    await init_beanie_models()
    books = await BookResearch.find_all().to_list()
    return BookListResponse(
        books=[BookInfoResponse.from_book_research(br) for br in books]
    )

@router.delete("/delete/{book_id}")
async def books_delete(
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


