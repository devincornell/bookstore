"""
Text generation functions using Vertex AI
"""
from google.cloud import aiplatform
from vertexai.preview.generative_models import GenerativeModel, Part
from typing import Optional, Dict, Any, List
import logging
from app.ai.client import vertex_client

logger = logging.getLogger(__name__)


class TextGenerator:
    """Text generation using Vertex AI Gemini models"""
    
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.model_name = model_name
        self._model = None
    
    def _get_model(self):
        """Get or initialize the generative model"""
        if not vertex_client.is_available:
            raise RuntimeError("Vertex AI not available")
        
        if self._model is None:
            try:
                self._model = GenerativeModel(self.model_name)
            except Exception as e:
                logger.error(f"Failed to initialize model {self.model_name}: {str(e)}")
                raise
        
        return self._model
    
    def generate_text(
        self, 
        prompt: str, 
        max_output_tokens: int = 1024,
        temperature: float = 0.7,
        top_p: float = 0.8,
        top_k: int = 40
    ) -> Optional[str]:
        """
        Generate text from a prompt
        
        Args:
            prompt: Input text prompt
            max_output_tokens: Maximum number of tokens to generate
            temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
            top_p: Controls diversity via nucleus sampling
            top_k: Controls diversity by limiting vocabulary
            
        Returns:
            Generated text or None if failed
        """
        try:
            model = self._get_model()
            
            generation_config = {
                "max_output_tokens": max_output_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k
            }
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Text generation failed: {str(e)}")
            return None
    
    def generate_book_description(
        self, 
        title: str, 
        author: str, 
        genre: Optional[str] = None,
        keywords: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Generate a book description based on title, author, and optional details
        
        Args:
            title: Book title
            author: Book author
            genre: Book genre (optional)
            keywords: List of keywords/themes (optional)
            
        Returns:
            Generated book description or None if failed
        """
        prompt_parts = [
            f"Write an engaging book description for:",
            f"Title: {title}",
            f"Author: {author}"
        ]
        
        if genre:
            prompt_parts.append(f"Genre: {genre}")
        
        if keywords:
            prompt_parts.append(f"Keywords/Themes: {', '.join(keywords)}")
        
        prompt_parts.extend([
            "",
            "Requirements:",
            "- Write 2-3 paragraphs",
            "- Make it engaging and compelling",
            "- Include what readers can expect",
            "- Use marketing-friendly language",
            "- Don't reveal major plot spoilers"
        ])
        
        prompt = "\n".join(prompt_parts)
        
        return self.generate_text(
            prompt=prompt,
            max_output_tokens=512,
            temperature=0.8
        )
    
    def suggest_similar_books(
        self, 
        title: str, 
        author: str, 
        genre: Optional[str] = None
    ) -> Optional[List[str]]:
        """
        Suggest similar books based on title, author, and genre
        
        Args:
            title: Book title
            author: Book author  
            genre: Book genre (optional)
            
        Returns:
            List of similar book suggestions or None if failed
        """
        prompt_parts = [
            f"Suggest 5 books similar to:",
            f"Title: {title}",
            f"Author: {author}"
        ]
        
        if genre:
            prompt_parts.append(f"Genre: {genre}")
        
        prompt_parts.extend([
            "",
            "Requirements:",
            "- List exactly 5 books",
            "- Format: 'Title by Author'",
            "- One book per line",
            "- No additional text or explanations",
            "- Choose well-known, published books"
        ])
        
        prompt = "\n".join(prompt_parts)
        
        response = self.generate_text(
            prompt=prompt,
            max_output_tokens=256,
            temperature=0.6
        )
        
        if response:
            # Parse the response into a list
            lines = [line.strip() for line in response.strip().split('\n') if line.strip()]
            return lines[:5]  # Ensure max 5 suggestions
        
        return None


# Global text generator instance
text_generator = TextGenerator()