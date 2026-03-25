from app.services.rag_pipeline import RAGPipeline

class RAGService:
    """Service to handle Retrieval-Augmented Generation logic."""
    
    def __init__(self):
        self.pipeline = RAGPipeline()

    def get_answer(self, question: str):
        """Processes the question through the RAG pipeline."""
        return self.pipeline.run(question)
