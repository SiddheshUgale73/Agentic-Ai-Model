# RAG-based AI Enquiry System Backend

This project provides a clean FastAPI-based backend for a training institute's enquiry system using RAG (Retrieval-Augmented Generation).

## Folder Structure

- `app/`: Core application logic.
    - `main.py`: Entry point of the FastAPI application.
    - `agent.py`: Agentic AI Counselor logic (ReAct loop, Conversation Memory, Tool bindings).
    - `services.py`: Backend services containing RAG, LLM inference, embedding, and environment settings.
    - `schemas.py`: Pydantic models for API data validation.
- `data/`: Persistence layer.
    - `uploads/`: Original files (PDF, Word, etc.).
    - `vectors/`: Saved FAISS indices.

## Getting Started

1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Set up environment variables in `.env` (using `.env.example` as a template).
4. Run the server: `python -m app.main`.
