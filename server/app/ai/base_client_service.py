from __future__ import annotations
import typing
import dataclasses
from importlib.metadata import metadata
import pydantic
from google import genai

    

@dataclasses.dataclass
class BaseClientService:
    client: genai.Client

    @classmethod
    def from_api_key(cls, api_key: str, **kwargs) -> typing.Self:
        """Create service instance from API key"""
        client = genai.Client(api_key=api_key)
        return cls(client=client, **kwargs)

    @classmethod
    def from_service_account(cls, **kwargs) -> typing.Self:
        """Create service instance using Vertex AI with Application Default Credentials.
        Requires GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION env vars (or defaults)."""
        import os
        project = os.environ.get("GOOGLE_CLOUD_PROJECT", "personal-data-269621")
        location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        client = genai.Client(vertexai=True, project=project, location=location)
        return cls(client=client, **kwargs)
