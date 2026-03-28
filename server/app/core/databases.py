from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
#from app.api.endpoints.books import router as books_router
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from pymongo import AsyncMongoClient
import pymongo
from app.core.config import app_settings

_client: pymongo.AsyncMongoClient|None = None

async def close_database_connection():
    """Close the MongoDB connection. Call this on app shutdown."""
    global _client
    if _client:
        _client.close()
        _client = None

# Store client as module-level variable for reuse

async def get_database_client(pool_size: int = 50, timeout: int = 5000) -> pymongo.AsyncMongoClient:
    """Get or create the MongoDB client singleton."""
    global _client
    if _client is None:
        _client = pymongo.AsyncMongoClient(app_settings.MONGODB_URL, maxPoolSize=pool_size, serverSelectionTimeoutMS=timeout)
    return _client


async def get_book_manager(db=Depends(get_db)):
    return BookManager.from_database(db)

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
