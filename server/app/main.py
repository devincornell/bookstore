from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
#from app.api.endpoints.books import router as books_router
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from pymongo import AsyncMongoClient

from .mongo_models import BookManager
from app.core import app_settings, get_book_manager, book_db
from app.api.endpoints import (
    books_router, 
    mount_mcp_apps, 
    mcp_app,
    research_router,
    extract_router,
)



def create_app() -> FastAPI:

    # Create FastAPI instance
    app = FastAPI(
        title="Bookstore API",
        description="A FastAPI application for managing a bookstore with SQLAlchemy ORM",
        version="1.0.0",
        #docs_url="/docs",
        #redoc_url="/redoc"
        lifespan=book_db.lifespan,
    )

    # Configure templates
    templates = Jinja2Templates(directory="templates")

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure this properly in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    mount_mcp_apps(app)

    app.include_router(
        books_router,
        prefix="/books",
        tags=["books"]
    )

    app.include_router(
        research_router,
        prefix="/research",
        tags=["research"]
    )

    app.include_router(
        extract_router,
        prefix="/extract",
        tags=["extract"]
    )

    @app.get("/", response_class=HTMLResponse)
    async def bookstore_frontend(request: Request):
        """Serve the bookstore frontend HTML page"""
        return templates.TemplateResponse("bookstore.html", {"request": request})

    @app.get("/health")
    async def health_check(book_manager: BookManager = Depends(get_book_manager)):
        """Health check endpoint"""
        return {"status": "healthy"}
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=app_settings.HOST,
        port=app_settings.PORT,
        reload=app_settings.DEBUG
    )