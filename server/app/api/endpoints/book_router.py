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


from app.api.deps import get_book_manager
from app.core.config import app_settings

from app.mongo_models import (
    BookResearchWithSimilarity,
    BookManager,
    BookDoc,
    BookCollection,
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

ai_services = AIServices.from_service_account()

router = APIRouter()
mcp_app = FastMCP('Test tools.', stateless_http = True)


@router.get("/recommend", response_model=BookRecommendOutput)
async def books_recommend(
    recommend_criteria: Optional[str] = Query(None, description="Criteria for recommending books"),
    book_manager: BookManager = Depends(get_book_manager)
) -> BookRecommendOutput:
    books = await book_manager.books.find_all()
    return await ai_services.recommend.recommend_books(
        recommend_criteria=recommend_criteria,
        book_info=[br.research_output.info for br in books],
    )

class BookInfoResponse(BaseModel):
    id: str = pydantic.Field(description="MongoDB document ID of the researched book")
    info: BookResearchInfo = pydantic.Field(description="Detailed information about the researched book")

    @classmethod
    def from_book_research(cls, book_research: BookDoc) -> typing.Self:
        return cls(
            id=str(book_research.id),
            info=book_research.research_output.info
        )


class BookWithSimilarityListResponse(BaseModel):
    books: list[BookResearchWithSimilarity] = pydantic.Field(description="List of researched books with similarity scores")

@router.get("/search", response_model=BookWithSimilarityListResponse)
async def search_books(
    q: str = Query(..., description="Text query to search for similar books"),
    top_n: int = Query(5, description="Number of top similar books to return"),
    book_manager: BookManager = Depends(get_book_manager),
) -> BookWithSimilarityListResponse:
    query_vector = await ai_services.embedding.generate_embedding(q)
    books = await book_manager.books.vector_similarity(query_vector=query_vector, limit=top_n)
    return BookWithSimilarityListResponse(books=books)

class BookListResponse(BaseModel):
    books: list[BookInfoResponse] = pydantic.Field(description="List of researched books")

@router.get("/list", response_model=BookListResponse)
async def list_books(
    book_manager: BookManager = Depends(get_book_manager),
) -> BookListResponse:
    raw_docs = await book_manager.books._collection.find().to_list()
    books = [
        BookInfoResponse(id=str(doc["_id"]), info=BookDoc.model_validate(doc).research_output.info)
        for doc in raw_docs
    ]
    return BookListResponse(books=books)

@router.delete("/delete/{book_id}")
async def books_delete(
    book_id: str,
    book_manager: BookManager = Depends(get_book_manager),
):
    """Delete a book by its MongoDB document ID."""
    from bson import ObjectId
    try:
        result = await book_manager.books._collection.delete_one({"_id": ObjectId(book_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Book not found")
        return {"message": "Book deleted successfully", "deleted_id": book_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error deleting book: {str(e)}")

@router.get("/clear")
async def books_clear(
    book_manager: BookManager = Depends(get_book_manager),
) -> bool:
    await book_manager.books._collection.delete_many({})
    return True


@mcp_app.tool()
async def search_books_mcp(
    search_query: str,
) -> str:
    '''OFFICIAL BOOKSTORE TOOL. Search bookstore based on any relevant information.'''
    from app.db.mongodb import db_manager
    logging.log(logging.INFO, "Received search query: %s", search_query)
    book_manager = BookManager.from_database(db_manager.db)
    query_vector = await ai_services.embedding.generate_embedding(search_query)
    books = await book_manager.books.vector_similarity(query_vector=query_vector, limit=5)
    out = ''
    for i, book in enumerate(books):
        out += f'# Book Result: {i}\n\n{book.book.as_string()}\n\n\n\n'
    return out

def mount_mcp_apps(router: APIRouter|FastAPI) -> None:
    """Mount MCP apps to the given router."""
    sse_app = mcp_app.sse_app()
    streamable_app = mcp_app.streamable_http_app()
    router.mount('/mcp/sse/', sse_app)
    router.mount('/mcp/streamable/', streamable_app) # access at /mcp/streamable/mcp


