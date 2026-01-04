from __future__ import annotations
import dataclasses
from importlib.metadata import metadata
import pydantic
from google import genai
from google.genai import types


from app.ai import BookResearchInfo

from .base_client_service import BaseClientService



class BookExtractionOutput(pydantic.BaseModel):
    books: list[ExtractedBookMetadata] = pydantic.Field(description="List of recommended books")

class ExtractedBookMetadata(pydantic.BaseModel):
    title: str = pydantic.Field(description="The title of the book")
    other_info: str = pydantic.Field(description="Other information about the recommended book including author, publication year, etc.")

@dataclasses.dataclass
class BookExtractionService(BaseClientService):
    text_input_model: str = "gemini-2.5-flash"
    text_input_prompt: str = (
        "Your job is to organize information provided from an unstructured list/descriptions of books "
        "into a structured JSON format for programatic parsing. Break the following book titles/information "
        "into discrete books/entries:\n\n"
        "book_list: {book_list_text}\n\n"
    )
    image_input_model: str = "gemini-2.5-flash"
    image_input_prompt: str = (
        "Analyze this image and extract all visible book information. Look for book titles, authors, "
        "publication years, and any other relevant metadata visible in the image. This could be from "
        "book covers, book spines, library catalogs, bookstore displays, reading lists, or any other "
        "source showing book information. Organize the extracted information into a structured JSON format."
    )
    
    async def extract_books(self, book_list_unstructured: str) -> BookExtractionOutput:
        """Generate book recommendations based on criteria and a list of books"""
        response = await self.client.models.generate_content_async(
            model=self.text_input_model,
            contents=self.text_input_prompt.format(book_list_text=book_list_unstructured),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=BookExtractionOutput # <--- Pass your Pydantic class here!
            )
        )
        return response.parsed
    
    async def extract_books_from_image(self, image_data: bytes, mime_type: str = "image/jpeg") -> BookExtractionOutput:
        """Extract book information from an image containing book titles, covers, or lists"""
        # Create the image part for multimodal input
        image_part = types.Part.from_bytes(data=image_data, mime_type=mime_type)
        
        response = await self.client.models.generate_content_async(
            model=self.image_input_model,
            contents=[
                self.image_input_prompt,
                image_part
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=BookExtractionOutput
            )
        )
        return response.parsed
    