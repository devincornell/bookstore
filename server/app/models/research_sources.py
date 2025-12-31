import typing
import datetime
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database import Base

class ResearchSource(Base):
    __tablename__ = "research_sources"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Foreign key to book
    book_id: Mapped[int] = mapped_column(Integer, ForeignKey("book_infos.id"), nullable=False)
    
    # Source information
    name: Mapped[str] = mapped_column(Text, nullable=False)  # Source title/name
    url: Mapped[str] = mapped_column(Text, nullable=False)   # Source URL
    
    # Relationship back to book
    book: Mapped["BookInfo"] = relationship(back_populates="sources")

    @classmethod
    def from_name_url(cls, book_id: int, name: str, url: str) -> typing.Self:
        """Create ResearchSource instance from BookResearchSource data."""
        return cls(
            book_id=book_id,
            name=name,
            url=url
        )