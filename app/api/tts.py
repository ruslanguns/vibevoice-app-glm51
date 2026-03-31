"""TTS (Text-to-Speech) API endpoints."""

import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.models.schemas import TTSRequest
from app.services.tts import tts_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tts", tags=["TTS"])


@router.post("/synthesize")
async def synthesize_speech(
    request: TTSRequest,
) -> FileResponse:
    """Synthesize text into speech audio using VibeVoice-Realtime-0.5B.

    Returns a WAV audio file (24kHz) synthesized from the provided text.
    Supports streaming-style generation with ~300ms first-audio latency.
    Max output: ~10 minutes of audio per request.
    """
    if not tts_service.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="TTS model not loaded. Please wait for model initialization.",
        )

    try:
        response, audio_path = tts_service.synthesize(
            text=request.text,
            speaker_name=request.speaker_name,
        )
        return FileResponse(
            path=str(audio_path),
            media_type="audio/wav",
            filename="synthesis.wav",
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
