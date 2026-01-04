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
router = APIRouter()



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


class SingleBookResearchRequest(BaseModel):
    title: str = Field(..., description="Book title to research")
    other_info: Optional[str] = Field(None, description="Other information about the book that may be helpful for researching")

class MultiBookResearchRequest(BaseModel):
    books: List[SingleBookResearchRequest] = Field(description="List of books to research")

@router.post("/research_and_insert_async", response_model=list[ResearchTask])
async def research_book_async(
    request: MultiBookResearchRequest,
    background_tasks: BackgroundTasks
) -> list[ResearchTask]:
    """Start asynchronous book research and return immediately with task ID"""
    await init_beanie_models()
    tasks = []
    for brq in request.books:
        task = await ResearchTask.insert_research_task(
            title=brq.title,
            other_info=brq.other_info
        )
        tasks.append(task)
        background_tasks.add_task(
            background_research,
            brq,
            task,
        )
    return tasks

async def background_research(
    research_request: SingleBookResearchRequest,
    task: ResearchTask,
) -> None:
    """Background task to research a single book and save to database"""
    research_output = await research_service.research_book(
        title=research_request.title,
        other_info=research_request.other_info,
    )
    await init_beanie_models()
    await BookResearch.insert_book(
        provided_title=research_request.title,
        provided_other_info=research_request.other_info,
        research_output=research_output,
    )
    return await task.delete()

@router.post("/research_and_insert", response_model=BookResearch)
async def research_and_insert(
    request: SingleBookResearchRequest,
) -> BookResearch:
    research_output = await research_service.research_book(
        title=request.title,
        other_info=request.other_info,
    )
    await init_beanie_models()
    new_book = await BookResearch.insert_book(
        provided_title=request.title,
        provided_other_info=request.other_info,
        research_output=research_output,
    )
    return new_book#BookResearchResponse.from_mongo_model(new_book)

@router.get("/research", response_model=BookResearchOutput)
async def research(
    title: str = Query(..., description="Book title to research"),
    other_info: Optional[str] = Query(None, description="Other information about the book"),
):
    '''Perform book research without saving to database.'''
    research_output = await research_service.research_book(
        title=title,
        other_info=other_info,
    )
    return research_output

class ResearchTasks(BaseModel):
    tasks: list[ResearchTask] = pydantic.Field(description="List of research tasks")

@router.get("/tasks/list", response_model=ResearchTasks)
async def research_tasks_list(
) -> ResearchTasks:
    await init_beanie_models()
    tasks = await ResearchTask.find_all().to_list()
    return ResearchTasks(
        tasks = tasks,
    )

@router.get("/tasks/clear")
async def research_tasks_clear(
) -> bool:
    await init_beanie_models()
    tasks = await ResearchTask.delete_all()
    return True




@router.get("/books/recommend", response_model=BookRecommendOutput)
async def books_recommend(
    recommend_criteria: Optional[str] = Query(None, description="Criteria for recommending books")
) -> BookRecommendOutput:
    await init_beanie_models()
    books = await BookResearch.find_all().to_list()
    return await recommend_service.recommend_books(
        recommend_criteria=recommend_criteria,
        book_info=[br.research_output.info for br in books],
    )


class BookListResponse(BaseModel):
    books: list[BookResearchResponse] = pydantic.Field(description="List of researched books")

@router.get("/books/list", response_model=BookListResponse)
async def books_list(
) -> BookListResponse:
    await init_beanie_models()
    books = await BookResearch.find_all().to_list()
    return BookListResponse(
        books=[BookResearchResponse.from_mongo_model(book) for book in books]
    )

@router.delete("/books/delete/{book_id}")
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

