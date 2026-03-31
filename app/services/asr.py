"""VibeVoice ASR service — handles model loading and transcription."""

import logging
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.models.schemas import SpeakerSegment, TranscriptionResponse

logger = logging.getLogger(__name__)


class ASRService:
    """Service for VibeVoice-ASR speech-to-text transcription.

    Uses HuggingFace Transformers v5.3.0+ native integration with
    microsoft/VibeVoice-ASR-HF for speaker-diarized transcription
    supporting up to 60 minutes of audio in a single pass.
    """

    def __init__(self) -> None:
        self._processor = None
        self._model = None
        self._loaded = False

    def load_model(self) -> None:
        """Load the VibeVoice-ASR model and processor."""
        if self._loaded:
            logger.info("ASR model already loaded, skipping.")
            return

        logger.info("Loading VibeVoice-ASR model: %s", settings.asr_model_id)
        try:
            from transformers import AutoProcessor, VibeVoiceAsrForConditionalGeneration

            self._processor = AutoProcessor.from_pretrained(settings.asr_model_id)
            self._model = VibeVoiceAsrForConditionalGeneration.from_pretrained(
                settings.asr_model_id,
                device_map=settings.device if settings.device != "auto" else "auto",
            )
            self._loaded = True
            logger.info("ASR model loaded successfully on %s", self._model.device)
        except Exception as e:
            logger.error("Failed to load ASR model: %s", e)
            raise

    @property
    def is_loaded(self) -> bool:
        """Check if the model is loaded and ready."""
        return self._loaded

    def transcribe(
        self,
        audio_path: str | Path,
        prompt: Optional[str] = None,
    ) -> TranscriptionResponse:
        """Transcribe an audio file with speaker diarization.

        Args:
            audio_path: Path to the audio file.
            prompt: Optional context/hotwords for better recognition.

        Returns:
            TranscriptionResponse with segments, full text, and metadata.
        """
        if not self._loaded:
            raise RuntimeError("ASR model not loaded. Call load_model() first.")

        audio_path = Path(audio_path)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info("Transcribing: %s (prompt=%s)", audio_path, prompt)

        # Prepare inputs using the processor
        kwargs = {"audio": str(audio_path)}
        if prompt:
            kwargs["prompt"] = prompt

        inputs = self._processor.apply_transcription_request(**kwargs)
        inputs = inputs.to(self._model.device, self._model.dtype)

        # Generate transcription
        output_ids = self._model.generate(**inputs)
        generated_ids = output_ids[:, inputs["input_ids"].shape[1] :]

        # Parse into structured segments
        segments_raw = self._processor.decode(generated_ids, return_format="parsed")[0]
        full_text = self._processor.decode(generated_ids, return_format="transcription_only")[0]

        segments = []
        speakers_seen = set()
        total_duration = 0.0

        for seg in segments_raw:
            segment = SpeakerSegment(
                start=seg.get("Start", 0.0),
                end=seg.get("End", 0.0),
                speaker=seg.get("Speaker", 0),
                content=seg.get("Content", ""),
            )
            segments.append(segment)
            speakers_seen.add(segment.speaker)
            total_duration = max(total_duration, segment.end)

        return TranscriptionResponse(
            segments=segments,
            full_text=full_text,
            duration_seconds=total_duration,
            num_speakers=len(speakers_seen),
        )


# Singleton instance
asr_service = ASRService()
