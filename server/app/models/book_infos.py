import typing
from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON, DateTime, func
from sqlalchemy.orm import relationship

from app.ai import BookResearchInfo
from app.database import Base

class BookInfo(Base):
    __tablename__ = "book_infos"
    model_config = ConfigDict(from_attributes=True) # Tells Pydantic to read from ORM attributes
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Basic book information (matches BookResearchInfo)
    title = Column(Text, nullable=False, index=True)
    author = Column(Text, nullable=False, index=True)
    publication_year = Column(Integer)
    isbn = Column(String(20), unique=True, index=True)  # Allow for longer ISBNs
    
    # Series information
    series_title = Column(Text)  # If part of series, else 'Standalone'
    series_description = Column(Text)  # Brief description of the series
    series_entry_number = Column(Text)  # Book's entry number in series
    other_series_entries = Column(JSON)  # List of other books in series
    
    # Reception information  
    awards = Column(JSON)  # List of awards won
    ratings = Column(JSON)  # List of ratings from major sources
    bestseller_lists = Column(JSON)  # List of bestseller lists appeared on
    review_quotes = Column(JSON)  # Notable quotes from reviews
    critical_consensus = Column(Text)  # What critics generally agree
    reception_overview = Column(Text)  # Overall summary of reception
    
    # Content information
    page_count = Column(Integer)
    word_count = Column(Integer)
    description = Column(Text)  # Book summary/description
    emotional_tone = Column(Text)  # Dark, uplifting, melancholy, etc.
    spicy_rating = Column(Text)  # Content spiciness: None, Mild, Moderate, Hot, Extra Hot
    content_warnings = Column(Text)  # Violence, sexual content, trauma, etc.
    target_audience = Column(Text)  # Age range and intended audience
    reader_demographics = Column(Text)  # Typical reader demographics
    setting_time_place = Column(Text)  # Time period and location
    
    # Narrative and writing style
    general_style = Column(Text)  # Writing style and literary techniques
    pacing = Column(Text)  # Slow burn, fast-paced, episodic, etc.
    reading_difficulty = Column(Text)  # Easy, moderate, challenging, academic
    narrative_pov = Column(Text)  # First person, third person limited, etc.
    
    # Literary context
    genres = Column(JSON)  # List of genres
    similar_works = Column(JSON)  # List of similar works
    frequently_compared_to = Column(JSON)  # Books frequently compared to
    
    # Author information
    author_other_series = Column(JSON)  # Other series by author
    author_other_works = Column(JSON)  # Other notable works by author  
    author_background = Column(Text)  # Author biography and credentials
    
    # Relationship to sources
    sources = relationship("BookSource", back_populates="book", cascade="all, delete-orphan")

    @classmethod
    def from_research_info(cls, info: BookResearchInfo) -> typing.Self:
        '''Create BookInfo instance from BookResearchInfo data.'''
        return cls(
            title=info.title,
            author=info.author,
            publication_year=info.publication_year,
            isbn=info.isbn,
            series_title=info.series_title,
            series_description=info.series_description,
            series_entry_number=info.series_entry_number,
            other_series_entries=info.other_series_entries,
            awards=info.awards,
            ratings=info.ratings,
            bestseller_lists=info.bestseller_lists,
            review_quotes=info.review_quotes,
            critical_consensus=info.critical_consensus,
            reception_overview=info.reception_overview,
            page_count=info.page_count,
            word_count=info.word_count,
            description=info.description,
            emotional_tone=info.emotional_tone,
            spicy_rating=info.spicy_rating,
            content_warnings=info.content_warnings,
            target_audience=info.target_audience,
            reader_demographics=info.reader_demographics,
            setting_time_place=info.setting_time_place,
            general_style=info.general_style,
            pacing=info.pacing,
            reading_difficulty=info.reading_difficulty,
            narrative_pov=info.narrative_pov,
            genres=info.genres,
            similar_works=info.similar_works,
            frequently_compared_to=info.frequently_compared_to,
            author_other_series=info.author_other_series,
            author_other_works=info.author_other_works,
            author_background=info.author_background
        )
    
    def get_textual_representation(self) -> str:
        '''Format all object properties into human-readable string so that it may be used in an LLM.'''
        return format_book_info_as_text(self)

    def __repr__(self):
        return f"<Book(title='{self.title}', author='{self.author}')>"
    





def format_book_info_as_text(book_info: BookInfo) -> str:
    """
    Format a BookInfo object's properties into human-readable string for LLM processing.
    
    Args:
        book_info: BookInfo instance to format
        
    Returns:
        Formatted string representation of the book information
    """
    sections = []
    
    # Basic Information
    basic_info = f"Title: {book_info.title or 'Unknown'}"
    basic_info += f"\nAuthor: {book_info.author or 'Unknown'}"
    if book_info.publication_year:
        basic_info += f"\nPublication Year: {book_info.publication_year}"
    if book_info.isbn:
        basic_info += f"\nISBN: {book_info.isbn}"
    sections.append(f"=== BASIC INFORMATION ===\n{basic_info}")
    
    # Series Information
    if book_info.series_title or book_info.series_description or book_info.other_series_entries:
        series_info = ""
        if book_info.series_title:
            series_info += f"Series: {book_info.series_title}"
        if book_info.series_entry_number:
            series_info += f" (Book {book_info.series_entry_number})"
        if book_info.series_description:
            series_info += f"\nSeries Description: {book_info.series_description}"
        if book_info.other_series_entries:
            other_books = ", ".join(book_info.other_series_entries) if isinstance(book_info.other_series_entries, list) else str(book_info.other_series_entries)
            series_info += f"\nOther Books in Series: {other_books}"
        sections.append(f"=== SERIES INFORMATION ===\n{series_info}")
    
    # Content Details
    content_info = ""
    if book_info.description:
        content_info += f"Description: {book_info.description}\n"
    if book_info.page_count:
        content_info += f"Page Count: {book_info.page_count}\n"
    if book_info.word_count:
        content_info += f"Word Count: {book_info.word_count}\n"
    if book_info.genres:
        genres = ", ".join(book_info.genres) if isinstance(book_info.genres, list) else str(book_info.genres)
        content_info += f"Genres: {genres}\n"
    if book_info.setting_time_place:
        content_info += f"Setting: {book_info.setting_time_place}\n"
    if book_info.target_audience:
        content_info += f"Target Audience: {book_info.target_audience}\n"
    if book_info.reader_demographics:
        content_info += f"Reader Demographics: {book_info.reader_demographics}\n"
    if book_info.emotional_tone:
        content_info += f"Emotional Tone: {book_info.emotional_tone}\n"
    if book_info.spicy_rating:
        content_info += f"Content Spiciness: {book_info.spicy_rating}\n"
    if book_info.content_warnings:
        content_info += f"Content Warnings: {book_info.content_warnings}\n"
    if content_info:
        sections.append(f"=== CONTENT DETAILS ===\n{content_info.rstrip()}")
    
    # Writing Style & Structure
    style_info = ""
    if book_info.general_style:
        style_info += f"Writing Style: {book_info.general_style}\n"
    if book_info.narrative_pov:
        style_info += f"Narrative POV: {book_info.narrative_pov}\n"
    if book_info.pacing:
        style_info += f"Pacing: {book_info.pacing}\n"
    if book_info.reading_difficulty:
        style_info += f"Reading Difficulty: {book_info.reading_difficulty}\n"
    if style_info:
        sections.append(f"=== WRITING STYLE ===\n{style_info.rstrip()}")
    
    # Reception & Awards
    reception_info = ""
    if book_info.awards:
        awards = ", ".join(book_info.awards) if isinstance(book_info.awards, list) else str(book_info.awards)
        reception_info += f"Awards: {awards}\n"
    if book_info.bestseller_lists:
        lists = ", ".join(book_info.bestseller_lists) if isinstance(book_info.bestseller_lists, list) else str(book_info.bestseller_lists)
        reception_info += f"Bestseller Lists: {lists}\n"
    if book_info.ratings:
        ratings = str(book_info.ratings)
        reception_info += f"Ratings: {ratings}\n"
    if book_info.critical_consensus:
        reception_info += f"Critical Consensus: {book_info.critical_consensus}\n"
    if book_info.reception_overview:
        reception_info += f"Reception Overview: {book_info.reception_overview}\n"
    if book_info.review_quotes:
        quotes = str(book_info.review_quotes)
        reception_info += f"Notable Review Quotes: {quotes}\n"
    if reception_info:
        sections.append(f"=== RECEPTION & AWARDS ===\n{reception_info.rstrip()}")
    
    # Literary Context
    context_info = ""
    if book_info.similar_works:
        similar = ", ".join(book_info.similar_works) if isinstance(book_info.similar_works, list) else str(book_info.similar_works)
        context_info += f"Similar Works: {similar}\n"
    if book_info.frequently_compared_to:
        compared = ", ".join(book_info.frequently_compared_to) if isinstance(book_info.frequently_compared_to, list) else str(book_info.frequently_compared_to)
        context_info += f"Frequently Compared To: {compared}\n"
    if context_info:
        sections.append(f"=== LITERARY CONTEXT ===\n{context_info.rstrip()}")
    
    # Author Information
    author_info = ""
    if book_info.author_background:
        author_info += f"Author Background: {book_info.author_background}\n"
    if book_info.author_other_works:
        other_works = ", ".join(book_info.author_other_works) if isinstance(book_info.author_other_works, list) else str(book_info.author_other_works)
        author_info += f"Author's Other Works: {other_works}\n"
    if book_info.author_other_series:
        other_series = ", ".join(book_info.author_other_series) if isinstance(book_info.author_other_series, list) else str(book_info.author_other_series)
        author_info += f"Author's Other Series: {other_series}\n"
    if author_info:
        sections.append(f"=== AUTHOR INFORMATION ===\n{author_info.rstrip()}")
    
    return "\n\n".join(sections)


