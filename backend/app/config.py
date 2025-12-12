"""Application configuration."""

import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # API Configuration
    API_TITLE: str = "COTECMAR - Reclutador IA"
    API_DESCRIPTION: str = "CV Analysis and Matching Platform for Recruitment"
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"

    # Server Configuration
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    RELOAD: bool = os.getenv("RELOAD", "True").lower() == "true"

    # CORS Configuration
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    CORS_HEADERS: list = ["*"]

    # File Upload Configuration
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    MAX_UPLOAD_FILES: int = int(os.getenv("MAX_UPLOAD_FILES", "10"))
    UPLOAD_TEMP_DIR: str = os.getenv("UPLOAD_TEMP_DIR", "/tmp/uploads")
    ALLOWED_FORMATS: list = [".pdf", ".docx", ".doc", ".txt"]

    # NLP & ML Models Configuration
    MODELS_PATH: str = os.getenv("MODELS_PATH", "./models")
    NLP_PARSER_MODEL: str = os.getenv("NLP_PARSER_MODEL", "beto")
    RANKING_MODEL_PATH: str = os.getenv("RANKING_MODEL_PATH", "./ranking_model")
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    )

    # Database Configuration (for future use)
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL", None)

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE", None)

    # Feature Flags
    ENABLE_NL_SEARCH: bool = os.getenv("ENABLE_NL_SEARCH", "True").lower() == "true"
    ENABLE_CV_ANALYSIS: bool = os.getenv("ENABLE_CV_ANALYSIS", "True").lower() == "true"


# Global settings instance
settings = Settings()
