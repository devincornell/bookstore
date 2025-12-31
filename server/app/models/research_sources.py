import typing
from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON, DateTime, func
from sqlalchemy.orm import relationship

from app.ai import BookResearchSource

class ResearchSource:
    __tablename__ = "research_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Foreign key to book
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    
    # Source information
    name = Column(Text, nullable=False)  # Source title/name
    url = Column(Text, nullable=False)   # Source URL
    
    # Relationship back to book
    book = relationship("Book", back_populates="sources")

    @classmethod
    def from_name_url(cls, book_id: int, name: str, url: str) -> typing.Self:
        """Create ResearchSource instance from BookResearchSource data."""
        return cls(
            book_id=book_id,
            name=name,
            url=url
        )