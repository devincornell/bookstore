"""
Vertex AI configuration and client setup for the bookstore application.
"""

import os
from google.cloud import aiplatform
from google.auth import default
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class VertexAIConfig:
    """Configuration class for Vertex AI services"""
    
    def __init__(
        self, 
        project_id: Optional[str] = None,
        location: str = "us-central1",
        credentials_path: Optional[str] = None
    ):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location
        self.credentials_path = credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        if not self.project_id:
            raise ValueError("Google Cloud project ID must be provided via GOOGLE_CLOUD_PROJECT environment variable")
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Vertex AI client"""
        try:
            # Set up authentication if credentials path is provided
            if self.credentials_path and os.path.exists(self.credentials_path):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.credentials_path
            
            # Initialize Vertex AI
            aiplatform.init(
                project=self.project_id,
                location=self.location
            )
            
            logger.info(f"Vertex AI initialized successfully for project: {self.project_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {str(e)}")
            raise

# Global configuration instance
vertex_config: Optional[VertexAIConfig] = None

def get_vertex_config() -> VertexAIConfig:
    """Get the global Vertex AI configuration instance"""
    global vertex_config
    if vertex_config is None:
        vertex_config = VertexAIConfig()
    return vertex_config