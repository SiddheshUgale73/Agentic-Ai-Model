import logging
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service to generate embeddings using sentence-transformers."""
    
    def __init__(self):
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Converts a list of text strings into normalized numerical embeddings."""
        if not texts:
            return np.array([])
        
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        # Normalize for cosine similarity if using IndexFlatIP or L2
        return embeddings
