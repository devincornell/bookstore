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
    ResearchTaskAlreadyExists,
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
) -> str:
    """Start asynchronous book research and return immediately with task ID"""
    for brq in request.books:
        background_tasks.add_task(
            background_task_research,
            research_request=brq,
        )
    return 'Submitted!'

async def background_task_research(
    research_request: SingleBookResearchRequest,
) -> None:
    """Background task to research a single book and save to database"""
    book_manager = await get_book_manager(await get_db())
    print(f'Background task started for book: {research_request.title}')

    try:
        task_id, task = await book_manager.tasks.insert_new_research_task(
            title=research_request.title,
            other_info=research_request.other_info
        )
    except ResearchTaskAlreadyExists:
        print(f"Research task for book '{research_request.title}' already exists. Checking status.")
        task_id, existing_task = await book_manager.tasks.find_task_by_title(research_request.title)
        if existing_task.status == TaskStatus.SUCCESS:
            print(f"Book '{research_request.title}' already researched successfully. No action needed.")
            return
        elif existing_task.status == TaskStatus.WORKING:
            print(f"Research task for book '{research_request.title}' is already in progress. Please wait.")
            return
        else:
            print(f"Previous research task for book '{research_request.title}' failed. Starting a new research task.")
            await book_manager.tasks.update_task_status_by_title(research_request.title, TaskStatus.WORKING, reason='Retrying after previous failure')

    print(f'Research id={task_id} started for book: {research_request.title}')
    try:
        research_output = await ai_services.research.research_book(
            title=research_request.title,
            other_info=research_request.other_info,
        )
    except Exception as e:
        print(f"Error researching book '{research_request.title}': {str(e)}")
        await book_manager.tasks.update_task_failure(task_id=task_id, reason=f'Research failed. {type(e).__name__}: {str(e)}')
        return
    
    try:
        embedding = await ai_services.embedding.generate_embedding(
            text = research_output.info.as_string()
        )
    except Exception as e:
        print(f"Error generating embedding for book '{research_request.title}': {str(e)}")
        await book_manager.tasks.update_task_failure(task_id=task_id, reason=f'Embedding generation failed. {type(e).__name__}: {str(e)}')
        return

    try:
        await book_manager.books.insert_book(
            research_output=research_output,
            embedding=embedding,
            provided_title=research_request.title,
            provided_other_info=research_request.other_info,
        )
    except pymongo.errors.DuplicateKeyError:
        print(f"Book '{research_request.title}' already exists in database. Marking task as successful. (Task ID: {task_id})")
        await book_manager.tasks.update_task_success(
            task_id=task_id,
            reason='Book already exists in database',
        )
        return

    await book_manager.tasks.update_task_success(task_id=task_id, reason='Done!')

    print(f'Background task completed for book: {research_request.title} (Task ID: {task_id})')


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

