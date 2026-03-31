"""Import tests — verify all modules can be imported without errors."""

import importlib

import pytest


@pytest.mark.parametrize(
    "module_path",
    [
        "app",
        "app.core",
        "app.core.config",
        "app.models",
        "app.models.schemas",
        "app.api",
        "app.api.asr",
        "app.api.tts",
        "app.services",
        "app.services.asr",
        "app.services.tts",
        "app.main",
    ],
)
def test_module_imports(module_path: str):
    """Verify that every module can be imported without errors."""
    mod = importlib.import_module(module_path)
    assert mod is not None, f"Failed to import {module_path}"


def test_app_version():
    """Verify the app version is set."""
    from app import __version__

    assert __version__ == "0.1.0"


def test_settings_defaults():
    """Verify settings have sensible defaults."""
    from app.core.config import settings

    assert settings.asr_model_id == "microsoft/VibeVoice-ASR-HF"
    assert settings.tts_model_id == "microsoft/VibeVoice-Realtime-0.5B"
    assert settings.host == "0.0.0.0"
    assert settings.port == 8000
    assert ".wav" in settings.supported_formats
    assert ".mp3" in settings.supported_formats


def test_schemas_structure():
    """Verify Pydantic schemas are properly defined."""
    from app.models.schemas import (
        HealthResponse,
        SpeakerSegment,
        TranscriptionRequest,
        TranscriptionResponse,
        TTSRequest,
        TTSResponse,
    )

    # Test SpeakerSegment
    seg = SpeakerSegment(start=0.0, end=5.0, speaker=0, content="Hello world")
    assert seg.start == 0.0
    assert seg.content == "Hello world"

    # Test TranscriptionRequest
    req = TranscriptionRequest()
    assert req.prompt is None
    req_with_prompt = TranscriptionRequest(prompt="About VibeVoice")
    assert req_with_prompt.prompt == "About VibeVoice"

    # Test TranscriptionResponse
    resp = TranscriptionResponse(
        segments=[seg],
        full_text="Hello world",
        duration_seconds=5.0,
        num_speakers=1,
    )
    assert resp.num_speakers == 1
    assert len(resp.segments) == 1

    # Test TTSRequest
    tts_req = TTSRequest(text="Hello world")
    assert tts_req.text == "Hello world"
    assert tts_req.speaker_name is None

    # Test TTSResponse
    tts_resp = TTSResponse(message="ok", text_length=11, speaker="default")
    assert tts_resp.text_length == 11

    # Test HealthResponse
    health = HealthResponse()
    assert health.status == "ok"
    assert health.version == "0.1.0"
