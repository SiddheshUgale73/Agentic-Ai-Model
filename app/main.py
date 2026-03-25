import os
import logging
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Import simplified service
from app.models.schemas import QueryRequest, QueryResponse, UploadResponse
from app.services import rag_pipeline
from app.core.config import settings
from app.agent.agent_service import agent_service

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Institute AI Assistant", version="1.1.0")

# --- Middleware --- 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoints ---

@app.post("/upload", response_model=UploadResponse)
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Admin uploads a file for indexing."""
    os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOADS_DIR, file.filename)
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Background processing
    background_tasks.add_task(rag_pipeline.process_file, file_path)
    
    return UploadResponse(
        filename=file.filename,
        status="success",
        message="File received and indexing started."
    )

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """Students ask questions about the institute."""
    answer = rag_pipeline.ask(request.question)
    return QueryResponse(answer=answer)

@app.get("/health")
async def health():
    return {"status": "up"}

@app.post("/agent/chat", response_model=QueryResponse)
async def agent_chat(request: QueryRequest):
    """Interacts with the Institute Agent that uses tools and memory to answer."""
    answer = agent_service.run(request.question, session_id=request.session_id)
    return QueryResponse(answer=answer)

# --- Error Handling ---

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error: {str(exc)}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

# --- Static Files ---

os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
