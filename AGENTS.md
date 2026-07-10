# AGENTS.md

## Commands

```sh
uv sync                    # install deps (uv, not pip)
uv sync --group dev        # include dev deps (pytest, coverage)
python -m stirlingpdf_assistant.main  # run bot
stirling-bot              # same via entrypoint
pytest                    # run all tests (src is on sys.path via pyproject.toml)
pytest tests/test_tools.py -v  # single test file
```

## Architecture

- Package: `stirlingpdf_assistant` under `src/`
- Entrypoint: `src/stirlingpdf_assistant/main.py` / `stirlingpdf_assistant.main:main`
- Classes: modular tool pattern via `BaseTool` (api/tools/base.py), each maps to one Stirling PDF API endpoint
- Client: `StirlingPDFClient` (`api/client.py`) — async httpx transport, multipart/form-data via `tool.prepare_payload()`
- Bot: `python-telegram-bot` v22+, handlers in `bot/handlers.py`
- Security: two decorators in `bot/decorators.py` — `restricted` (whitelist) and `owner_only`
- i18n: en/es in `utils/i18n.py`, auto-detected from `user.language_code`
- Merge mode: hybrid state via `chat_data`; images auto-converted to PDF before final merge
- ZIP output detected by `b"PK\x03\x04"` magic bytes

## Testing

- `pytest-asyncio` with `asyncio_mode = auto` and `asyncio_default_fixture_loop_scope = "function"`
- Integration tests (`test_integration_api.py`) are `@pytest.mark.skipif` — require live Stirling PDF (set `STIRLING_PDF_URL` and `STIRLING_PDF_API_KEY`)
- `test_user_manager.py` uses fixture creating `test_users.json` (auto-cleaned)
- No lint or typecheck config in pyproject.toml — only pytest + coverage for dev

## Config & Run

- `.env` with: `TELEGRAM_BOT_TOKEN`, `STIRLING_PDF_URL`, `STIRLING_PDF_API_KEY`, `BOT_OWNER_ID`, `USERS_FILE`, `MAX_CONCURRENT_TASKS`, `MAX_FILE_SIZE_MB`, `API_TIMEOUT`
- `users.json` persisted via Docker volume (`./users.json:/app/users.json`)
- Python 3.14 required (`requires-python = ">=3.14"`)
- Docker: multi-stage, non-root user `appuser:appgroup` (UID 1000), `cmd ["stirling-bot"]`
- CI: builds + Trivy scan + pushes multi-arch image to ghcr.io (linux/amd64, linux/arm64)

## Quirks

- `bot/handlers.py` has duplicate `from stirlingpdf_assistant.api.tools import` blocks (lines 14 and 29). Keep both in sync or deduplicate.
- `scripts/api_validate.py` mentioned in README does not exist — the live validation was moved to `tests/test_integration_api.py`.
- All tools expose `input_schema` (JSON Schema) for planned MCP compatibility.
