import typing
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks
import pydantic
import pymongo
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, Field
import pymongo.errors
from mcp.server import FastMCP
import logging


from app.core.config import app_settings
from app.mongo_models import (
    BookResearch, 
    init_beanie_models, 
    ResearchTask, 
    TaskStatusEnum, 
    BookResearchWithSimilarity,
)
from app.ai import (
    BookResearchService, 
    BookResearchOutput, 
    BookResearchInfo,
    BookRecommendService,
    BookRecommendOutput,
    BookExtractionService,
    BookExtractionOutput,
    AIServices,
)




ai_services = AIServices.from_api_key(app_settings.GOOGLE_API_KEY)

router = APIRouter()

mcp_app = FastMCP('Test tools.', stateless_http = True)




mcp_app.tool()
async def search_books(
    search_query: str = Query(..., description="Search query string"),
) -> str:
    '''Search books based on any relevant information.
    '''
    logging.log(logging.INFO, "Received search query: %s", search_query)

    await init_beanie_models()
    query_vector = await ai_services.embedding.generate_embedding(search_query)
    books = await BookResearch.vector_similarity(query_vector=query_vector, limit=5)

    out = ''
    for i, book in enumerate(books):
        out += f'# Book Result: {i}\n\n{book.book.as_string()}\n\n\n\n'
    return out


sse_app = mcp_app.sse_app()
streamable_app = mcp_app.streamable_http_app()
router.mount('mcp/', sse_app)
router.mount('mcp/streamable/', streamable_app)


