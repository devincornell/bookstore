from __future__ import annotations
import dataclasses
from importlib.metadata import metadata
import pydantic
from google import genai
from google.genai import types

class BookResearchInfo(pydantic.BaseModel):
    company_name: str = pydantic.Field(description="The full name of the company")
    current_price: float = pydantic.Field(description="The current stock price")
    currency: str = pydantic.Field(description="The currency symbol, e.g., USD, INR")
    summary: str = pydantic.Field(description="A 1-sentence summary of recent news")

@dataclasses.dataclass
class BookResearchAIService:
    client: genai.Client
    search_model: str = "gemini-2.5-flash"
    search_prompt: str = (
        'I need you to do research on a book titled \"{title}\" by \"{author}\". '
        " For this book, search the web thoroughly and find the following information:"
        "   + General genre or style"
        "   + Aparent audience including age range type or ammont of explicit content"
        "   + Other books and articles that may be similar"
        "   + Content described frequently in reviews and write-ups for critics and regular users."
        "   + Author fame and background"
        "   + Reception: any awards that the book has won; average or median user star ratings on websites like kindle, Goodreads, or Barnes and noble; and any best selling lists that the book has appeared on."
        " Make sure you provide ALL of this information - you can't miss a single point!"
    )
    structure_model: str = "gemini-2.5-flash"
    structure_prompt: str = (
        "Based on the following research output, structure the information as JSON:\n"
        "{research_output}"
    )

    @classmethod
    def from_api_key(cls, api_key: str) -> BookResearchInfo:
        """Create BookAIService instance from API key"""
        client = genai.Client(api_key=api_key)
        return cls(client=client)
    
    def structure_book_info(self, research_output: str) -> BookResearchInfo:
        """Structure the research output into BookResearchInfo dataclass"""
        structure_response = self.client.models.generate_content(
            model=self.structure_model,
            contents=self.structure_prompt.format(research_output=research_output),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=BookResearchInfo # <--- Pass your Pydantic class here!
            )
        )

    def search_book_info(self, title: str, author: str|None) -> tuple[str, list[tuple[str, str]]]:
        """Search for book information using Google GenAI"""
        response = self.client.models.generate_content(
            model=self.search_model,
            contents=self.search_prompt.format(title=title, author=author or "Unknown Author"),
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )
        return response.parsed
    
    def _get_unique_sources(self, response: types.GenerateContentResponse) -> list[tuple[str, str]]:
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