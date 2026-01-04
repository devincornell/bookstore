from __future__ import annotations
import dataclasses
from importlib.metadata import metadata
import pydantic
from google import genai
from google.genai import types


from app.ai import BookResearchInfo

from .base_client_service import BaseClientService



class BookRecommendOutput(pydantic.BaseModel):
    recommends: list[RecommendedBook] = pydantic.Field(description="List of recommended books")

class RecommendedBook(pydantic.BaseModel):
    title: str = pydantic.Field(description="The title of the recommended book")
    author: str = pydantic.Field(description="The author of the recommended book")
    year: int = pydantic.Field(description="The publication year of the recommended book")
    reason: str = pydantic.Field(description="Reason for the recommendation")



@dataclasses.dataclass
class BookRecommendService(BaseClientService):
    model: str = "gemini-2.5-flash"
    prompt: str = (
        "You have access to a ton of information about multiple books.\n"
        "I'd like you to take into account all information about each book and make a recommendation.\n"
        "The recommendation should take into account all information about the book, but they should "
        "have a special focus on these features:\n {recommend_criteria}\n"
        "# Books and Book Info to Choose From (in JSON format):\n {book_list}\n"
    )
    
    async def recommend_books(self, recommend_criteria: str, book_info: list[BookResearchInfo]) -> BookRecommendOutput:
        """Generate book recommendations based on criteria and a list of books"""
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=self.prompt.format(recommend_criteria=recommend_criteria, book_list=[book.as_string() for book in book_info]),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=BookRecommendOutput # <--- Pass your Pydantic class here!
            )
        )
        return response.parsed
    