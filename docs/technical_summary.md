# Technical Summary: Stirling PDF Assistant

The **Stirling PDF Assistant** is a Telegram bot designed to serve as a bridge between users and a self-hosted [Stirling PDF](https://github.com/Stirling-Tools/Stirling-PDF) instance. It provides a user-friendly interface for common PDF manipulations like OCR, compression, merging, and security.

## 🏗️ Core Architecture

The project is built with Python 3.14+ and follows a modular, asynchronous architecture:

1.  **Telegram Layer (`python-telegram-bot`)**: Handles communication with the Telegram API, managing message routing, callback queries, and user sessions.
2.  **Logic Layer (`src/stirlingpdf_assistant/bot`)**: Contains the business logic for handling various PDF operations, including state management for complex tasks like "Merge Mode."
3.  **API Client Layer (`src/stirlingpdf_assistant/api`)**: A custom, asynchronous client built on `httpx` that interacts with the Stirling PDF REST API.
4.  **Tooling System (`src/stirlingpdf_assistant/api/tools.py`)**: A set of modular "Tool" classes that abstract individual Stirling PDF API endpoints. This design is inspired by the **Model Context Protocol (MCP)**, making it extensible for future AI agent integration.
5.  **Utility Layer (`src/stirlingpdf_assistant/utils`)**: Provides supporting functions for user management (persistence) and internationalization (i18n).

## 🛠️ Key Technologies

-   **Python 3.14+**: Leverages modern async/await patterns.
-   **`httpx`**: Used for efficient, asynchronous HTTP requests to the Stirling PDF API.
-   **`python-telegram-bot`**: A robust framework for building Telegram bots.
-   **`hatchling`**: Used as the build backend for the project.
-   **`pytest`**: Comprehensive testing suite for API validation and logic.

## 🔒 Security & Access Control

-   **Whitelisting**: Only authorized users can interact with the bot.
-   **Owner System**: A designated `BOT_OWNER_ID` has administrative rights (adding/removing users).
-   **Access Requests**: New users can request access, which the owner can approve or deny via inline buttons in Telegram.
-   **Safeguards**: Configurable limits on concurrent tasks (`MAX_CONCURRENT_TASKS`) and maximum file size (`MAX_FILE_SIZE_MB`) protect the host system (e.g., Raspberry Pi) from overload.

## 🌐 Features

-   **PDF Manipulation**: OCR (Searchable PDF), Compression, Merge, Password Protection, PDF to Word conversion.
-   **Image Support**: Convert one or more images into a single PDF.
-   **Scanner Effect**: Apply a "scanned" look to digital documents.
-   **Merge Mode**: A specialized mode for queueing multiple documents/images before merging them.
-   **Multi-language Support**: Full support for English and Spanish, with the ability to easily add more languages via `i18n.py`.

## 🚀 Future Roadmap

-   **MCP AI Agent**: Integrating an LLM to allow natural language commands (e.g., "Merge these three scans, OCR them, and protect the result with 'mypassword123'").
-   **Enhanced Tooling**: Expanding the supported Stirling PDF endpoints.
-   **Improved Persistence**: Moving from JSON-based user management to a lightweight database (e.g., SQLite) if needed.
