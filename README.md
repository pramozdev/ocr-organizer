<h1 align="center">OCR Organizer</h1>

<p align="center">
  <b>Local Python API for intelligent image text analysis</b>
</p>

<p align="center">
  <a href="https://github.com/pramozdev/ocr-organizer/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/pramozdev/ocr-organizer/ci.yml?branch=main&style=for-the-badge&logo=githubactions&logoColor=white&label=CI&color=2088FF" alt="CI">
  </a>
  <a href="https://github.com/pramozdev/ocr-organizer/releases">
    <img src="https://img.shields.io/github/v/release/pramozdev/ocr-organizer?style=for-the-badge&logo=github&logoColor=white&label=Release&color=00C7B7" alt="Release">
  </a>
  <a href="https://github.com/pramozdev/ocr-organizer/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/pramozdev/ocr-organizer?style=for-the-badge&logo=opensourceinitiative&logoColor=white&label=License&color=green" alt="License">
  </a>
</p>

<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.12+-FFD43B?style=flat-square&logo=python&logoColor=blue" alt="Python">
  </a>
  <a href="https://fastapi.tiangolo.com/">
    <img src="https://img.shields.io/badge/FastAPI-0.136.3-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
  </a>
  <a href="https://github.com/tesseract-ocr/tesseract">
    <img src="https://img.shields.io/badge/Tesseract-OCR-black?style=flat-square&logo=google&logoColor=white" alt="Tesseract">
  </a>
  <a href="https://docs.pydantic.dev/">
    <img src="https://img.shields.io/badge/Pydantic-V2-E92063?style=flat-square&logo=pydantic&logoColor=white" alt="Pydantic">
  </a>
  <a href="https://github.com/psf/black">
    <img src="https://img.shields.io/badge/Style-Black-000000?style=flat-square&logo=python&logoColor=white" alt="Black">
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Tests-27%20passing-success?style=flat-square&logo=pytest&logoColor=white" alt="Tests">
  <img src="https://img.shields.io/badge/Async-Thread%20Pool-FF6F00?style=flat-square" alt="Async">
  <img src="https://img.shields.io/badge/OCR-Tesseract%20OCR-blueviolet?style=flat-square" alt="OCR">
</p>

<p align="center">
  <a href="#features">Features</a> &bull;
  <a href="#quick-start">Quick Start</a> &bull;
  <a href="#api-endpoints">API</a> &bull;
  <a href="#architecture">Architecture</a> &bull;
  <a href="#use-cases">Use Cases</a>
</p>

---

**Local Python API for intelligent image text analysis.** Extracts text from images using Tesseract OCR, structures it semantically, and generates AI-ready prompts for local LLM interpretation.

## Features

- **OCR Engine** — Tesseract OCR with Portuguese language support
- **Smart Preprocessing** — Deskew, denoise, sharpen, grayscale, resize, threshold
- **Semantic Parsing** — Auto-classifies text into questions, alternatives, titles, CTAs, emails, phones, links, and list items
- **Deep Document Analysis** — Identifies document type (Quiz, Exam, Article, Landing Page, WhatsApp Chat, etc.)
- **AI Integration** — Generates formatted prompts for local LLMs (full analysis or summary modes)
- **Async Architecture** — CPU-bound OCR and preprocessing run in thread pools to avoid blocking the event loop
- **CLI Tools** — Direct image analysis, clipboard bridge, and screenshot capture utilities

## Tech Stack

| Layer | Technology |
|-------|------------|
| Web Framework | FastAPI + Uvicorn |
| Validation | Pydantic V2 + pydantic-settings |
| OCR | Tesseract (pytesseract) |
| Image Processing | OpenCV + Pillow |
| Logging | Loguru |
| Testing | pytest + pytest-asyncio |

## Quick Start

### Prerequisites

```bash
# Ubuntu/Debian
sudo apt install tesseract-ocr tesseract-ocr-por

# Optional: clipboard tools
sudo apt install xclip          # X11
sudo apt install wl-clipboard   # Wayland

# Optional: screenshot capture
sudo apt install imagemagick
```

### Installation

```bash
git clone https://github.com/pramozdev/ocr-organizer.git
cd ocr-organizer/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run the API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Interactive docs: http://localhost:8000/docs

## API Endpoints

### Core OCR
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/analyze` | OCR + semantic parsing |
| POST | `/api/v1/analyze/deep` | Deep analysis (document type, structure, reading order) |

### AI Bridge
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/ai/analyze` | Full OCR + formatted AI prompt |
| POST | `/api/v1/ai/summary` | OCR + summary AI prompt |

All endpoints support preprocessing flags: `grayscale`, `threshold`, `denoise`, `sharpen`, `resize`, `deskew`.

## CLI Usage

```bash
# Analyze an image locally
python cli_analyze.py image.png --mode full

# Generate a summary prompt
python cli_analyze.py image.png --mode summary --context "Python course page"
```

## Desktop Tools

```bash
# Screenshot area selection
python tools/ocr_screenshot.py

# Fullscreen capture
python tools/ocr_screenshot.py --fullscreen

# Clipboard bridge (image already in system clipboard)
python tools/clipboard_ocr.py
```

## Architecture

```
backend/
├── app/
│   ├── api/          # FastAPI routes (DRY preprocess params, global exception handlers)
│   ├── ai_local/     # OCR -> AI bridge (prompt builder, interpreter)
│   ├── core/         # Settings, custom exceptions, lifespan events
│   ├── ocr/          # Tesseract engine (line-level grouping, newline preservation)
│   ├── vision/       # OpenCV preprocessing pipeline
│   ├── parsers/      # Semantic + deep document parsers
│   ├── schemas/      # Pydantic V2 models
│   ├── services/     # Async orchestration with thread pool executor
│   └── utils/        # Lazy logger init, lazy validation constants
├── tests/            # pytest suite (27 tests passing)
└── tools/            # Desktop utilities (clipboard, screenshot)
```

## Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
HOST=0.0.0.0
PORT=8000
MAX_FILE_SIZE_MB=20
OCR_LANG=por
PREPROCESS_MAX_DIM=2000
```

## Real-World Use Cases

1. **Quiz / Exam Solver** — Screenshot a question, get structured text + AI prompt with alternatives
2. **Document Data Extraction** — Scan contracts, invoices, IDs; extract emails, phones, dates automatically
3. **WhatsApp Chat Archiving** — Screenshots of conversations parsed and summarized by AI
4. **Accessibility** — Convert inaccessible images to structured text for screen readers
5. **Legacy System Bridge** — Read data from old ERP screens without APIs

## Testing

```bash
cd backend
pytest tests/ -v
```

## License

MIT — see [LICENSE](LICENSE)
