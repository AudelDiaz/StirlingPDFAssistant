# 🛰️ Stirling PDF Assistant

A production-grade Telegram bot optimized for **Raspberry Pi** and low-resource environments. It provides a secure, multilingual interface for performing powerful PDF operations via a private [Stirling PDF](https://github.com/Stirling-Tools/Stirling-PDF) instance.

![PDF Assistant](https://raw.githubusercontent.com/Stirling-Tools/Stirling-PDF/main/docs/stirling-pdf-logo.png)

## 🌟 Key Features

- **🛡️ Secure Access**: Built-in User Management System with Owner Approval workflow.
- **🌍 Multilingual**: Native English and Spanish support with automatic language detection.
- **⚡ Resource Aware**: Concurrency throttling (Semaphores) and file size safeguards to protect your Raspberry Pi.
- **📝 Private OCR**: Optical Character Recognition using your own Stirling instance.
- **✂️ Advanced Tools**:
  - **🗜 Compress**: Reduce file size with optional target size, grayscale, and linearize.
  - **🔍 OCR**: Make scanned PDFs searchable.
  - **🔒 Password**: Encrypt PDFs with a secure password.
  - **📝 To Word**: Convert PDFs to editable `.docx` files.
  - **🛡 Auto Redact**: Mask sensitive info (emails, IDs) automatically.
  - **✂️ Split PDF**: Extract specific page ranges (e.g., `1,3,5-10`).
  - **🌐 URL to PDF**: Send a link, get a clean PDF document back instantly.
  - **📚 Hybrid Merge**: Mix Photos and PDFs into a single document seamlessly.
  - **🖨 Scanner Effect**: Make digital docs look like scanned paper documents.
  - **📄 File to PDF**: Convert Office docs, Markdown, and text files to PDF.

## 🏗️ Architecture

The project uses a **Modular Tool Architecture**:
- Each PDF operation is a self-documenting Class.
- Highly scalable and aligned with the **Model Context Protocol (MCP)**.
- Hybrid state management for complex multi-step operations (Merging, Redacting).

## 📚 Documentation

Detailed documentation is available in the `docs/` folder:

- **[Architecture](docs/architecture.md)**: High-level overview of the system components and data flow.
- **[API Integration](docs/api_integration.md)**: Details on how the bot communicates with Stirling PDF and the "Tool" pattern.
- **[User Management](docs/user_management.md)**: Explains the security model, whitelisting, and owner approval workflow.

## 📂 Project Structure

```text
stirlingpdf-assistant/
├── docker/
│   ├── bot/                    # Multi-stage Docker build
│   └── telegram-bot-api/      # Custom local Bot API server (UID 1000)
├── docs/                      # Detailed documentation
│   ├── architecture.md
│   ├── api_integration.md
│   └── user_management.md
├── src/
│   └── stirlingpdf_assistant/
│       ├── api/        # Stirling PDF API client and Tool definitions
│       ├── bot/        # Telegram bot handlers and decorators
│       ├── utils/      # I18n, user management, and common utilities
│       └── main.py     # Application entry point
├── tests/              # Test suite for API and logic
├── .env.example        # Environment variable template
├── AGENTS.md           # Developer onboarding and quirks
├── docker-compose.yml  # Docker Compose orchestration
├── LICENSE             # MIT License
└── pyproject.toml      # Project dependencies and metadata
```

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.14+
- [uv](https://github.com/astral-sh/uv) (Recommended) or `pip`
- A running Stirling PDF instance with API enabled.

### 2. Configuration
Create a `.env` file from the example:
```bash
cp .env.example .env
```
Key variables:
- `TELEGRAM_BOT_TOKEN`: Your bot token from @BotFather.
- `STIRLING_PDF_URL`: Your Stirling PDF endpoint.
- `STIRLING_PDF_API_KEY`: Your Stirling API Key.
- `BOT_OWNER_ID`: Your Telegram User ID.
- `API_TIMEOUT`: Request timeout in seconds (default: 180). Increase for slow LibreOffice conversions on Raspberry Pi.
- `MAX_FILE_SIZE_MB`: Max upload size in MB (default: 50).
- `MAX_CONCURRENT_TASKS`: Limit concurrent PDF operations (default: 2).
- `USERS_FILE`: Path to the users JSON file (default: `users.json`).

### 3. Installation & Run
Using `uv`:
```bash
uv venv
source .venv/bin/activate
uv sync
python -m stirlingpdf_assistant.main
```

Using Docker (development — build and run locally):
```bash
docker build -t ghcr.io/audeldiaz/StirlingPDFAssistant:master -f docker/bot/Dockerfile .
# Build the telegram-bot-api image if you need local changes:
docker build -t ghcr.io/audeldiaz/StirlingPDFAssistant/telegram-bot-api:master -f docker/telegram-bot-api/Dockerfile .
docker compose up -d
```

Using Docker (Raspberry Pi — pull pre-built from GHCR):
```bash
docker compose pull
docker compose up -d
```

Both images are built with multi-arch support (linux/amd64, linux/arm64) via a GitHub Actions matrix job and published to `ghcr.io`.

## 🐋 Docker & Raspberry Pi Optimization

The included `docker/bot/Dockerfile` uses a multi-stage build and a non-root user for maximum security and reduced image size, making it ideal for 64-bit ARM boards (Pi 4/5).

### 📥 Handling Large Files (Local Telegram Bot API Server)

Telegram's cloud Bot API limits file downloads to **20 MB**. To process larger files (up to 2 GB), run a **local Telegram Bot API server** alongside the bot:

1. Get your `TELEGRAM_API_ID` and `TELEGRAM_API_HASH` from [my.telegram.org](https://my.telegram.org).
2. The `telegram-bot-api` service is already included in `docker-compose.yml`.
3. Add `TELEGRAM_BOT_API_URL=http://telegram-bot-api:8081` to your `.env`.

The local server removes all download size restrictions and can handle files up to 2 GB. See [Telegram's official docs](https://core.telegram.org/bots/api#using-a-local-bot-api-server) for details.

### 🔑 Shared Volume UID Matching

Both containers share a Docker volume (`telegram-bot-api-data`) for file access:
- **telegram-bot-api** runs as UID 1000 (user `telegram-bot-api`) via `docker/telegram-bot-api/Dockerfile`.
- **stirlingpdfassistant** runs as UID 1000 (user `appuser`) via the multi-stage build.
- The custom Bot API Dockerfile patches the base image's UID/GID from 101 → 1000 using `sed` on `/etc/passwd` and `/etc/group`.

This ensures the bot container can read files downloaded by the Bot API server without permission errors.

## 🧪 Testing & Validation

```bash
# Unit tests (no external dependencies)
pytest

# Integration tests — validate compatibility with your Stirling PDF instance
# Requires STIRLING_PDF_URL and STIRLING_PDF_API_KEY to be set
pytest tests/test_integration_api.py -v
```

## 📜 License
MIT License.
