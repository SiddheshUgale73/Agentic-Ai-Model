import faiss
import os
import numpy as np
import logging
from typing import List, Tuple
from app.core.config import settings

logger = logging.getLogger(__name__)

class FAISSManager:
    """Manages the FAISS index for vector storage and retrieval."""
    
    def __init__(self, dimension: int = 384): # Default for all-MiniLM-L6-v2 is 384
        self.index_path = os.path.join(settings.VECTORS_DIR, "faiss_index.index")
        self.dimension = dimension
        self.index = self.load_index()

    def create_index(self):
        """Creates a new L2 distance index."""
        logger.info(f"Creating new FAISS index with dimension {self.dimension}")
        self.index = faiss.IndexFlatL2(self.dimension)
    
    def add_vectors(self, embeddings: np.ndarray):
        """Adds a numpy array of vectors to the index."""
        if self.index is None:
            self.create_index()
        
        if embeddings.shape[1] != self.dimension:
            raise ValueError(f"Embedding dimension {embeddings.shape[1]} does not match index dimension {self.dimension}")
        
        self.index.add(embeddings.astype('float32'))
        logger.info(f"Added {len(embeddings)} vectors to the index.")
        self.save_index()

    def save_index(self):
        """Saves index to disk."""
        if self.index:
            if not os.path.exists(settings.VECTORS_DIR):
                os.makedirs(settings.VECTORS_DIR)
            faiss.write_index(self.index, self.index_path)
            logger.info(f"Index saved to {self.index_path}")

    def load_index(self):
        """Loads index from disk if it exists."""
        if os.path.exists(self.index_path):
            logger.info(f"Loading existing FAISS index from {self.index_path}")
            return faiss.read_index(self.index_path)
        logger.info("No existing index found.")
        return None

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        """Searches the index for the most similar vectors."""
        if self.index is None:
            logger.error("Attempted search with no index loaded.")
            return np.array([]), np.array([])
        
        distances, indices = self.index.search(query_embedding.astype('float32'), top_k)
        return distances, indices
