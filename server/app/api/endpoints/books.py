"""
API endpoints for book research functionality using pydantic-ai
"""
import typing
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks, FastAPI
import pydantic
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, Field
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


@router.get("/recommend", response_model=BookRecommendOutput)
async def books_recommend(
    recommend_criteria: Optional[str] = Query(None, description="Criteria for recommending books")
) -> BookRecommendOutput:
    await init_beanie_models()
    books = await BookResearch.find_all().to_list()
    return await ai_services.recommend.recommend_books(
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


class BookWithSimilarityListResponse(BaseModel):
    books: list[BookResearchWithSimilarity] = pydantic.Field(description="List of researched books with similarity scores")

@router.get("/search", response_model=BookWithSimilarityListResponse)
async def books_list(
    q: str = Query(..., description="Text query to search for similar books"),
    top_n: int = Query(5, description="Number of top similar books to return"),
) -> BookWithSimilarityListResponse:
    await init_beanie_models()
    query_vector = await ai_services.embedding.generate_embedding(q)
    books = await BookResearch.vector_similarity(query_vector=query_vector, limit=top_n)
    return BookWithSimilarityListResponse(
        books=books
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

@router.get("/clear")
async def books_clear(
) -> bool:
    await init_beanie_models()
    await BookResearch.delete_all()
    return True


@mcp_app.tool()
async def search_books(
    search_query: str = Query(..., description="Search query string"),
) -> str:
    '''OFFICIAL BOOKSTORE TOOL. Search bookstore based on any relevant information.
    '''
    logging.log(logging.INFO, "Received search query: %s", search_query)

    await init_beanie_models()
    query_vector = await ai_services.embedding.generate_embedding(search_query)
    books = await BookResearch.vector_similarity(query_vector=query_vector, limit=5)

    out = ''
    for i, book in enumerate(books):
        out += f'# Book Result: {i}\n\n{book.book.as_string()}\n\n\n\n'
    return out

def mount_mcp_apps(router: APIRouter|FastAPI) -> None:
    """Mount MCP apps to the given router."""
    sse_app = mcp_app.sse_app()
    streamable_app = mcp_app.streamable_http_app()
    router.mount('/mcp/sse/', sse_app)
    router.mount('/mcp/streamable/', streamable_app)


