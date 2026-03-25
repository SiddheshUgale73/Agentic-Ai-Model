from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends
from app.models.schemas import UploadResponse
import os
import logging
from app.core.config import settings
from app.services.file_processor import FileProcessor
from app.services.vector_store_service import VectorStoreService
from app.core.dependencies import get_file_processor, get_vector_store_service

router = APIRouter()
logger = logging.getLogger(__name__)

def process_and_index(file_path: str, file_processor: FileProcessor, vector_store: VectorStoreService):
    """Background task to extract text and index it."""
    try:
        text = file_processor.extract_text(file_path)
        chunks = file_processor.chunk_text(text)
        vector_store.add_texts(chunks)
        logger.info(f"Successfully indexed file: {file_path}")
    except Exception as e:
        logger.error(f"Failed to index file {file_path}: {str(e)}")

@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...),
    file_processor: FileProcessor = Depends(get_file_processor),
    vector_store: VectorStoreService = Depends(get_vector_store_service)
):
    file_path = os.path.join(settings.UPLOADS_DIR, file.filename)
    
    # Ensure directory exists
    os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Process file in background
    background_tasks.add_task(process_and_index, file_path, file_processor, vector_store)
    
    return UploadResponse(
        filename=file.filename,
        status="success",
        message="File uploaded and indexing started in background."
    )
