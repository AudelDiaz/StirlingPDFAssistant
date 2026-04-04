# Stirling PDF Assistant

A powerful, private Telegram Bot that serves as a bridge to your self-hosted [Stirling PDF](https://github.com/Stirling-Tools/Stirling-PDF) instance.

## 🚀 Overview

The Stirling PDF Assistant allows you to perform complex PDF operations directly from Telegram. It's designed to run on resource-constrained hardware like a Raspberry Pi 4B, providing a sleek interface for OCR, compression, merging, and more.

## 📖 Documentation

Detailed documentation is available in the `docs` folder:

-   [**Technical Summary**](docs/technical_summary.md): High-level project overview and technology stack.
-   [**System Architecture**](docs/architecture.md): Deep dive into the component design and data flow.
-   [**API Integration**](docs/api_integration.md): Understanding the modular "Tool" pattern and Stirling PDF communication.
-   [**User Management**](docs/user_management.md): Details on security, whitelisting, and access requests.
-   [**Bot Commands & Features**](docs/commands.md): A complete guide to using the bot.

## 🛠️ Quick Start

1.  **Clone the repository**.
2.  **Configure environment variables**: Copy `.env.example` to `.env` and fill in your `TELEGRAM_BOT_TOKEN`, `STIRLING_PDF_URL`, and `BOT_OWNER_ID`.
3.  **Run with Docker**:
    ```bash
    docker-compose up -d
    ```
4.  **Install locally (Development)**:
    ```bash
    uv sync
    stirling-bot
    ```

## ⚖️ License

This project is open-source. See the LICENSE file (if available) for details.
