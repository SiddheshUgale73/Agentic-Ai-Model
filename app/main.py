import os
import logging
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Import simplified service
from app.schemas import QueryRequest, QueryResponse, UploadResponse
from app.services import rag_pipeline, settings
from app.agent import agent_service

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

import csv

@app.get("/api/courses")
async def get_courses():
    """Returns the list of courses from the CSV database."""
    courses = []
    if os.path.exists("data/courses.csv"):
        with open("data/courses.csv", mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                courses.append(row)
    return courses

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

import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error: {str(exc)}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": str(exc), "traceback": traceback.format_exc()})

# --- Static Files ---

os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
