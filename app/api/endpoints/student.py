from fastapi import APIRouter, Depends
from app.models.schemas import QueryRequest, QueryResponse
from app.services.rag_pipeline import RAGPipeline
from app.core.dependencies import get_rag_pipeline

router = APIRouter()

@router.post("/ask", response_model=QueryResponse)
async def ask_question(
    request: QueryRequest,
    rag_pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    answer = rag_pipeline.run(request.question)
    return QueryResponse(
        answer=answer,
        sources=[] 
    )
