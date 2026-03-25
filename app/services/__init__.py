from app.services.embedding_service import EmbeddingService
from app.db.faiss_manager import FAISSManager
from app.services.vector_store_service import VectorStoreService
from app.services.llm_provider import LLMProvider
from app.services.rag_pipeline import RAGPipeline

# Initialize core components
embedding_service = EmbeddingService()
faiss_manager = FAISSManager()
vector_store = VectorStoreService(embedding_service, faiss_manager)
llm_provider = LLMProvider()

# Instantiate the main pipeline
rag_pipeline = RAGPipeline(vector_store, llm_provider)

# Export for use in main.py and other modules
__all__ = ["rag_pipeline", "embedding_service", "vector_store", "llm_provider"]
