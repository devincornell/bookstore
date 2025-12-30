"""
Google GenAI client configuration and initialization
"""
from google import genai
from google.genai import types
from google.auth.exceptions import DefaultCredentialsError
from typing import Optional
import logging
import os
from app.core.config import settings

logger = logging.getLogger(__name__)


class GenAIClient:
    """Singleton client for Google GenAI operations"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.project_id = settings.GOOGLE_CLOUD_PROJECT
            self.region = settings.GOOGLE_CLOUD_REGION
            self._client = None
            self._initialize_client()
            GenAIClient._initialized = True
    
    def _initialize_client(self):
        """Initialize GenAI client"""
        try:
            # Check for API key first
            api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
            
            if api_key:
                # Use Gemini Developer API
                self._client = genai.Client(api_key=api_key)
                logger.info("GenAI initialized with API key (Gemini Developer API)")
            elif self.project_id:
                # Use Vertex AI
                self._client = genai.Client(
                    vertexai=True, 
                    project=self.project_id, 
                    location=self.region
                )
                logger.info(f"GenAI initialized with Vertex AI for project: {self.project_id}")
            else:
                logger.warning("No API key or project configured. GenAI features will be disabled.")
                return
                
        except DefaultCredentialsError:
            logger.error(
                "Google Cloud credentials not found. Please set up authentication:\n"
                "1. Set GEMINI_API_KEY environment variable, OR\n"
                "2. Set GOOGLE_CLOUD_PROJECT and authenticate with:\n"
                "   - Set GOOGLE_APPLICATION_CREDENTIALS environment variable\n"
                "   - Or run 'gcloud auth application-default login'"
            )
        except Exception as e:
            logger.error(f"Failed to initialize GenAI: {str(e)}")
    
    @property
    def is_available(self) -> bool:
        """Check if GenAI is properly configured and available"""
        return self._client is not None
    
    def get_client(self):
        """Get the GenAI client"""
        if not self.is_available:
            raise RuntimeError(
                "GenAI not available. Please check your configuration:\n"
                "1. Set GEMINI_API_KEY environment variable, OR\n"
                "2. Set GOOGLE_CLOUD_PROJECT and authenticate with gcloud\n"
                "3. Ensure google-genai is installed"
            )
        return self._client


# Global client instance
genai_client = GenAIClient()