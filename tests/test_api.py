"""Tests for FastAPI endpoints using httpx AsyncClient."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    """Async HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test the root endpoint returns API info."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "VibeVoice Studio"
    assert data["version"] == "0.1.0"
    assert "endpoints" in data


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test the health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"
    assert "asr_model" in data
    assert "tts_model" in data


@pytest.mark.asyncio
async def test_asr_transcribe_no_model(client: AsyncClient):
    """Test ASR endpoint returns 503 when model not loaded."""
    response = await client.post(
        "/asr/transcribe",
        files={"file": ("test.wav", b"fake audio data", "audio/wav")},
    )
    assert response.status_code == 503


@pytest.mark.asyncio
async def test_asr_transcribe_invalid_format(client: AsyncClient):
    """Test ASR endpoint rejects unsupported formats."""
    response = await client.post(
        "/asr/transcribe",
        files={"file": ("test.txt", b"not audio", "text/plain")},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_tts_synthesize_no_model(client: AsyncClient):
    """Test TTS endpoint returns 503 when model not loaded."""
    response = await client.post(
        "/tts/synthesize",
        json={"text": "Hello world"},
    )
    assert response.status_code == 503


@pytest.mark.asyncio
async def test_openapi_docs_available(client: AsyncClient):
    """Test that OpenAPI docs are accessible."""
    response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_openapi_json_available(client: AsyncClient):
    """Test that OpenAPI JSON schema is accessible."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "VibeVoice Studio"
    assert "/asr/transcribe" in schema["paths"]
    assert "/tts/synthesize" in schema["paths"]
