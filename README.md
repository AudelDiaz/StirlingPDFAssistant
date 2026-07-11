# Stirling PDF Assistant

A Telegram bot for PDF operations via a self-hosted [Stirling PDF](https://github.com/Stirling-Tools/Stirling-PDF) instance. Designed for Raspberry Pi and low-resource environments, with multi-language support and access control.

## Features

- **Access control**: Whitelist-based user management with owner approval workflow.
- **Multi-language**: English and Spanish, auto-detected from Telegram language settings.
- **Resource limits**: Configurable concurrency throttling and max file size.
- **Tools**:
  - Compress (target size, grayscale, linearize)
  - OCR (make scanned PDFs searchable)
  - Password encryption
  - PDF to Word (`.docx`)
  - Auto redact (mask keywords)
  - Split PDF (page ranges like `1,3,5-10`)
  - URL to PDF
  - Merge PDFs and images
  - Scanner effect
  - Image to PDF
  - File to PDF (Office docs, Markdown, text)

## Architecture

Each PDF operation is a class inheriting from `BaseTool`, which maps to one Stirling PDF API endpoint. The `StirlingPDFClient` handles multipart transport via `httpx`. The bot uses `python-telegram-bot` v22+ with callback query handlers and `chat_data` for multi-step operations (merge, redact).

## Documentation

- **[Architecture](docs/architecture.md)**: System components and data flow.
- **[API Integration](docs/api_integration.md)**: How the bot communicates with Stirling PDF and the Tool pattern.
- **[User Management](docs/user_management.md)**: Security model, whitelisting, and owner approval workflow.

## Project Structure

```text
stirlingpdf-assistant/
├── docker/
│   ├── bot/                    # Multi-stage Docker build
│   └── telegram-bot-api/      # Custom local Bot API server (UID 1000)
├── docs/
│   ├── architecture.md
│   ├── api_integration.md
│   └── user_management.md
├── src/
│   └── stirlingpdf_assistant/
│       ├── api/        # API client and Tool definitions
│       ├── bot/        # Telegram handlers and decorators
│       ├── utils/      # I18n, user management
│       └── main.py     # Entry point
├── tests/
├── .env.example
├── AGENTS.md
├── docker-compose.yml
├── LICENSE
└── pyproject.toml
```

## Quick Start

### Prerequisites

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) or pip
- A running Stirling PDF instance with API enabled

### Configuration

```bash
cp .env.example .env
```

Key environment variables:

- `TELEGRAM_BOT_TOKEN` — from @BotFather.
- `STIRLING_PDF_URL` — your Stirling PDF endpoint.
- `STIRLING_PDF_API_KEY` — your Stirling API key.
- `BOT_OWNER_ID` — your Telegram user ID.
- `API_TIMEOUT` — request timeout in seconds (default 180). Increase for slow LibreOffice conversions on Raspberry Pi.
- `MAX_FILE_SIZE_MB` — max upload size in MB (default 50).
- `MAX_CONCURRENT_TASKS` — limit concurrent PDF operations (default 2).
- `USERS_FILE` — path to the users JSON file (default `users.json`).

### Install and Run

With uv:

```bash
uv venv
source .venv/bin/activate
uv sync
python -m stirlingpdf_assistant.main
```

With Docker (local development):

```bash
docker build -t ghcr.io/audeldiaz/StirlingPDFAssistant:master -f docker/bot/Dockerfile .
docker build -t ghcr.io/audeldiaz/StirlingPDFAssistant/telegram-bot-api:master -f docker/telegram-bot-api/Dockerfile .
docker compose up -d
```

With Docker (Raspberry Pi — pre-built images):

```bash
docker compose pull
docker compose up -d
```

Both images are multi-arch (linux/amd64, linux/arm64), built via GitHub Actions and published to `ghcr.io`.

## Docker and Raspberry Pi

The `docker/bot/Dockerfile` uses a multi-stage build with a non-root user (UID 1000) to reduce image size. The `docker/telegram-bot-api/Dockerfile` patches the base image UID/GID from 101 to 1000 so both containers can read files on the shared volume.

### Large Files (Local Telegram Bot API Server)

Telegram's cloud API limits file downloads to 20 MB. To handle larger files (up to 2 GB), run a local Telegram Bot API server:

1. Get `TELEGRAM_API_ID` and `TELEGRAM_API_HASH` from [my.telegram.org](https://my.telegram.org).
2. The `telegram-bot-api` service is already in `docker-compose.yml`.
3. Add `TELEGRAM_BOT_API_URL=http://telegram-bot-api:8081` to your `.env`.

See [Telegram's docs](https://core.telegram.org/bots/api#using-a-local-bot-api-server) for more.

### Shared Volume UID Matching

Both containers share the `telegram-bot-api-data` volume:

- `telegram-bot-api` runs as UID 1000 (user `telegram-bot-api`).
- `stirlingpdfassistant` runs as UID 1000 (user `appuser`).
- The custom Bot API Dockerfile patches the base image's UID/GID from 101 to 1000 via `sed` on `/etc/passwd` and `/etc/group`.

Without this, files created by the Bot API server are owned by UID 101 and the bot can't read them.

## Testing

```bash
# Unit tests (no external dependencies)
pytest

# Integration tests — requires STIRLING_PDF_URL and STIRLING_PDF_API_KEY
pytest tests/test_integration_api.py -v
```

## License

MIT
