from __future__ import annotations
import dataclasses
from importlib.metadata import metadata
import pydantic
from google import genai
from google.genai import types
from .base_client_service import BaseClientService


@dataclasses.dataclass
class EmbeddingService(BaseClientService):
    embedding_model: str = "embed-gecko-001"

    def generate_embedding(
        self,
        text: str,
    ) -> list[float]:
        """Generate embedding for the given text"""
        response = self.client.models.embed_content(
            model=self.embedding_model,
            contents=[text],
        )
        return response.embeddings[0].values
