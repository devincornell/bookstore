"""
Embedding functions using Vertex AI for semantic search and recommendations
"""
from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel
from typing import List, Optional, Dict, Any
import numpy as np
import logging
from app.ai.client import vertex_client

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings using Vertex AI text embedding models"""
    
    def __init__(self, model_name: str = "textembedding-gecko@003"):
        self.model_name = model_name
        self._model = None
    
    def _get_model(self):
        """Get or initialize the embedding model"""
        if not vertex_client.is_available:
            raise RuntimeError("Vertex AI not available")
        
        if self._model is None:
            try:
                self._model = TextEmbeddingModel.from_pretrained(self.model_name)
            except Exception as e:
                logger.error(f"Failed to initialize embedding model {self.model_name}: {str(e)}")
                raise
        
        return self._model
    
    def generate_embeddings(self, texts: List[str]) -> Optional[List[List[float]]]:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors or None if failed
        """
        try:
            model = self._get_model()
            
            # Generate embeddings
            embeddings = model.get_embeddings(texts)
            
            # Extract the embedding values
            embedding_vectors = [embedding.values for embedding in embeddings]
            
            return embedding_vectors
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            return None
    
    def generate_single_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text string to embed
            
        Returns:
            Embedding vector or None if failed
        """
        embeddings = self.generate_embeddings([text])
        return embeddings[0] if embeddings else None
    
    def create_book_embedding_text(
        self,
        title: str,
        author: str,
        description: Optional[str] = None,
        genre: Optional[str] = None
    ) -> str:
        """
        Create a combined text representation of a book for embedding
        
        Args:
            title: Book title
            author: Book author
            description: Book description (optional)
            genre: Book genre (optional)
            
        Returns:
            Combined text representation
        """
        parts = [f"Title: {title}", f"Author: {author}"]
        
        if genre:
            parts.append(f"Genre: {genre}")
        
        if description:
            parts.append(f"Description: {description}")
        
        return " | ".join(parts)
    
    def calculate_cosine_similarity(
        self, 
        embedding1: List[float], 
        embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1, higher = more similar)
        """
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return max(0.0, min(1.0, similarity))  # Clamp to [0, 1]
            
        except Exception as e:
            logger.error(f"Similarity calculation failed: {str(e)}")
            return 0.0
    
    def find_similar_books_by_embedding(
        self,
        query_embedding: List[float],
        book_embeddings: List[Dict[str, Any]],
        top_k: int = 5,
        min_similarity: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Find similar books based on embedding similarity
        
        Args:
            query_embedding: Embedding of the query book/text
            book_embeddings: List of dicts with book info and embeddings
                           Format: [{"id": int, "title": str, "embedding": List[float]}, ...]
            top_k: Number of similar books to return
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of similar books sorted by similarity (highest first)
        """
        try:
            similarities = []
            
            for book in book_embeddings:
                similarity = self.calculate_cosine_similarity(
                    query_embedding, 
                    book["embedding"]
                )
                
                if similarity >= min_similarity:
                    book_with_similarity = book.copy()
                    book_with_similarity["similarity"] = similarity
                    similarities.append(book_with_similarity)
            
            # Sort by similarity (highest first) and return top_k
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Similar books search failed: {str(e)}")
            return []
    
    def generate_book_embedding_from_model(self, book) -> Optional[List[float]]:
        """
        Generate embedding for a book using its get_embedding_text() method.
        This excludes the author field as requested.
        
        Args:
            book: Book model instance with get_embedding_text() method
            
        Returns:
            Embedding vector as list of floats, or None if failed
        """
        try:
            # Use the book's own method to get embedding text (excludes author)
            embedding_text = book.get_embedding_text()
            
            if not embedding_text.strip():
                logger.warning(f"Empty embedding text for book {getattr(book, 'id', 'unknown')}")
                return None
            
            # Generate embedding for the text
            embeddings = self.generate_embeddings([embedding_text])
            
            if embeddings and len(embeddings) > 0:
                return embeddings[0]
            else:
                logger.warning(f"Failed to generate embedding for book {getattr(book, 'id', 'unknown')}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating book embedding: {str(e)}")
            return None


# Global embedding generator instance
embedding_generator = EmbeddingGenerator()