from __future__ import annotations
import dataclasses
from importlib.metadata import metadata
import pydantic
from google import genai
from google.genai import types


class BookResearchOutput(pydantic.BaseModel):
    info: BookResearchInfo = pydantic.Field(description="Comprehensive researched information about the book")
    sources: list[tuple[str, str]] = pydantic.Field(description="List of unique source URLs and their titles used in the research")
    provided_title: str = pydantic.Field(description="The title of the book as provided in the research request")
    provided_author: str|None = pydantic.Field(description="The author of the book as provided in the research request")

class BookResearchInfo(pydantic.BaseModel):
    title: str = pydantic.Field(description="The full title of the book")
    author: str = pydantic.Field(description="The author's name")
    isbn: str = pydantic.Field(description="The ISBN number (10 or 13 digits)")
    description: str = pydantic.Field(description="A description or summary of the book")
    publication_year: int = pydantic.Field(description="The year the book was published")
    
    # Genres as comma-separated list
    genres: str = pydantic.Field(description="Comma-separated list of genres")
    
    # Existing detailed fields
    general_style: str = pydantic.Field(description="Writing style, narrative approach, and literary techniques")
    target_audience: str = pydantic.Field(description="Age range, content appropriateness, and intended audience")
    similar_works: str = pydantic.Field(description="Other books, articles, or works that are similar")
    review_content: str = pydantic.Field(description="Common themes and content mentioned in reviews")
    author_background: str = pydantic.Field(description="Author's fame, biography, credentials, and other works")
    reception: str = pydantic.Field(description="Awards, ratings, bestseller lists, and critical reception")
    
    # New fields to help readers decide if they'd like the book
    reading_difficulty: str = pydantic.Field(description="Reading level: easy, moderate, challenging, or academic")
    emotional_tone: str = pydantic.Field(description="Overall emotional tone: dark, uplifting, melancholy, humorous, etc.")
    pacing: str = pydantic.Field(description="Story pacing: slow burn, fast-paced, episodic, etc.")
    major_themes: str = pydantic.Field(description="Main themes: love, betrayal, coming of age, survival, etc.")
    content_warnings: str = pydantic.Field(description="Content warnings: violence, sexual content, trauma, etc.")
    series_info: str = pydantic.Field(description="Series information: standalone, book number, part of universe, etc.")
    page_count: int = pydantic.Field(description="Approximate number of pages")
    narrative_pov: str = pydantic.Field(description="Narrative point of view: first person, third person limited, omniscient, etc.")
    setting_time_place: str = pydantic.Field(description="Setting details: time period and location")
    main_characters: str = pydantic.Field(description="Main character types, demographics, and personalities")
    notable_quotes: str = pydantic.Field(description="Memorable lines that capture the book's essence")
    reader_demographics: str = pydantic.Field(description="Typical reader demographics who enjoy this book")
    frequently_compared_to: str = pydantic.Field(description="Books frequently compared to this one")
    critical_consensus: str = pydantic.Field(description="What critics generally agree about the book")
    discussion_points: str = pydantic.Field(description="Common topics for book clubs and discussions")

@dataclasses.dataclass
class BookResearchService:
    client: genai.Client
    search_model: str = "gemini-2.5-flash"
    search_prompt: str = (
        'I need you to do research on a book titled \"{title}\" by \"{author}\". '
        " For this book, search the web thoroughly and find the following information:"
        "   + Basic Information: Full title, author name, ISBN, description/summary, publication year"
        "   + Genres: Specific genres as a comma-separated list"
        "   + Writing Style: General style, narrative approach, literary techniques"
        "   + Target Audience: Age range, content appropriateness, intended audience"
        "   + Similar Works: Other books, articles, or works that are similar"
        "   + Review Content: Common themes and content mentioned in reviews"
        "   + Author Background: Author's fame, biography, credentials, other works"
        "   + Reception: Awards, ratings, bestseller lists, critical reception"
        "   + Reading Experience: Reading difficulty level (easy/moderate/challenging/academic)"
        "   + Emotional Tone: Overall emotional tone (dark, uplifting, melancholy, humorous, etc.)"
        "   + Pacing: Story pacing (slow burn, fast-paced, episodic, etc.)"
        "   + Major Themes: Main themes (love, betrayal, coming of age, survival, etc.)"
        "   + Content Warnings: Any content warnings (violence, sexual content, trauma, etc.)"
        "   + Series Information: Standalone or part of series, book number, universe info"
        "   + Page Count: Approximate number of pages"
        "   + Narrative POV: Point of view (first person, third person limited, omniscient, etc.)"
        "   + Setting: Time period and place where the story occurs"
        "   + Main Characters: Character types, demographics, personalities"
        "   + Notable Quotes: Memorable lines that capture the book's essence"
        "   + Reader Demographics: Who typically enjoys this book"
        "   + Comparisons: Books this is frequently compared to"
        "   + Critical Consensus: What critics generally agree about"
        "   + Discussion Points: Common topics for book clubs and discussions"
        " Make sure you provide ALL of this information comprehensively - you can't miss a single point!"
    )
    structure_model: str = "gemini-2.5-flash"
    structure_prompt: str = (
        "Based on the following research output, structure the information as JSON:\n"
        "{research_output}"
    )

    @classmethod
    def from_api_key(cls, api_key: str) -> BookResearchService:
        """Create BookAIService instance from API key"""
        client = genai.Client(api_key=api_key)
        return cls(client=client)
    
    def research_book(self, title: str, author: str|None) -> BookResearchOutput:
        """Perform comprehensive research on a book and return structured info"""
        research_output, sources = self._search_book_info(title=title, author=author)
        structured_info = self._structure_book_info(research_output=research_output)
        return BookResearchOutput(
            info=structured_info,
            sources=sources,
            provided_title=title,
            provided_author=author
        )
    
    def _structure_book_info(self, research_output: str) -> BookResearchInfo:
        """Structure the research output into BookResearchInfo dataclass"""
        structure_response = self.client.models.generate_content(
            model=self.structure_model,
            contents=self.structure_prompt.format(research_output=research_output),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=BookResearchInfo # <--- Pass your Pydantic class here!
            )
        )

    def _search_book_info(self, title: str, author: str|None) -> tuple[str, list[tuple[str, str]]]:
        """Search for book information using Google GenAI"""
        response = self.client.models.generate_content(
            model=self.search_model,
            contents=self.search_prompt.format(title=title, author=author or "Unknown Author"),
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )
        return response.parsed, self._get_unique_sources(response=response)
    
    @staticmethod
    def _get_unique_sources(response: types.GenerateContentResponse) -> list[tuple[str, str]]:
        """Extract unique source URLs from grounding metadata"""
        metadata = response.candidates[0].grounding_metadata
        if metadata is None:
            return []
        
        sources = {}
        if metadata and metadata.grounding_chunks:
            for chunk in metadata.grounding_chunks:
                if chunk.web:
                    url = chunk.web.uri
                    if url not in sources:
                        sources[url] = chunk.web.title
        return [(v,k) for k,v in sources.items()]