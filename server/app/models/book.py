from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Book(BaseModel):
    __tablename__ = "books"
    
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
    
    def get_embedding_text(self) -> str:
        """
        Generate text representation for embedding generation (excludes author).
        Combines all relevant book fields into a single text for vector embedding.
        """
        text_parts = []
        
        # Always include title
        if self.title:
            text_parts.append(f"Title: {self.title}")
        
        # Include all descriptive text fields
        field_mappings = [
            ("Description", self.description),
            ("General Style", self.general_style),
            ("Target Audience", self.target_audience),
            ("Emotional Tone", self.emotional_tone),
            ("Pacing", self.pacing),
            ("Content Warnings", self.content_warnings),
            ("Narrative POV", self.narrative_pov),
            ("Setting", self.setting_time_place),
            ("Critical Consensus", self.critical_consensus),
            ("Author Background", self.author_background),
            ("Reading Difficulty", self.reading_difficulty),
            ("Spicy Rating", self.spicy_rating),
            ("Series Title", self.series_title),
            ("Series Description", self.series_description),
            ("Reception Overview", self.reception_overview),
        ]
        
        for label, value in field_mappings:
            if value and value.strip():
                text_parts.append(f"{label}: {value.strip()}")
        
        # Handle JSON list fields
        json_field_mappings = [
            ("Genres", self.genres),
            ("Similar Works", self.similar_works),
            ("Frequently Compared To", self.frequently_compared_to),
            ("Awards", self.awards),
            ("Review Quotes", self.review_quotes),
        ]
        
        for label, value in json_field_mappings:
            if value and isinstance(value, list) and len(value) > 0:
                text_parts.append(f"{label}: {', '.join(map(str, value))}")
        
        # Add numeric fields if available
        if self.publication_year:
            text_parts.append(f"Published: {self.publication_year}")
        if self.page_count:
            text_parts.append(f"Pages: {self.page_count}")
        if self.word_count:
            text_parts.append(f"Words: {self.word_count}")
        
        return " | ".join(text_parts)
    
    def __repr__(self):
        return f"<Book(title='{self.title}', author='{self.author}')>"


class BookSource(BaseModel):
    __tablename__ = "book_sources"
    
    # Foreign key to book
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    
    # Source information
    name = Column(Text, nullable=False)  # Source title/name
    url = Column(Text, nullable=False)   # Source URL
    
    # Relationship back to book
    book = relationship("Book", back_populates="sources")