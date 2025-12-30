"""
Comprehensive book research service using AI to gather detailed information about books
"""

import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.ai.text_generation import get_book_text_generator
from app.models.book import Book
from app.schemas.book import BookCreate
import json
import re

logger = logging.getLogger(__name__)

class BookResearchService:
    """Service for comprehensive book research using AI"""
    
    def __init__(self):
        self.text_generator = get_book_text_generator()
    
    async def research_book_comprehensive(
        self,
        title: str,
        author: Optional[str] = None,
        publication_year: Optional[int] = None,
        isbn: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive research on a book using AI to gather all possible information
        
        Args:
            title: Book title (can be approximate)
            author: Author name (optional)
            publication_year: Publication year (optional)
            isbn: ISBN if known (optional)
            
        Returns:
            Dictionary with comprehensive book information
        """
        try:
            logger.info(f"Starting comprehensive research for: {title}")
            
            # Step 1: Basic book identification and core info
            basic_info = await self._research_basic_info(title, author, publication_year, isbn)
            
            # Step 2: Reader experience research
            reader_info = await self._research_reader_experience(basic_info)
            
            # Step 3: Critical and academic analysis
            critical_info = await self._research_critical_analysis(basic_info)
            
            # Step 4: Author and context research
            context_info = await self._research_author_context(basic_info)
            
            # Step 5: Community and discussion research
            community_info = await self._research_community_aspects(basic_info)
            
            # Combine all research
            comprehensive_data = {
                **basic_info,
                **reader_info,
                **critical_info,
                **context_info,
                **community_info,
                "research_completeness": self._assess_completeness({
                    **basic_info, **reader_info, **critical_info, **context_info, **community_info
                })
            }
            
            return comprehensive_data
            
        except Exception as e:
            logger.error(f"Error in comprehensive book research: {str(e)}")
            raise
    
    async def _research_basic_info(
        self, title: str, author: Optional[str], year: Optional[int], isbn: Optional[str]
    ) -> Dict[str, Any]:
        """Research basic book identification and core information"""
        
        author_text = f"by {author}" if author else ""
        year_text = f"published in {year}" if year else ""
        isbn_text = f"ISBN: {isbn}" if isbn else ""
        
        prompt = f"""
        Research the book "{title}" {author_text} {year_text} {isbn_text}.
        
        Provide comprehensive basic information in JSON format:
        {{
            "verified_title": "exact title",
            "verified_author": "full author name",
            "verified_publication_year": year,
            "isbn": "ISBN if found",
            "description": "comprehensive plot/content summary",
            "genres": "comma-separated list of genres",
            "page_count": approximate_pages,
            "series_info": "standalone or series details",
            "publisher": "publisher name",
            "original_language": "language if not English originally"
        }}
        
        Be as accurate as possible. If information is uncertain, indicate with "approximately" or "likely".
        """
        
        response = await self.text_generator.model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 1000,
                "temperature": 0.2,
                "top_p": 0.8,
            }
        )
        
        try:
            return json.loads(response.text.strip())
        except json.JSONDecodeError:
            logger.warning("Could not parse basic info JSON, using fallback")
            return {"verified_title": title, "verified_author": author or "Unknown"}
    
    async def _research_reader_experience(self, basic_info: Dict[str, Any]) -> Dict[str, Any]:
        """Research aspects that help readers decide if they'd enjoy the book"""
        
        title = basic_info.get("verified_title", "")
        author = basic_info.get("verified_author", "")
        
        prompt = f"""
        Analyze "{title}" by {author} from a reader's perspective.
        
        Provide detailed reader experience information in JSON format:
        {{
            "reading_difficulty": "easy/moderate/challenging/academic - with explanation",
            "emotional_tone": "overall emotional feeling of the book",
            "pacing": "detailed description of how fast/slow the story moves",
            "major_themes": "comma-separated list of main themes explored",
            "content_warnings": "any potentially triggering content",
            "target_audience": "detailed description of ideal readers",
            "narrative_pov": "first person/third person/etc with details",
            "setting_time_place": "when and where the story takes place",
            "main_characters": "description of protagonists and character types",
            "notable_quotes": "2-3 memorable or representative quotes",
            "reader_demographics": "who typically enjoys this book"
        }}
        
        Focus on helping potential readers understand what reading this book would be like.
        """
        
        response = await self.text_generator.model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 1200,
                "temperature": 0.3,
                "top_p": 0.8,
            }
        )
        
        try:
            return json.loads(response.text.strip())
        except json.JSONDecodeError:
            logger.warning("Could not parse reader experience JSON")
            return {}
    
    async def _research_critical_analysis(self, basic_info: Dict[str, Any]) -> Dict[str, Any]:
        """Research critical reception and literary analysis"""
        
        title = basic_info.get("verified_title", "")
        author = basic_info.get("verified_author", "")
        
        prompt = f"""
        Analyze the critical reception and literary significance of "{title}" by {author}.
        
        Provide critical analysis in JSON format:
        {{
            "critical_consensus": "what critics generally agree about this book",
            "reception": "awards, accolades, bestseller lists, critical ratings",
            "general_style": "detailed analysis of writing style and technique",
            "frequently_compared_to": "books this is commonly compared to",
            "discussion_points": "topics often discussed in reviews and book clubs",
            "literary_significance": "importance in its genre or literature generally",
            "review_content": "common themes mentioned in professional and reader reviews"
        }}
        
        Focus on objective analysis and documented reception.
        """
        
        response = await self.text_generator.model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 1000,
                "temperature": 0.25,
                "top_p": 0.8,
            }
        )
        
        try:
            return json.loads(response.text.strip())
        except json.JSONDecodeError:
            logger.warning("Could not parse critical analysis JSON")
            return {}
    
    async def _research_author_context(self, basic_info: Dict[str, Any]) -> Dict[str, Any]:
        """Research author background and book context"""
        
        author = basic_info.get("verified_author", "")
        title = basic_info.get("verified_title", "")
        
        prompt = f"""
        Research the author {author} and the context of "{title}".
        
        Provide author and context information in JSON format:
        {{
            "author_background": "detailed biography, other works, writing style, reputation",
            "similar_works": "other books by this author and similar books by other authors",
            "book_context": "when this was written and why, author's intent",
            "author_significance": "the author's place in literature/their genre"
        }}
        
        Provide factual, verifiable information about the author and their work.
        """
        
        response = await self.text_generator.model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 800,
                "temperature": 0.2,
                "top_p": 0.8,
            }
        )
        
        try:
            return json.loads(response.text.strip())
        except json.JSONDecodeError:
            logger.warning("Could not parse author context JSON")
            return {}
    
    async def _research_community_aspects(self, basic_info: Dict[str, Any]) -> Dict[str, Any]:
        """Research community discussion and reader engagement"""
        
        title = basic_info.get("verified_title", "")
        
        prompt = f"""
        Research how readers and communities engage with "{title}".
        
        Provide community engagement information in JSON format:
        {{
            "book_club_appeal": "why this book works well or poorly for book clubs",
            "discussion_topics": "common discussion points and debate topics",
            "reader_reactions": "typical reader reactions and emotional responses",
            "cultural_impact": "any broader cultural significance or influence",
            "adaptation_info": "any movie, TV, or other adaptations",
            "fan_community": "whether there's an active fan community"
        }}
        
        Focus on how the book functions in reading communities and its social aspects.
        """
        
        response = await self.text_generator.model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": 600,
                "temperature": 0.3,
                "top_p": 0.8,
            }
        )
        
        try:
            return json.loads(response.text.strip())
        except json.JSONDecodeError:
            logger.warning("Could not parse community aspects JSON")
            return {}
    
    def _assess_completeness(self, data: Dict[str, Any]) -> float:
        """Assess how complete the research data is (0.0 to 1.0)"""
        
        required_fields = [
            "verified_title", "verified_author", "description", "genres",
            "reading_difficulty", "emotional_tone", "pacing", "major_themes"
        ]
        
        optional_fields = [
            "target_audience", "content_warnings", "series_info", "page_count",
            "narrative_pov", "setting_time_place", "main_characters", "reception",
            "critical_consensus", "author_background", "similar_works"
        ]
        
        required_score = sum(1 for field in required_fields if data.get(field))
        optional_score = sum(1 for field in optional_fields if data.get(field))
        
        required_weight = 0.7
        optional_weight = 0.3
        
        total_score = (
            (required_score / len(required_fields)) * required_weight +
            (optional_score / len(optional_fields)) * optional_weight
        )
        
        return round(total_score, 2)
    
    async def create_book_from_research(
        self, 
        research_data: Dict[str, Any],
        db: Session
    ) -> Book:
        """
        Create a Book object from comprehensive research data
        
        Args:
            research_data: Result from research_book_comprehensive
            db: Database session
            
        Returns:
            Book model instance
        """
        try:
            # Map research data to book schema
            book_data = {
                "title": research_data.get("verified_title", "Unknown Title"),
                "author": research_data.get("verified_author", "Unknown Author"),
                "isbn": research_data.get("isbn"),
                "description": research_data.get("description"),
                "publication_year": research_data.get("verified_publication_year"),
                "genres": research_data.get("genres"),
                "general_style": research_data.get("general_style"),
                "target_audience": research_data.get("target_audience"),
                "similar_works": research_data.get("similar_works"),
                "review_content": research_data.get("review_content"),
                "author_background": research_data.get("author_background"),
                "reception": research_data.get("reception"),
                "reading_difficulty": research_data.get("reading_difficulty"),
                "emotional_tone": research_data.get("emotional_tone"),
                "pacing": research_data.get("pacing"),
                "major_themes": research_data.get("major_themes"),
                "content_warnings": research_data.get("content_warnings"),
                "series_info": research_data.get("series_info"),
                "page_count": research_data.get("page_count"),
                "narrative_pov": research_data.get("narrative_pov"),
                "setting_time_place": research_data.get("setting_time_place"),
                "main_characters": research_data.get("main_characters"),
                "notable_quotes": research_data.get("notable_quotes"),
                "reader_demographics": research_data.get("reader_demographics"),
                "frequently_compared_to": research_data.get("frequently_compared_to"),
                "critical_consensus": research_data.get("critical_consensus"),
                "discussion_points": research_data.get("discussion_points"),
            }
            
            # Remove None values
            book_data = {k: v for k, v in book_data.items() if v is not None}
            
            # Create Book object
            book = Book(**book_data)
            
            # Save to database
            db.add(book)
            db.commit()
            db.refresh(book)
            
            logger.info(f"Successfully created book: {book.title} by {book.author}")
            return book
            
        except Exception as e:
            logger.error(f"Error creating book from research: {str(e)}")
            db.rollback()
            raise

# Global service instance
book_research_service: Optional[BookResearchService] = None

def get_book_research_service() -> BookResearchService:
    """Get the global book research service instance"""
    global book_research_service
    if book_research_service is None:
        book_research_service = BookResearchService()
    return book_research_service