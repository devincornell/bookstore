from sqlalchemy.orm import Session
from app.database import get_db


# Dependency to get database session
def get_database_session():
    return get_db