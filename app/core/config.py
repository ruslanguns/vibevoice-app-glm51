"""Application configuration using pydantic-settings."""

import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    """Application settings loaded from environment variables."""

    # Model configuration
    asr_model_id: str = field(
        default_factory=lambda: os.getenv("ASR_MODEL_ID", "microsoft/VibeVoice-ASR-HF")
    )
    tts_model_id: str = field(
        default_factory=lambda: os.getenv("TTS_MODEL_ID", "microsoft/VibeVoice-Realtime-0.5B")
    )

    # Server configuration
    host: str = field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "8000")))

    # Upload configuration
    upload_dir: str = field(default_factory=lambda: os.getenv("UPLOAD_DIR", "uploads"))
    max_upload_size_mb: int = field(
        default_factory=lambda: int(os.getenv("MAX_UPLOAD_SIZE_MB", "500"))
    )

    # Device configuration
    device: str = field(default_factory=lambda: os.getenv("DEVICE", "auto"))

    # Supported audio formats
    supported_formats: tuple = field(default=(".wav", ".mp3", ".ogg", ".flac", ".m4a", ".webm"))


settings = Settings()
