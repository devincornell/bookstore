from __future__ import annotations
import dataclasses
from importlib.metadata import metadata
import pydantic
from google import genai
from google.genai import types
from .base_client_service import BaseClientService


@dataclasses.dataclass
class EmbeddingService(BaseClientService):
    embedding_model: str = "text-embedding-004"  # Latest model with improved performance

    async def generate_embedding(
        self,
        text: str,
    ) -> list[float]:
        """Generate embedding for the given text"""
        response = await self.client.aio.models.embed_content(
            model=self.embedding_model,
            contents=[text],
        )
        return response.embeddings[0].values
