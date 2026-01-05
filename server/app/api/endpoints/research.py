"""
API endpoints for book research functionality using pydantic-ai
"""
import typing
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks
import pydantic
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, Field


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
    EmbeddingService,
    AIServices,
)

ai_services = AIServices.from_api_key(app_settings.GOOGLE_API_KEY)


router = APIRouter()

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
            background_task_research,
            brq,
            task,
        )
    return tasks

async def background_task_research(
    research_request: SingleBookResearchRequest,
    task: ResearchTask,
) -> None:
    """Background task to research a single book and save to database"""
    try:
        research_output = await ai_services.research.research_book(
            title=research_request.title,
            other_info=research_request.other_info,
        )
        embedding = await ai_services.embedding.generate_embedding(research_output.info.as_string())
        await init_beanie_models()
        await BookResearch.insert_book(
            research_output=research_output,
            embedding=embedding,
            provided_title=research_request.title,
            provided_other_info=research_request.other_info,
        )
        task.status = TaskStatusEnum.SUCCESS
        await task.save()
    except Exception as e:
        print(f"Error researching book '{research_request.title}': {str(e)}")
        task.status = TaskStatusEnum.FAILURE
        await task.save()


@router.post("/research_and_insert", response_model=BookResearch)
async def research_and_insert(
    request: SingleBookResearchRequest,
) -> BookResearch:
    research_output = await ai_services.research.research_book(
        title=request.title,
        other_info=request.other_info,
    )
    await init_beanie_models()
    new_book = await BookResearch.insert_book(
        provided_title=request.title,
        provided_other_info=request.other_info,
        research_output=research_output,
    )
    return new_book

@router.get("/quick", response_model=BookResearchOutput)
async def research(
    title: str = Query(..., description="Book title to research"),
    other_info: Optional[str] = Query(None, description="Other information about the book"),
):
    '''Perform book research without saving to database.'''
    research_output = await ai_services.research.research_book(
        title=title,
        other_info=other_info,
    )
    return research_output



class ResearchTasks(BaseModel):
    tasks: list[ResearchTask] = pydantic.Field(description="List of research tasks")

@router.get("/tasks/get/{task_id}", response_model=ResearchTask)
async def research_task_get(
    task_id: str
) -> ResearchTask:
    await init_beanie_models()
    task = await ResearchTask.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Research task not found")
    return task


@router.get("/tasks/list_working", response_model=ResearchTasks)
async def research_tasks_list(
) -> ResearchTasks:
    await init_beanie_models()
    tasks = await ResearchTask.find(ResearchTask.status == TaskStatusEnum.WORKING).to_list()
    return ResearchTasks(
        tasks = tasks,
    )

@router.get("/tasks/list_failed", response_model=ResearchTasks)
async def research_tasks_list(
) -> ResearchTasks:
    await init_beanie_models()
    tasks = await ResearchTask.find(ResearchTask.status == TaskStatusEnum.FAILURE).to_list()
    return ResearchTasks(
        tasks = tasks,
    )

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

@router.delete("/tasks/delete/{task_id}")
async def research_task_delete(
    task_id: str
) -> bool:
    await init_beanie_models()
    task = await ResearchTask.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Research task not found")
    await task.delete()
    return True

