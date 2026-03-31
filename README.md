# VibeVoice Studio 🎙️

A FastAPI application for voice transcription and synthesis using [Microsoft VibeVoice](https://github.com/microsoft/VibeVoice) models.

## Features

- **ASR (Speech-to-Text)**: Upload audio up to 60 minutes long and get structured transcription with:
  - Speaker diarization (who said what)
  - Precise timestamps (when they said it)
  - Full text content (what was said)
  - 50+ languages with automatic detection
  - Custom hotwords/context for better accuracy

- **TTS (Text-to-Speech)**: Real-time speech synthesis with:
  - ~300ms first-audio latency
  - Streaming text input support
  - Up to ~10 minutes of generated audio
  - Multiple speaker voices

## Models Used

| Model | Purpose | Size | HF Link |
|-------|---------|------|---------|
| VibeVoice-ASR | Speech-to-text with diarization | 7B | [microsoft/VibeVoice-ASR-HF](https://huggingface.co/microsoft/VibeVoice-ASR-HF) |
| VibeVoice-Realtime | Real-time text-to-speech | 0.5B | [microsoft/VibeVoice-Realtime-0.5B](https://huggingface.co/microsoft/VibeVoice-Realtime-0.5B) |

> **Note**: VibeVoice-TTS (1.5B) was disabled by Microsoft due to misuse concerns and is NOT used.

## Prerequisites

- **Python 3.10+**
- **CUDA-capable GPU** (for model inference)
- **NVIDIA Deep Learning Container** recommended (24.07+ verified)
- **~16GB VRAM** for ASR model, ~4GB for TTS model

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/<username>/vibevoice-app-glm51.git
cd vibevoice-app-glm51
```

### 2. Create virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 3. Configure (optional)

Set environment variables or use defaults:

```bash
# ASR model (default: microsoft/VibeVoice-ASR-HF)
export ASR_MODEL_ID="microsoft/VibeVoice-ASR-HF"

# TTS model (default: microsoft/VibeVoice-Realtime-0.5B)
export TTS_MODEL_ID="microsoft/VibeVoice-Realtime-0.5B"

# Server settings
export HOST="0.0.0.0"
export PORT=8000

# Upload directory
export UPLOAD_DIR="uploads"
```

### 4. Run the server

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production (models will load on startup)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
```

### 5. Use the API

Open the interactive docs at **http://localhost:8000/docs**

#### Transcribe audio

```bash
curl -X POST http://localhost:8000/asr/transcribe \
  -F "file=@meeting.wav" \
  -F "prompt=John, Sarah, quarterly review"
```

Response:
```json
{
  "segments": [
    {
      "start": 0.0,
      "end": 15.43,
      "speaker": 0,
      "content": "Hello everyone, welcome to the quarterly review."
    }
  ],
  "full_text": "Hello everyone, welcome to the quarterly review. ...",
  "duration_seconds": 120.5,
  "num_speakers": 3
}
```

#### Synthesize speech

```bash
curl -X POST http://localhost:8000/tts/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, welcome to VibeVoice Studio!", "speaker_name": "Carter"}' \
  --output speech.wav
```

## Project Structure

```
vibevoice-app-glm51/
├── app/
│   ├── __init__.py          # App version
│   ├── main.py              # FastAPI app entry point
│   ├── api/
│   │   ├── asr.py           # ASR endpoints
│   │   └── tts.py           # TTS endpoints
│   ├── core/
│   │   └── config.py        # Configuration
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   └── services/
│       ├── asr.py           # VibeVoice-ASR service
│       └── tts.py           # VibeVoice-Realtime TTS service
├── tests/
│   ├── test_imports.py      # Import verification tests
│   ├── test_services.py     # Service unit tests
│   └── test_api.py          # API endpoint tests
├── pyproject.toml           # Project configuration
├── .gitignore
├── README.md
├── operations-log.md
└── metrics.md
```

## Development

### Run tests

```bash
# All tests (no GPU required)
pytest -v

# With coverage
pytest --cov=app -v
```

### Lint

```bash
ruff check app/ tests/
ruff format --check app/ tests/
```

## How It Works

### ASR Pipeline

1. Audio file is uploaded via the `/asr/transcribe` endpoint
2. The file is saved to a temporary location
3. `AutoProcessor.apply_transcription_request()` prepares the audio inputs
4. `VibeVoiceAsrForConditionalGeneration.generate()` produces the transcription
5. The processor decodes the output into structured segments with speaker labels
6. The temporary file is cleaned up

### TTS Pipeline

1. Text and optional speaker name are sent to `/tts/synthesize`
2. The VibeVoice Realtime model generates audio from the text
3. A WAV file is returned as the response

## Technology Choices

- **FastAPI**: High-performance async web framework with automatic OpenAPI docs
- **HuggingFace Transformers v5.3.0+**: Native VibeVoice-ASR integration
- **Pydantic v2**: Request/response validation and serialization
- **Uvicorn**: ASGI server with HTTP/1.1 and WebSocket support

## License

MIT License — This project. VibeVoice models are also MIT licensed (check model cards).

## References

- [VibeVoice GitHub](https://github.com/microsoft/VibeVoice)
- [VibeVoice-ASR Model Card](https://huggingface.co/microsoft/VibeVoice-ASR)
- [VibeVoice-ASR HF Integration Docs](https://huggingface.co/docs/transformers/model_doc/vibevoice_asr)
- [VibeVoice-Realtime-0.5B Model Card](https://huggingface.co/microsoft/VibeVoice-Realtime-0.5B)
- [VibeVoice-ASR Technical Report](https://arxiv.org/pdf/2601.18184)
- [VibeVoice TTS Technical Report](https://arxiv.org/abs/2508.19205)
