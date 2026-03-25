# RAG-based AI Enquiry System Backend

This project provides a clean FastAPI-based backend for a training institute's enquiry system using RAG (Retrieval-Augmented Generation).

## Folder Structure

- `app/`: Core application logic.
    - `main.py`: Entry point of the FastAPI application.
    - `api/`: API route definitions.
        - `endpoints/`: Admin and Student dashboard logic.
    - `core/`: Configurations and security settings.
    - `services/`: Business logic (RAG, File Processing, Embeddings).
    - `models/`: Pydantic models for API data validation.
    - `db/`: Logic for managing FAISS vector indices.
- `data/`: Persistence layer.
    - `uploads/`: Original files (PDF, Word, etc.).
    - `vectors/`: Saved FAISS indices.

## Getting Started

1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Set up environment variables in `.env` (using `.env.example` as a template).
4. Run the server: `python -m app.main`.
