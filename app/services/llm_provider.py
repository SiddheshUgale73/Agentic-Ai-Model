import logging
import os
from groq import Groq
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMProvider:
    """
    Service to interface with Groq API for generating responses 
    using the Llama 3 model.
    """

    def __init__(self):
        if not settings.GROQ_API_KEY:
            logger.error("GROQ_API_KEY not found in configuration.")
            raise ValueError("GROQ_API_KEY must be set in the environment.")
        
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama3-8b-8192"

    def generate_response(self, context: str, question: str) -> str:
        """
        Sends a context-aware prompt to Groq and returns the generated response.
        
        Args:
            context (str): The retrieved text chunks to use as context.
            question (str): The user's query.
            
        Returns:
            str: The LLM generated answer.
        """
        prompt = self._build_prompt(context, question)
        
        try:
            logger.info(f"Generating LLM response using model {self.model}...")
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for a training institute. Use the provided context to answer the student's question accurately. If the answer is not in the context, say you don't know based on the documents provided."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2, # Lower temperature for more factual responses
                max_tokens=1024,
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling Groq API: {str(e)}")
            return "I'm sorry, I encountered an error while processing your request."

    def _build_prompt(self, context: str, question: str) -> str:
        """Structures the prompt with context and question boundaries."""
        return f"""
Context Information:
---------------------
{context}
---------------------

Based on the context above, please answer the following question:
Question: {question}

Answer:
"""
