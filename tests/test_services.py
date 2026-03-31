"""Tests for ASR service logic (without GPU/model)."""

import pytest

from app.services.asr import ASRService
from app.services.tts import TTSService


class TestASRService:
    """Tests for ASRService class."""

    def test_initial_state(self):
        """Service should start unloaded."""
        svc = ASRService()
        assert not svc.is_loaded

    def test_transcribe_without_load_raises(self):
        """Transcribing before loading should raise RuntimeError."""
        svc = ASRService()
        with pytest.raises(RuntimeError, match="not loaded"):
            svc.transcribe("/tmp/nonexistent.wav")

    def test_transcribe_missing_file_raises(self):
        """Transcribing a nonexistent file should raise FileNotFoundError."""
        svc = ASRService()
        # Manually set loaded to test the file check
        svc._loaded = True
        with pytest.raises(FileNotFoundError, match="not found"):
            svc.transcribe("/tmp/this_file_does_not_exist_12345.wav")


class TestTTSService:
    """Tests for TTSService class."""

    def test_initial_state(self):
        """Service should start unloaded."""
        svc = TTSService()
        assert not svc.is_loaded

    def test_synthesize_without_load_raises(self):
        """Synthesizing before loading should raise RuntimeError."""
        svc = TTSService()
        with pytest.raises(RuntimeError, match="not loaded"):
            svc.synthesize("Hello world")
