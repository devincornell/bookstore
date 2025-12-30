from sqlalchemy import Column, String, Text, Integer
from app.models.base import BaseModel


class Book(BaseModel):
    __tablename__ = "books"
    
    # Basic book information - unlimited length for flexibility
    title = Column(Text, nullable=False, index=True)
    author = Column(Text, nullable=False, index=True)
    isbn = Column(String(13), unique=True, index=True)
    description = Column(Text)
    publication_year = Column(Integer)
    
    # Genres as comma-separated list
    genres = Column(Text)  # Store comma-separated list of genres
    
    # Existing detailed fields
    general_style = Column(Text)  # Writing style, narrative approach, etc.
    target_audience = Column(Text)  # Age range, content warnings, intended audience
    similar_works = Column(Text)  # Other books/articles that are similar
    review_content = Column(Text)  # Common themes/content mentioned in reviews
    author_background = Column(Text)  # Author fame, biography, credentials
    reception = Column(Text)  # Awards, ratings, bestseller lists, critical reception
    
    # New fields to help readers decide if they'd like the book
    reading_difficulty = Column(Text)  # Easy, moderate, challenging, academic
    emotional_tone = Column(Text)  # Dark, uplifting, melancholy, humorous, etc.
    pacing = Column(Text)  # Slow burn, fast-paced, episodic, etc.
    major_themes = Column(Text)  # Love, betrayal, coming of age, survival, etc.
    content_warnings = Column(Text)  # Violence, sexual content, trauma, etc.
    series_info = Column(Text)  # Standalone, book 1 of 3, part of universe, etc.
    page_count = Column(Integer)  # Approximate length
    narrative_pov = Column(Text)  # First person, third person limited, omniscient, etc.
    setting_time_place = Column(Text)  # Medieval England, modern NYC, far future, etc.
    main_characters = Column(Text)  # Character types, demographics, personalities
    notable_quotes = Column(Text)  # Memorable lines that capture the book's essence
    reader_demographics = Column(Text)  # Who typically enjoys this book
    frequently_compared_to = Column(Text)  # "If you liked X, you'll love this"
    critical_consensus = Column(Text)  # What critics generally agree about
    discussion_points = Column(Text)  # Common topics for book clubs/discussions
    reception = Column(Text)  
    
    def get_embedding_text(self) -> str:
        """
        Generate text representation for embedding generation (excludes author).
        Combines all relevant book fields into a single text for vector embedding.
        """
        text_parts = []
        
        # Always include title
        if self.title:
            text_parts.append(f"Title: {self.title}")
        
        # Include all descriptive fields (excluding author per request)
        field_mappings = [
            ("Description", self.description),
            ("Genres", self.genres),
            ("General Style", self.general_style),
            ("Target Audience", self.target_audience),
            ("Similar Works", self.similar_works),
            ("Review Content", self.review_content),
            ("Reception", self.reception),
            ("Reading Difficulty", self.reading_difficulty),
            ("Emotional Tone", self.emotional_tone),
            ("Pacing", self.pacing),
            ("Major Themes", self.major_themes),
            ("Content Warnings", self.content_warnings),
            ("Series Info", self.series_info),
            ("Narrative POV", self.narrative_pov),
            ("Setting", self.setting_time_place),
            ("Main Characters", self.main_characters),
            ("Critical Consensus", self.critical_consensus),
            ("Discussion Points", self.discussion_points),
        ]
        
        for label, value in field_mappings:
            if value and value.strip():
                text_parts.append(f"{label}: {value.strip()}")
        
        # Add publication year if available
        if self.publication_year:
            text_parts.append(f"Published: {self.publication_year}")
        
        return " | ".join(text_parts)
    
    def __repr__(self):
        return f"<Book(title='{self.title}', author='{self.author}')>"