"""
AI service utilities and helper functions.
"""

from typing import Dict, Any, List, Optional
from app.ai.text_generation import get_book_text_generator
from app.ai.embeddings import get_book_embeddings_service
from app.models.book import Book
import logging

logger = logging.getLogger(__name__)

class BookAIService:
    """High-level service that combines text generation and embeddings for book operations"""
    
    def __init__(self):
        self.text_generator = get_book_text_generator()
        self.embeddings_service = get_book_embeddings_service()
    
    async def enhance_book_data(self, book: Book) -> Dict[str, Any]:
        """
        Enhance book data with AI-generated content
        
        Args:
            book: The book model to enhance
            
        Returns:
            Dictionary with enhanced book data
        """
        try:
            enhanced_data = {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "original_description": book.description,
                "price": float(book.price),
                "genre": book.genre,
                "publication_year": book.publication_year
            }
            
            # Generate AI description if none exists or if existing one is short
            if not book.description or len(book.description) < 100:
                enhanced_data["ai_description"] = await self.text_generator.generate_book_description(
                    title=book.title,
                    author=book.author,
                    genre=book.genre
                )
            
            # Generate book categorization
            description_for_analysis = book.description or enhanced_data.get("ai_description", "")
            if description_for_analysis:
                enhanced_data["ai_categorization"] = await self.text_generator.categorize_book(
                    title=book.title,
                    description=description_for_analysis,
                    author=book.author
                )
            
            # Generate embedding
            enhanced_data["embedding"] = self.embeddings_service.generate_book_embedding(
                title=book.title,
                author=book.author,
                description=description_for_analysis,
                genre=book.genre
            )
            
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Error enhancing book data for book {book.id}: {str(e)}")
            raise
    
    async def get_personalized_recommendations(
        self,
        user_preferences: List[str],
        available_books: List[Book],
        max_recommendations: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get personalized book recommendations for a user
        
        Args:
            user_preferences: User's reading preferences
            available_books: List of available books
            max_recommendations: Maximum number of recommendations
            
        Returns:
            List of recommended books with AI reasoning
        """
        try:
            book_titles = [book.title for book in available_books]
            
            recommendations = await self.text_generator.generate_book_recommendations(
                user_preferences=user_preferences,
                book_titles=book_titles,
                max_recommendations=max_recommendations
            )
            
            # Enhance recommendations with book data
            enhanced_recommendations = []
            for rec in recommendations:
                # Find the corresponding book object
                matching_book = next(
                    (book for book in available_books if book.title == rec["title"]), 
                    None
                )
                
                if matching_book:
                    enhanced_rec = {
                        **rec,
                        "book_id": matching_book.id,
                        "author": matching_book.author,
                        "price": float(matching_book.price),
                        "genre": matching_book.genre,
                        "stock_quantity": matching_book.stock_quantity
                    }
                    enhanced_recommendations.append(enhanced_rec)
            
            return enhanced_recommendations
            
        except Exception as e:
            logger.error(f"Error getting personalized recommendations: {str(e)}")
            raise
    
    def find_similar_books_by_content(
        self,
        target_book: Book,
        candidate_books: List[Book],
        top_k: int = 5,
        threshold: float = 0.6
    ) -> List[Dict[str, Any]]:
        """
        Find books similar to a target book based on content embeddings
        
        Args:
            target_book: The book to find similarities for
            candidate_books: List of books to search through
            top_k: Number of similar books to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of similar books with similarity scores
        """
        try:
            # Generate embedding for target book
            target_embedding = self.embeddings_service.generate_book_embedding(
                title=target_book.title,
                author=target_book.author,
                description=target_book.description,
                genre=target_book.genre
            )
            
            # Generate embeddings for candidate books
            candidate_embeddings = []
            for book in candidate_books:
                if book.id != target_book.id:  # Don't include the target book itself
                    embedding = self.embeddings_service.generate_book_embedding(
                        title=book.title,
                        author=book.author,
                        description=book.description,
                        genre=book.genre
                    )
                    candidate_embeddings.append((book.id, embedding))
            
            # Find similar books
            similar_book_ids = self.embeddings_service.find_similar_books(
                query_embedding=target_embedding,
                book_embeddings=candidate_embeddings,
                top_k=top_k,
                threshold=threshold
            )
            
            # Build result with book data
            similar_books = []
            for book_id, similarity_score in similar_book_ids:
                matching_book = next(
                    (book for book in candidate_books if book.id == book_id),
                    None
                )
                
                if matching_book:
                    similar_books.append({
                        "book_id": matching_book.id,
                        "title": matching_book.title,
                        "author": matching_book.author,
                        "genre": matching_book.genre,
                        "price": float(matching_book.price),
                        "similarity_score": similarity_score
                    })
            
            return similar_books
            
        except Exception as e:
            logger.error(f"Error finding similar books: {str(e)}")
            raise

# Global instance
book_ai_service: Optional[BookAIService] = None

def get_book_ai_service() -> BookAIService:
    """Get the global book AI service instance"""
    global book_ai_service
    if book_ai_service is None:
        book_ai_service = BookAIService()
    return book_ai_service