# 🛰️ Stirling PDF Assistant

A production-grade Telegram bot optimized for **Raspberry Pi** and low-resource environments. It provides a secure, multilingual interface for performing powerful PDF operations via a private [Stirling PDF](https://github.com/Stirling-Tools/Stirling-PDF) instance.

![PDF Assistant](https://raw.githubusercontent.com/Stirling-Tools/Stirling-PDF/main/docs/stirling-pdf-logo.png)

## 🌟 Key Features

- **🛡️ Secure Access**: Built-in User Management System with Owner Approval workflow.
- **🌍 Multilingual**: Native English and Spanish support with automatic language detection.
- **⚡ Resource Aware**: Concurrency throttling (Semaphores) and file size safeguards to protect your Raspberry Pi.
- **📝 Private OCR**: Optical Character Recognition using your own Stirling instance.
- **✂️ Advanced Tools**:
  - **Auto Redact**: Mask sensitive info (emails, IDs) automatically.
  - **Split PDF**: Extract specific page ranges (e.g., `1,3,5-10`).
  - **URL to PDF**: Send a link, get a clean PDF document back instantly.
  - **Hybrid Merge**: Mix Photos and PDFs into a single document seamlessly.
  - **Scanner Effect**: Make digital docs look like scanned paper documents.

## 🏗️ Architecture

The project uses a **Modular Tool Architecture**:
- Each PDF operation is a self-documenting Class.
- Highly scalable and aligned with the **Model Context Protocol (MCP)**.
- Hybrid state management for complex multi-step operations (Merging, Redacting).

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
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

### 3. Installation & Run
Using `uv`:
```bash
uv venv
source .venv/bin/activate
uv sync
python -m stirlingpdf_assistant.main
```

Using Docker:
```bash
docker-compose up -d --build
```

## 🐋 Docker & Raspberry Pi Optimization
The included `Dockerfile` uses a multi-stage build and a non-root user for maximum security and reduced image size, making it ideal for 64-bit ARM boards (Pi 4/5).

## 🧪 Testing & Validation
A live validation suite is included to ensure your Stirling PDF API is compatible:
```bash
python scripts/api_validate.py
```

## 📜 License
MIT License. See `LICENSE` for details.
