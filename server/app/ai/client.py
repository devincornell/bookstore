"""
Vertex AI client configuration and initialization
"""
from google.cloud import aiplatform
from google.auth.exceptions import DefaultCredentialsError
from typing import Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class VertexAIClient:
    """Singleton client for Vertex AI operations"""
    
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
            VertexAIClient._initialized = True
    
    def _initialize_client(self):
        """Initialize Vertex AI client"""
        try:
            if not self.project_id:
                logger.warning("GOOGLE_CLOUD_PROJECT not configured. Vertex AI features will be disabled.")
                return
            
            # Initialize Vertex AI
            aiplatform.init(
                project=self.project_id,
                location=self.region,
                credentials=None  # Uses default credentials or GOOGLE_APPLICATION_CREDENTIALS
            )
            
            logger.info(f"Vertex AI initialized successfully for project: {self.project_id}")
            self._client = aiplatform
            
        except DefaultCredentialsError:
            logger.error(
                "Google Cloud credentials not found. Please set up authentication:\n"
                "1. Set GOOGLE_APPLICATION_CREDENTIALS environment variable\n"
                "2. Or run 'gcloud auth application-default login'"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {str(e)}")
    
    @property
    def is_available(self) -> bool:
        """Check if Vertex AI is properly configured and available"""
        return self._client is not None and self.project_id is not None
    
    def get_client(self):
        """Get the Vertex AI client"""
        if not self.is_available:
            raise RuntimeError(
                "Vertex AI not available. Please check your configuration:\n"
                "1. Set GOOGLE_CLOUD_PROJECT environment variable\n"
                "2. Set up authentication (GOOGLE_APPLICATION_CREDENTIALS or gcloud auth)\n"
                "3. Ensure google-cloud-aiplatform is installed"
            )
        return self._client


# Global client instance
vertex_client = VertexAIClient()