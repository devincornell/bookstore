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
        """Create BookAIService instance from API key"""
        client = genai.Client(api_key=api_key)
        return cls(client=client, **kwargs)
