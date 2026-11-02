"""
NeuralCanvas Configuration & Multimodal Runtime Settings.
"""

from typing import List, Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "NeuralCanvas"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    WS_V1_STR: str = "/ws/v1"
    DEBUG: bool = False

    # Database Settings (PostgreSQL with SQLite local dev fallback)
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgrespassword@localhost:5432/neural_canvas_db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    # Voice & Audio Ingestion Settings
    AUDIO_SAMPLE_RATE: int = 16000  # 16kHz standard for ASR / VAD
    AUDIO_CHANNELS: int = 1         # Mono audio
    AUDIO_FRAME_CHUNK_MS: int = 20  # 20ms frame chunking for streaming audio
    VAD_ENERGY_THRESHOLD: float = 0.015  # Voice Activity Detection energy cutoff
    MAX_AUDIO_BUFFER_SECONDS: int = 60   # Bounded audio capture window

    # Canvas & Action Execution Limits
    MAX_NODES_PER_SESSION: int = 200
    MAX_EDGES_PER_SESSION: int = 500
    DEFAULT_VIEWPORT: Dict[str, float] = {"x": 0.0, "y": 0.0, "zoom": 1.0}

    # Action Execution Timeout
    ACTION_TIMEOUT_MS: int = 5000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )


settings = Settings()
