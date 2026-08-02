from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
import os

class Settings(BaseSettings):
    APP_NAME: str = "AI Resume Screening & Job Matching System"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # PostgreSQL Configuration
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "resume_matcher_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/resume_matcher_db"
    
    # ML Models
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    
    # Upload Storage
    UPLOAD_DIR: str = "./uploads"

    # CORS Origins
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
