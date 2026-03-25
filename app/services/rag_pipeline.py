import logging
from typing import List
from app.services.vector_store_service import VectorStoreService
from app.services.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

class RAGPipeline:
    """
    Main RAG pipeline that coordinates retrieval and generation.
    """
    
    def __init__(self, vector_store: VectorStoreService, llm_provider: LLMProvider):
        self.vector_store = vector_store
        self.llm_provider = llm_provider

    def ask(self, question: str) -> str:
        """
        Executes the full RAG flow.
        
        Args:
            question (str): The user's query.
            
        Returns:
            str: The final generated answer from the LLM.
        """
        logger.info(f"RAG Pipeline started for question: {question}")

        # 1. Retrieve top 3 relevant text chunks
        relevant_chunks = self.vector_store.query(question, top_k=3)
        
        if not relevant_chunks:
            logger.warning("No relevant context found in vector store.")
            context = "No relevant institute documents found."
        else:
            # 2. Build context string
            context = "\n\n".join(relevant_chunks)
            logger.info(f"Retrieved {len(relevant_chunks)} context chunks.")

        # 3. Generate response using Groq
        structured_context_message = f"Use the following institute data to answer the enquiry:\n\n{context}"
        answer = self.llm_provider.generate_response(structured_context_message, question)
        
        return answer
