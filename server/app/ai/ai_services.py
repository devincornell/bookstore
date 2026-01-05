


# ai services
from .research_service import BookResearchService
from .embedding_service import EmbeddingService
from .recommend_service import BookRecommendService
from .extraction_service import BookExtractionService


from .base_client_service import BaseClientService

class AIServices(BaseClientService):
    @property
    def research(self) -> BookResearchService:
        return BookResearchService(self.client)
    
    @property
    def recommend(self) -> BookRecommendService:
        return BookRecommendService(self.client)
    
    @property
    def extraction(self) -> BookExtractionService:
        return BookExtractionService(self.client)
    
    @property
    def embedding(self) -> EmbeddingService:
        return EmbeddingService(self.client)

