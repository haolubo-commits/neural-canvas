"""
FastAPI application entrypoint for NeuralCanvas.
Multimodal Voice & Real-Time Action Cockpit.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.models import (
    CanvasSession,
    CanvasNode,
    CanvasEdge,
    MultimodalMessage,
    ActionExecution,
)
from app.api.v1.api import api_router
from app.api.v1.endpoints.websocket import router as ws_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("neural_canvas")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages application startup and database schema initialization."""
    logger.info("Initializing NeuralCanvas database schemas...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified and initialized successfully.")
    except Exception as e:
        logger.warning(f"Database initialization caveat: {e}")
    yield
    logger.info("Shutting down NeuralCanvas service...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Multimodal Voice & Real-Time Action Cockpit API Gateway",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Configure CORS
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Mount REST API v1 router and WebSocket gateway router
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(ws_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Confirms service health and verifies database connectivity."""
    db_status = "connected"
    try:
        with engine.connect() as conn:
            conn.execute(Base.metadata.tables["canvas_sessions"].select().limit(1))
    except Exception as e:
        db_status = f"unhealthy ({str(e)[:60]})"

    return {
        "status": "healthy" if "unhealthy" not in db_status else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database_status": db_status,
        "audio_sample_rate_hz": settings.AUDIO_SAMPLE_RATE,
        "vad_energy_threshold": settings.VAD_ENERGY_THRESHOLD,
    }


@app.get("/", tags=["Root"])
async def root():
    """API Gateway root index."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API Gateway",
        "docs": "/docs",
        "health": "/health",
        "api_v1": settings.API_V1_STR,
        "ws_v1": settings.WS_V1_STR,
    }

