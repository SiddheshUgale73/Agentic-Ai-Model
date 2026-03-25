from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GROQ_API_KEY: str
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    DATA_DIR: str = "data"
    UPLOADS_DIR: str = "data/uploads"
    VECTORS_DIR: str = "data/vectors"

    class Config:
        env_file = ".env"

settings = Settings()
