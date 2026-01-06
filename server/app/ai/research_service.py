from __future__ import annotations
import dataclasses
from importlib.metadata import metadata
import pydantic
from google import genai
from google.genai import types

from .base_client_service import BaseClientService
from .embedding_service import EmbeddingService

class BookResearchOutput(pydantic.BaseModel):
    info: BookResearchInfo = pydantic.Field(description="Comprehensive researched information about the book")
    sources: list[ResearchSource] = pydantic.Field(description="List of unique source URLs and their titles used in the research")

class ResearchSource(pydantic.BaseModel):
    name: str = pydantic.Field(description="The name or title of the source")
    url: str = pydantic.Field(description="The URL of the source")

class BookResearchInfo(pydantic.BaseModel):
    title: str = pydantic.Field(description="The full standard title of the book, not including subtitle or information about the series.")
    authors: list[str] = pydantic.Field(description="The authors' names. Not pen initials, and names should be in order - don't do 'last name, first name' format)")
    publication_year: int = pydantic.Field(description="The year the book was published")
    isbn: str = pydantic.Field(description="The ISBN number (10 or 13 digits)")
    
    # series information
    series_title: str = pydantic.Field(description="If the book is part of a series, the series title, else 'Standalone'")
    series_entry_number: int = pydantic.Field(description="If part of a series, the book's entry number in the series, else provide no number.")
    series_description: str = pydantic.Field(description="If part of a series, a brief description of the series, else provide no description.")
    other_series_entries: list[str] = pydantic.Field(description="Other books in the series with their titles, entry numbers, and publication years if applicable, else provide no entries.")

    # reception by critics
    awards: list[str] = pydantic.Field(description="List of any awards the book has won, else provide an empty list")
    bestseller_lists: list[str] = pydantic.Field(description="List of any bestseller lists the book has appeared on, else provide an empty list")
    critical_quotes: list[str] = pydantic.Field(description="Negative critical quotes from professional critics. Quotes about the things that were not good.")
    positive_quotes: list[str] = pydantic.Field(description="Positive quotes from critics.")
    critical_consensus: str = pydantic.Field(description="What critics generally agree about the book")

    # receptiion by users
    user_ratings: list[str] = pydantic.Field(description="List of ratings from major review sources. Follow the format 4.4/5 on Goodreads, 4.6/5 on Amazon, etc. Don't add extra text.")
    user_quotes: list[str] = pydantic.Field(description="Notable quotes from regular users - not critics, just regular users.")
    user_reception: str = pydantic.Field(description="Overall summary of the user reception of the book - not critics, just regular users.")

    # content
    page_count: int = pydantic.Field(description="Approximate number of pages")
    word_count: int = pydantic.Field(description="Approximate word count of the book")
    genres: list[str] = pydantic.Field(description="List of genres that the book belongs to. All genres should be lower-case.")
    description: str = pydantic.Field(description="A description or summary of the book")
    emotional_tone: str = pydantic.Field(description="Overall emotional tone: dark, uplifting, melancholy, humorous, etc.")
    spicy_rating: str = pydantic.Field(description="Content spicyness rating in number of chilly peppers ranging from 0 (clean) to 5 (explicit),")
    content_warnings: str = pydantic.Field(description="Content warnings: violence, sexual content, trauma, etc.")
    target_audience: str = pydantic.Field(description="Age range, content appropriateness, and intended audience")
    reader_demographics: str = pydantic.Field(description="Typical reader demographics who enjoy this book")
    setting_time_place: str = pydantic.Field(description="Setting details: time period and location")

    # narrative writing style
    general_style: str = pydantic.Field(description="Writing style, narrative approach, and literary techniques")
    pacing: str = pydantic.Field(description="Story pacing: slow burn, fast-paced, episodic, etc.")
    reading_difficulty: str = pydantic.Field(description="Reading level: easy, moderate, challenging, or academic")
    narrative_pov: str = pydantic.Field(description="Narrative point of view: first person, third person limited, omniscient, etc.")

    # other works
    
    similar_works: list[str] = pydantic.Field(description="Other books, articles, or works that are similar")
    frequently_compared_to: list[str] = pydantic.Field(description="Books frequently compared to this one")

    # author
    author_other_series: list[str] = pydantic.Field(description="Other series written by the author")
    author_other_works: list[str] = pydantic.Field(description="Other notable works by the author")
    author_background: str = pydantic.Field(description="Author's biography, credentials, and other relevant background information")

    def as_string(self) -> str:
        """Return a string representation of the book research info"""
        return self.model_dump_json(indent=2)
    

@dataclasses.dataclass
class BookResearchService(BaseClientService):
    search_model: str = "gemini-2.5-flash"
    search_prompt: str = (
        'I need you to do comprehensive research on a book titled \"{title}\". Here is some other info about the book: \"{other_info}\". '
        "Search the web thoroughly and provide detailed information for ALL of the following categories. "
        "Be thorough, specific, and comprehensive in your research:\n\n"
        
        "**BASIC BOOK INFORMATION:**\n"
        "- Full official title (including subtitle if any)\n"
        "- Complete author name (first and last name)\n"
        "- Publication year (exact year of first publication)\n"
        "- ISBN number (10 or 13 digit ISBN, prefer ISBN-13)\n\n"
        
        "**DETAILED BOOK DESCRIPTION:**\n"
        "- Comprehensive plot summary and description (2-3 paragraphs)\n"
        "- What the book is about, main plot points, key story elements\n"
        "- Book's central premise and what makes it unique\n\n"
        
        "**SERIES INFORMATION:**\n"
        "- If part of a series: official series name/title\n"
        "- If part of a series: brief description of what the series is about\n"
        "- If part of a series: this book's number/position in the series\n"
        "- If part of a series: list other books in the series with titles and publication years\n"
        "- If standalone: clearly state it's a standalone novel\n\n"
        
        "**CRITICAL RECEPTION & RECOGNITION:**\n"
        "- Complete list of any literary awards won (Hugo, Nebula, Pulitzer, etc.)\n"
        "- Specific ratings from major platforms (Goodreads average rating, Amazon rating, etc.)\n"
        "- Bestseller lists it appeared on (NYT, Amazon, etc.) and for how long\n"
        "- Notable quotes from professional critics and reviews\n"
        "- Overall critical consensus - what do critics generally say about it?\n"
        "- Summary of overall reception - was it well-received, controversial, etc.\n\n"
        
        "**CONTENT & READER INFORMATION:**\n"
        "- Approximate word AND page count (be specific, e.g., '350 pages', '90,000 words')\n"
        "- Emotional tone and mood (dark, uplifting, melancholy, humorous, suspenseful, etc.)\n"
        "- Content spiciness/heat level for romantic content (None, Mild, Moderate, Hot, Extra Hot)\n"
        "- Detailed content warnings (violence, sexual content, trauma, suicide, abuse, etc.)\n"
        "- Target audience and age range (YA, adult, middle grade, etc.)\n"
        "- Typical reader demographics who enjoy this book\n"
        "- Setting details: specific time period and geographical location\n\n"
        
        "**WRITING STYLE & NARRATIVE STRUCTURE:**\n"
        "- Detailed writing style description (prose style, literary techniques used)\n"
        "- Story pacing (slow burn, fast-paced, episodic, character-driven, plot-driven)\n"
        "- Reading difficulty level (easy, moderate, challenging, academic, literary)\n"
        "- Narrative point of view (first person, third person limited, omniscient, multiple POV)\n\n"
        
        "**GENRE & LITERARY CONTEXT:**\n"
        "- Specific genres this book belongs to (be precise - not just 'fantasy' but 'urban fantasy', 'epic fantasy', etc.)\n"
        "- List of similar works that readers of this book would enjoy\n"
        "- Books this is frequently compared to in reviews and recommendations\n\n"
        
        "**AUTHOR INFORMATION:**\n"
        "- Author's background, biography, and credentials\n"
        "- Other series written by this author\n"
        "- Other notable standalone works by this author\n"
        "- Author's reputation and standing in their genre\n\n"
        
        "**RESEARCH REQUIREMENTS:**\n"
        "Search multiple sources including Goodreads, Amazon, publisher websites, literary review sites, "
        "author websites, book blogs, and professional review publications. "
        "Cross-reference information to ensure accuracy. "
        "If any information is unavailable or unclear, clearly state that in your response. "
        "Provide specific, factual details rather than vague generalizations. "
        "Make sure you provide ALL of this information comprehensively - you cannot miss any category!"
        "You will be asked to reorganize this later, so don't forget to include everything!"
    )
    structure_model: str = "gemini-2.5-flash"
    structure_prompt: str = (
        "Based on the following research output, structure the information as JSON:\n"
        "{research_output}"
    )

    @classmethod
    def from_api_key(cls, api_key: str, **kwargs) -> BookResearchService:
        """Create BookAIService instance from API key"""
        client = genai.Client(api_key=api_key)
        return cls(client=client, **kwargs)
    
    async def research_book(self, title: str, other_info: str|None) -> BookResearchOutput:
        """Perform comprehensive research on a book and return structured info"""
        research_output, sources = await self._search_book_info(title=title, other_info=other_info)
        structured_info = await self._structure_book_info(research_output=research_output)
        return BookResearchOutput(
            info=structured_info,
            sources=sources,
        )
    
    async def _structure_book_info(self, research_output: str) -> BookResearchInfo:
        """Structure the research output into BookResearchInfo dataclass"""
        response = await self.client.aio.models.generate_content(
            model=self.structure_model,
            contents=self.structure_prompt.format(research_output=research_output),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=BookResearchInfo # <--- Pass your Pydantic class here!
            )
        )
        return response.parsed

    async def _search_book_info(self, title: str, other_info: str|None) -> tuple[str, list[ResearchSource]]:
        """Search for book information using Google GenAI"""
        response = await self.client.aio.models.generate_content(
            model=self.search_model,
            contents=self.search_prompt.format(title=title, other_info=other_info),
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )
        return response.text, self._get_unique_sources(response=response)
    
    @staticmethod
    def _get_unique_sources(response: types.GenerateContentResponse) -> list[ResearchSource]:
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
        return [ResearchSource(name=v, url=k) for k,v in sources.items()]