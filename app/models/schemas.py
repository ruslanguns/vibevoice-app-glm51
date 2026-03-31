"""Pydantic models for request/response schemas."""

from typing import Optional

from pydantic import BaseModel, Field


class TranscriptionRequest(BaseModel):
    """Request model for transcription endpoint."""

    prompt: Optional[str] = Field(
        default=None,
        description="Optional context/hotwords to guide ASR (e.g., names, technical terms)",
        examples=["About VibeVoice"],
    )


class SpeakerSegment(BaseModel):
    """A single speaker segment from transcription."""

    start: float = Field(description="Start time in seconds")
    end: float = Field(description="End time in seconds")
    speaker: int = Field(description="Speaker identifier (0-indexed)")
    content: str = Field(description="Transcribed text content")


class TranscriptionResponse(BaseModel):
    """Response model for transcription endpoint."""

    segments: list[SpeakerSegment] = Field(description="List of speaker-attributed segments")
    full_text: str = Field(description="Complete transcription text without speaker labels")
    duration_seconds: float = Field(description="Total audio duration")
    num_speakers: int = Field(description="Number of distinct speakers detected")


class TTSRequest(BaseModel):
    """Request model for text-to-speech endpoint."""

    text: str = Field(
        description="Text to synthesize into speech",
        min_length=1,
        max_length=10000,
    )
    speaker_name: Optional[str] = Field(
        default=None,
        description="Optional speaker name (e.g., 'Carter'). If None, uses default.",
    )


class TTSResponse(BaseModel):
    """Response model for TTS endpoint (metadata — audio returned as file)."""

    message: str = Field(description="Status message")
    text_length: int = Field(description="Length of input text")
    speaker: str = Field(description="Speaker used for synthesis")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    version: str = "0.1.0"
    asr_model: str = ""
    tts_model: str = ""
