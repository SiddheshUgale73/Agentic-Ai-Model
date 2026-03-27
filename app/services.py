import os
import json
import logging
import numpy as np
import faiss
from typing import List, Tuple, Optional
from PyPDF2 import PdfReader
from docx import Document
import pandas as pd
from sentence_transformers import SentenceTransformer
from groq import Groq
from pydantic_settings import BaseSettings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration & Models ---

class Settings(BaseSettings):
    GROQ_API_KEY: str
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    DATA_DIR: str = "data"
    UPLOADS_DIR: str = "data/uploads"
    VECTORS_DIR: str = "data/vectors"
    SENDER_EMAIL: Optional[str] = None
    SENDER_PASSWORD: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()

# --- Services ---

class FileProcessor:
    """Extracts text from PDF, Word, Excel, and TXT files."""
    
    def extract_text(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == ".pdf":
                reader = PdfReader(file_path)
                return "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
            elif ext == ".docx":
                doc = Document(file_path)
                return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            elif ext in [".xls", ".xlsx"]:
                excel_data = pd.read_excel(file_path, sheet_name=None)
                return "\n\n".join([f"Sheet: {s}\n{df.to_string(index=False)}" for s, df in excel_data.items()])
            elif ext == ".txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                raise ValueError(f"Unsupported format: {ext}")
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            raise

    def chunk_text(self, text: str, max_words: int = 150, overlap: int = 30) -> List[str]:
        """Chunks text with a sliding window to maintain context overlap."""
        if not text: return []
        words = text.split()
        if len(words) <= max_words:
            return [" ".join(words)]
        
        chunks = []
        for i in range(0, len(words), max_words - overlap):
            chunk = words[i : i + max_words]
            chunks.append(" ".join(chunk))
            if i + max_words >= len(words):
                break
        return chunks

class VectorStore:
    """Manages Embeddings and FAISS index."""
    
    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        self.index_path = os.path.join(settings.VECTORS_DIR, "faiss.index")
        self.chunks_path = os.path.join(settings.VECTORS_DIR, "chunks.json")
        self.dimension = 384
        self.index = self._load_index()
        self.text_chunks = self._load_chunks()

    def _load_index(self):
        if os.path.exists(self.index_path):
            return faiss.read_index(self.index_path)
        return faiss.IndexFlatL2(self.dimension)

    def _load_chunks(self):
        if os.path.exists(self.chunks_path):
            with open(self.chunks_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def add_texts(self, texts: List[str]):
        embeddings = self.model.encode(texts, convert_to_numpy=True).astype('float32')
        self.index.add(embeddings)
        self.text_chunks.extend(texts)
        # Save
        os.makedirs(settings.VECTORS_DIR, exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.chunks_path, "w", encoding="utf-8") as f:
            json.dump(self.text_chunks, f, ensure_ascii=False)

    def query(self, question: str, top_k: int = 5) -> List[str]:
        query_emb = self.model.encode([question], convert_to_numpy=True).astype('float32')
        _, indices = self.index.search(query_emb, top_k)
        return [self.text_chunks[idx] for idx in indices[0] if idx != -1 and idx < len(self.text_chunks)]

class LLMProvider:
    """Interfaces with Groq."""
    
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.1-8b-instant"

    def generate(self, context: str, question: str) -> str:
        prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer concisely based on the context above."
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq Error: {str(e)}")
            return "I'm sorry, I'm having trouble connecting to my brain right now."

class RAGPipeline:
    """Coordinates the full pipeline."""
    
    def __init__(self):
        self.file_processor = FileProcessor()
        self.vector_store = VectorStore()
        self.llm = LLMProvider()

    def process_file(self, file_path: str):
        text = self.file_processor.extract_text(file_path)
        chunks = self.file_processor.chunk_text(text)
        self.vector_store.add_texts(chunks)

    def ask(self, question: str) -> str:
        context_chunks = self.vector_store.query(question)
        context = "\n\n".join(context_chunks) if context_chunks else "No relevant data found."
        return self.llm.generate(context, question)

# Singleton
rag_pipeline = RAGPipeline()
