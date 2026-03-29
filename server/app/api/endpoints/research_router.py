"""
API endpoints for book research functionality using pydantic-ai
"""
import typing
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks

import pydantic
from pydantic import BaseModel, Field
import pymongo
import pymongo.errors

from app.core.config import app_settings
#from app.database import get_db
#from app.models import BookStoreDB
from app.mongo_models import (
    BookCollection, 
    BookDoc, 
    ResearchTaskCollection, 
    ResearchTaskDoc, 
    TaskStatus,
    BookManager,
    ResearchTaskDoesNotExist,
)

from app.ai import (
    BookResearchService, 
    BookResearchOutput, 
    BookResearchInfo,
    BookRecommendService,
    BookRecommendOutput,
    BookExtractionService,
    BookExtractionOutput,
    EmbeddingService,
    AIServices,
)

from app.api.deps import get_book_manager, get_db

ai_services = AIServices.from_api_key(app_settings.GOOGLE_API_KEY)


router = APIRouter()

class SingleBookResearchRequest(BaseModel):
    title: str = Field(..., description="Book title to research")
    other_info: str|None = Field(None, description="Other information about the book that may be helpful for researching")

class MultiBookResearchRequest(BaseModel):
    books: list[SingleBookResearchRequest] = Field(description="List of books to research")

@router.post("/research_and_insert_async", response_model=list[ResearchTaskDoc])
async def research_book_async(
    request: MultiBookResearchRequest,
    background_tasks: BackgroundTasks,
    book_manager: BookManager = Depends(get_book_manager),
) -> list[ResearchTaskDoc]:
    """Start asynchronous book research and return immediately with task ID"""
    tasks = []
    for brq in request.books:
        task_id, task = await book_manager.tasks.insert_new_research_task(
            title=brq.title,
            other_info=brq.other_info
        )
        tasks.append(task)
        background_tasks.add_task(
            background_task_research,
            research_request=brq,
            task=task,
            task_id=task_id,
        )
    return tasks

async def background_task_research(
    research_request: SingleBookResearchRequest,
    task: ResearchTaskDoc,
    task_id: int,
) -> None:
    """Background task to research a single book and save to database"""
    book_manager = await get_book_manager(await get_db())
    try:
        research_output = await ai_services.research.research_book(
            title=research_request.title,
            other_info=research_request.other_info,
        )
        embedding = await ai_services.embedding.generate_embedding(
            text = research_output.info.as_string()
        )
        try:
            await book_manager.books.insert_book(
                research_output=research_output,
                embedding=embedding,
                provided_title=research_request.title,
                provided_other_info=research_request.other_info,
            )
        except pymongo.errors.DuplicateKeyError:
            await book_manager.tasks.update_task_status(
                task_id=task_id,
                new_status=TaskStatus.FAILURE,
                reason='Book already exists in database',
            )

    except Exception as e:
        print(f"Error researching book '{research_request.title}': {str(e)}")
        await book_manager.tasks.update_task_status(
            task_id=task_id,
            new_status=TaskStatus.FAILURE,
            reason=f'{type(e).__name__}: {str(e)}',
        )


@router.post("/research_and_insert", response_model=BookDoc)
async def research_and_insert(
    request: SingleBookResearchRequest,
    book_manager: BookManager = Depends(get_book_manager),
) -> BookDoc:
    research_output = await ai_services.research.research_book(
        title=request.title,
        other_info=request.other_info,
    )
    new_book = await book_manager.books.insert_book(
        provided_title=request.title,
        provided_other_info=request.other_info,
        research_output=research_output,
        embedding=await ai_services.embedding.generate_embedding(research_output.info.as_string()),
    )

    return new_book

@router.get("/quick", response_model=BookResearchOutput)
async def research(
    title: str = Query(..., description="Book title to research"),
    other_info: str|None = Query(None, description="Other information about the book"),
):
    '''Perform book research without saving to database.'''
    research_output = await ai_services.research.research_book(
        title=title,
        other_info=other_info,
    )
    return research_output



class ResearchTasks(BaseModel):
    tasks: list[ResearchTaskDoc] = pydantic.Field(description="List of research tasks")

@router.get("/tasks/get/{task_id}", response_model=ResearchTaskDoc)
async def research_task_get(
    task_id: str,
    book_manager: BookManager = Depends(get_book_manager),
) -> ResearchTaskDoc:
    try:
        task = await book_manager.tasks.find_task_by_id(task_id)
    except ResearchTaskDoesNotExist:
        raise HTTPException(status_code=404, detail="Research task not found")
    return task


@router.get("/tasks/list_working", response_model=ResearchTasks)
async def research_tasks_list_working(
    book_manager: BookManager = Depends(get_book_manager),  
) -> ResearchTasks:
    tasks = await book_manager.tasks.find_by_status(TaskStatus.WORKING).to_list()
    return ResearchTasks(
        tasks = tasks,
    )

@router.get("/tasks/list_failed", response_model=ResearchTasks)
async def research_tasks_list_failed(
    book_manager: BookManager = Depends(get_book_manager),  
) -> ResearchTasks:
    tasks = await book_manager.tasks.find_by_status(TaskStatus.FAILURE).to_list()
    return ResearchTasks(
        tasks = tasks,
    )

@router.get("/tasks/list", response_model=ResearchTasks)
async def research_tasks_list(
    book_manager: BookManager = Depends(get_book_manager),
) -> ResearchTasks:
    tasks = await book_manager.tasks.find_all()
    return ResearchTasks(
        tasks = tasks,
    )

@router.get("/tasks/clear")
async def research_tasks_clear(
    book_manager: BookManager = Depends(get_book_manager),
) -> int:
    return await book_manager.tasks.delete_all()

@router.delete("/tasks/delete/{task_id}")
async def research_task_delete(
    task_id: str,
    book_manager: BookManager = Depends(get_book_manager),
) -> bool:
    deleted = await book_manager.tasks.delete_task_by_id(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Research task not found")
    return True

