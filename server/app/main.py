from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
#from app.api.endpoints.books import router as books_router
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from pymongo import AsyncMongoClient


from app.core.config import app_settings
from app.api.endpoints import (
    books_router, 
    mount_mcp_apps, 
    mcp_app,
    research_router,
    extract_router,
)

class DatabaseManager:
    def __init__(self, uri: str, db_name: str):
        self.uri = uri
        self.db_name = db_name
        self.client: AsyncMongoClient = None
        self.db = None

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        self.client = AsyncMongoClient(self.uri, maxPoolSize=50)
        self.db = self.client[self.db_name]
        
        try:
            await self.client.admin.command('ping')
            yield
        finally:
            # 2. Teardown: Close when the app stops
            if self.client:
                self.client.close()

# Initialize the manager instance
db_manager = DatabaseManager(
    uri=app_settings.MONGODB_URL, 
    db_name=app_settings.MONGODB_DB_NAME
)

# Dependency to get the database instance in routes
async def get_db():
    return db_manager.db


def create_app() -> FastAPI:

    # Create FastAPI instance
    app = FastAPI(
        title="Bookstore API",
        description="A FastAPI application for managing a bookstore with SQLAlchemy ORM",
        version="1.0.0",
        #docs_url="/docs",
        #redoc_url="/redoc"
        lifespan=db_manager.lifespan,
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
    def health_check():
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