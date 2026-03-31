"""ASR (Automatic Speech Recognition) API endpoints."""

import logging
import shutil
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.models.schemas import TranscriptionResponse
from app.services.asr import asr_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/asr", tags=["ASR"])

# Allowed audio extensions
ALLOWED_EXTENSIONS = {".wav", ".mp3", ".ogg", ".flac", ".m4a", ".webm"}


def _validate_audio_file(filename: str) -> str:
    """Validate the uploaded file has an allowed audio extension."""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported audio format: {ext}. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            ),
        )
    return ext


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(..., description="Audio file to transcribe"),
    prompt: Optional[str] = Form(
        default=None,
        description="Optional context/hotwords (e.g., names, technical terms)",
    ),
) -> TranscriptionResponse:
    """Transcribe an audio file with speaker diarization.

    Accepts audio files (wav, mp3, ogg, flac, m4a, webm) up to 60 minutes long.
    Returns structured transcription with speaker labels, timestamps, and content.

    Supports 50+ languages with automatic language detection and code-switching.
    Optionally provide a prompt with names/technical terms for better accuracy.
    """
    ext = _validate_audio_file(file.filename or "audio.wav")

    if not asr_service.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="ASR model not loaded. Please wait for model initialization.",
        )

    # Save uploaded file to temp location
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        try:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        except Exception as e:
            logger.error("Failed to save uploaded file: %s", e)
            raise HTTPException(status_code=500, detail="Failed to process uploaded file") from e

    try:
        result = asr_service.transcribe(tmp_path, prompt=prompt)
        logger.info(
            "Transcription complete: %d segments, %d speakers, %.1fs",
            len(result.segments),
            result.num_speakers,
            result.duration_seconds,
        )
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        Path(tmp_path).unlink(missing_ok=True)
