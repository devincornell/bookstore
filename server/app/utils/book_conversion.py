"""
Utility functions for converting between BookResearchOutput and database models
"""
from typing import List
from app.ai.research_service import BookResearchOutput, BookResearchInfo
from app.schemas.book import BookCreate, BookSourceCreate
from app.models.book import Book


def research_output_to_book_create(research_output: BookResearchOutput) -> tuple[BookCreate, List[BookSourceCreate]]:
    """
    Convert BookResearchOutput to BookCreate and BookSourceCreate objects
    for database storage.
    """
    info = research_output.info
    
    # Create book data
    book_data = BookCreate(
        # Basic information
        title=info.title,
        author=info.author,
        publication_year=info.publication_year,
        isbn=info.isbn,
        
        # Series information
        series_title=info.series_title,
        series_description=info.series_description,
        series_entry_number=info.series_entry_number,
        other_series_entries=info.other_series_entries or [],
        
        # Reception
        awards=info.awards or [],
        ratings=info.ratings or [],
        bestseller_lists=info.bestseller_lists or [],
        review_quotes=info.review_quotes or [],
        critical_consensus=info.critical_consensus,
        reception_overview=info.reception_overview,
        
        # Content
        page_count=info.page_count,
        word_count=info.word_count,
        description=info.description,
        emotional_tone=info.emotional_tone,
        spicy_rating=info.spicy_rating,
        content_warnings=info.content_warnings,
        target_audience=info.target_audience,
        reader_demographics=info.reader_demographics,
        setting_time_place=info.setting_time_place,
        
        # Narrative and writing style
        general_style=info.general_style,
        pacing=info.pacing,
        reading_difficulty=info.reading_difficulty,
        narrative_pov=info.narrative_pov,
        
        # Literary context
        genres=info.genres or [],
        similar_works=info.similar_works or [],
        frequently_compared_to=info.frequently_compared_to or [],
        
        # Author information
        author_other_series=info.author_other_series or [],
        author_other_works=info.author_other_works or [],
        author_background=info.author_background,
    )
    
    # Create sources data
    sources_data = [
        BookSourceCreate(
            name=source.get('name', ''),
            url=source.get('url', '')
        )
        for source in research_output.sources
    ]
    
    return book_data, sources_data


def book_model_to_research_info(book: Book) -> BookResearchInfo:
    """
    Convert Book model back to BookResearchInfo format
    (useful for API responses or further AI processing)
    """
    return BookResearchInfo(
        # Basic information
        title=book.title,
        author=book.author,
        publication_year=book.publication_year,
        isbn=book.isbn or "",
        
        # Series information
        series_title=book.series_title or "Standalone",
        series_description=book.series_description or "",
        series_entry_number=book.series_entry_number or "",
        other_series_entries=book.other_series_entries or [],
        
        # Reception
        awards=book.awards or [],
        ratings=book.ratings or [],
        bestseller_lists=book.bestseller_lists or [],
        review_quotes=book.review_quotes or [],
        critical_consensus=book.critical_consensus or "",
        reception_overview=book.reception_overview or "",
        
        # Content
        page_count=book.page_count or 0,
        word_count=book.word_count or 0,
        description=book.description or "",
        emotional_tone=book.emotional_tone or "",
        spicy_rating=book.spicy_rating or "",
        content_warnings=book.content_warnings or "",
        target_audience=book.target_audience or "",
        reader_demographics=book.reader_demographics or "",
        setting_time_place=book.setting_time_place or "",
        
        # Narrative and writing style
        general_style=book.general_style or "",
        pacing=book.pacing or "",
        reading_difficulty=book.reading_difficulty or "",
        narrative_pov=book.narrative_pov or "",
        
        # Literary context
        genres=book.genres or [],
        similar_works=book.similar_works or [],
        frequently_compared_to=book.frequently_compared_to or [],
        
        # Author information
        author_other_series=book.author_other_series or [],
        author_other_works=book.author_other_works or [],
        author_background=book.author_background or "",
    )