import os
import logging
from typing import List
from PyPDF2 import PdfReader
from docx import Document
import pandas as pd

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileProcessor:
    """
    Service to extract text from various file formats: PDF, Word, Excel, and TXT.
    Automatically detects file type based on extension.
    """

    def extract_text(self, file_path: str) -> str:
        """
        Extracts content from a file and returns it as a single string.
        
        Args:
            file_path (str): The absolute or relative path to the file.
            
        Returns:
            str: The extracted text content.
            
        Raises:
            ValueError: If the file extension is not supported.
            FileNotFoundError: If the file does not exist.
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        logger.info(f"Processing file: {file_path} (Type: {ext})")

        try:
            if ext == ".pdf":
                return self._process_pdf(file_path)
            elif ext == ".docx":
                return self._process_docx(file_path)
            elif ext in [".xls", ".xlsx"]:
                return self._process_excel(file_path)
            elif ext == ".txt":
                return self._process_txt(file_path)
            else:
                logger.warning(f"Unsupported file format: {ext}")
                raise ValueError(f"Unsupported file format: {ext}")
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            raise

    def _process_pdf(self, path: str) -> str:
        """Extracts text from PDF files using PyPDF2."""
        reader = PdfReader(path)
        text = []
        for page_num, page in enumerate(reader.pages):
            content = page.extract_text()
            if content:
                text.append(content)
            else:
                logger.warning(f"No text extracted from page {page_num} of {path}")
        return "\n".join(text)

    def _process_docx(self, path: str) -> str:
        """Extracts text from Word documents using python-docx."""
        doc = Document(path)
        return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

    def _process_excel(self, path: str) -> str:
        """Extracts text from Excel files using pandas. Converts all data to string format."""
        # Read all sheets by default
        excel_data = pd.read_excel(path, sheet_name=None)
        all_text = []
        for sheet_name, df in excel_data.items():
            all_text.append(f"Sheet: {sheet_name}")
            all_text.append(df.to_string(index=False))
        return "\n\n".join(all_text)

    def _process_txt(self, path: str) -> str:
        """Extracts text from plain text files."""
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def chunk_text(self, text: str, min_size: int = 400, max_size: int = 500) -> List[str]:
        """
        Splits text into chunks of 400-500 characters without breaking words.
        
        Args:
            text (str): The extracted text.
            min_size (int): Target minimum chunk size.
            max_size (int): Absolute maximum chunk size.
            
        Returns:
            List[str]: List of word-safe text chunks.
        """
        if not text:
            return []
            
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            # +1 for the space
            word_len = len(word) + 1
            
            if current_length + word_len > max_size:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = [word]
                    current_length = word_len
                else:
                    # Single word longer than max_size, force split it
                    chunks.append(word[:max_size])
                    current_chunk = [word[max_size:]]
                    current_length = len(current_chunk[0])
            else:
                current_chunk.append(word)
                current_length += word_len
                
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks
