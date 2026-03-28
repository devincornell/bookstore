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

from ..mongo_models import BookManager

class MDB:
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
book_db = MDB(
    uri=app_settings.MONGODB_URL, 
    db_name=app_settings.MONGODB_DB_NAME
)

# Dependency to get the database instance in routes
async def get_db():
    return book_db.db

async def get_book_manager(db=Depends(get_db)):
    return BookManager.from_database(db)
