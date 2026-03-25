import logging
import json
import os
from typing import List, Tuple
import numpy as np
from app.services.embedding_service import EmbeddingService
from app.db.faiss_manager import FAISSManager
from app.core.config import settings

logger = logging.getLogger(__name__)

class VectorStoreService:
    """
    High-level service that integrates EmbeddingService and FAISSManager.
    Handles converting text chunks to embeddings and managing the vector index
    along with their corresponding text metadata.
    """
    
    def __init__(self, embedding_service: EmbeddingService, faiss_manager: FAISSManager):
        self.embedding_service = embedding_service
        self.faiss_manager = faiss_manager
        self.chunks_path = os.path.join(settings.VECTORS_DIR, "chunks.json")
        self.text_chunks = self._load_chunks()

    def _load_chunks(self) -> List[str]:
        if os.path.exists(self.chunks_path):
            with open(self.chunks_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save_chunks(self):
        with open(self.chunks_path, "w", encoding="utf-8") as f:
            json.dump(self.text_chunks, f, ensure_ascii=False, indent=2)

    def add_texts(self, texts: List[str]):
        """Converts text segments to embeddings and saves them along with the text chunks."""
        if not texts:
            logger.warning("No texts provided to add_texts.")
            return

        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.embedding_service.generate_embeddings(texts)
        
        logger.info("Adding embeddings to FAISS index...")
        self.faiss_manager.add_vectors(embeddings)
        
        self.text_chunks.extend(texts)
        self._save_chunks()
        logger.info("Successfully updated vector store with text metadata.")

    def query(self, question: str, top_k: int = 3) -> List[str]:
        """
        Converts a question to an embedding, searches the FAISS index,
        and returns the actual text chunks.
        """
        logger.info(f"Querying vector store for: {question}")
        query_embedding = self.embedding_service.generate_embeddings([question])
        
        distances, indices = self.faiss_manager.search(query_embedding, top_k)
        
        relevant_chunks = []
        for idx in indices[0]:
            if idx != -1 and idx < len(self.text_chunks):
                relevant_chunks.append(self.text_chunks[idx])
        
        return relevant_chunks
