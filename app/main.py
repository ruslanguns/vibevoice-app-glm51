"""VibeVoice Studio — FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.asr import router as asr_router
from app.api.tts import router as tts_router
from app.core.config import settings
from app.models.schemas import HealthResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown events."""
    logger.info("VibeVoice Studio starting up...")
    logger.info("ASR model: %s", settings.asr_model_id)
    logger.info("TTS model: %s", settings.tts_model_id)
    logger.info("Upload dir: %s", settings.upload_dir)

    # In production, models would be loaded here:
    # from app.services.asr import asr_service
    # from app.services.tts import tts_service
    # asr_service.load_model()
    # tts_service.load_model()

    yield

    logger.info("VibeVoice Studio shutting down.")


app = FastAPI(
    title="VibeVoice Studio",
    description=(
        "Voice transcription and synthesis API powered by Microsoft VibeVoice models. "
        "Supports long-form ASR (up to 60 min) with speaker diarization, "
        "and real-time TTS with ~300ms latency."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# Register routers
app.include_router(asr_router)
app.include_router(tts_router)


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        version="0.1.0",
        asr_model=settings.asr_model_id,
        tts_model=settings.tts_model_id,
    )


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "VibeVoice Studio",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "asr": "/asr/transcribe",
            "tts": "/tts/synthesize",
        },
    }
