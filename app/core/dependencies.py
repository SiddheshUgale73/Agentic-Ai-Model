from typing import Annotated
from fastapi import Depends
from app.services.embedding_service import EmbeddingService
from app.db.faiss_manager import FAISSManager
from app.services.file_processor import FileProcessor
from app.services.llm_provider import LLMProvider
from app.services.vector_store_service import VectorStoreService
from app.services.rag_pipeline import RAGPipeline

# Singletons (initialized on first demand or at startup)
_embedding_service = None
_faiss_manager = None
_file_processor = None
_llm_provider = None
_vector_store_service = None
_rag_pipeline = None

def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

def get_faiss_manager() -> FAISSManager:
    global _faiss_manager
    if _faiss_manager is None:
        _faiss_manager = FAISSManager(dimension=384)
    return _faiss_manager

def get_file_processor() -> FileProcessor:
    global _file_processor
    if _file_processor is None:
        _file_processor = FileProcessor()
    return _file_processor

def get_llm_provider() -> LLMProvider:
    global _llm_provider
    if _llm_provider is None:
        _llm_provider = LLMProvider()
    return _llm_provider

def get_vector_store_service(
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    faiss_manager: FAISSManager = Depends(get_faiss_manager)
) -> VectorStoreService:
    global _vector_store_service
    if _vector_store_service is None:
        _vector_store_service = VectorStoreService(embedding_service, faiss_manager)
    return _vector_store_service

def get_rag_pipeline(
    vector_store: VectorStoreService = Depends(get_vector_store_service),
    llm: LLMProvider = Depends(get_llm_provider)
) -> RAGPipeline:
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline(vector_store, llm)
    return _rag_pipeline
