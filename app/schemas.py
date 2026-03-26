from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = "default"

class QueryResponse(BaseModel):
    answer: str
    sources: List[str] = []

class UploadResponse(BaseModel):
    filename: str
    status: str
    message: str
