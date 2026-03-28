
from fastapi import Depends
from app.db.mongodb import db_manager
from server.app.mongo_models.book_manager import BookManager

async def get_db():
    # Returns the database instance from our manager
    return db_manager.db

async def get_book_manager(db=Depends(get_db)):
    return BookManager.from_database(db)
