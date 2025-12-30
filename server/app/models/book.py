from sqlalchemy import Column, String, Text, Numeric, Integer
from app.models.base import BaseModel


class Book(BaseModel):
    __tablename__ = "books"
    
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)
    isbn = Column(String(13), unique=True, index=True)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    stock_quantity = Column(Integer, default=0)
    genre = Column(String(100))
    publication_year = Column(Integer)
    
    def __repr__(self):
        return f"<Book(title='{self.title}', author='{self.author}')>"