Project Plan: Stirling PDF Bot & AI Agent
1. Plan Overview

The objective is to leverage a self-hosted Stirling PDF instance on a Raspberry Pi 4B (8GB RAM, 1TB Disk) to provide a private, powerful PDF manipulation interface via Telegram.
Phase 1: Automation Bot (Current)

    Interface: Telegram Bot API using /commands and Inline Buttons.

    Logic: Python-based service acting as a bridge between Telegram and the Stirling PDF API.

    Infrastructure: Docker Compose running Stirling PDF and the Bot service on the RPi 4B.

    Key Features: OCR, Compression, Merging, and basic Security (Password/Watermark).

Phase 2: MCP AI Agent (Future)

    Interface: Natural language processing via an LLM (Claude, Gemini, or local Ollama).

    Logic: Implementing an MCP Server that exposes Stirling PDF endpoints as "Tools."

    Workflow: The AI analyzes user intent (e.g., "Summarize this scan and protect it with a password") and chains multiple API calls automatically.

2. Mermaid Diagrams
A. Sequence Diagram: Document Processing Flow

This diagram shows how the bot handles a user request to OCR and then compress a document.
Fragmento de código

sequenceDiagram
    participant User as Telegram User
    participant Bot as Telegram Bot
    participant Stirling as Stirling PDF API
    participant Disk as 1TB USB Disk

    User->>Bot: Sends PDF File
    Bot->>Disk: Store Temporary File
    User->>Bot: Request "OCR & Compress"
    
    rect rgb(200, 220, 240)
    Note over Bot, Stirling: Phase 1: OCR
    Bot->>Stirling: POST /api/v1/misc/ocr-pdf
    Stirling-->>Bot: Returns OCR'd PDF
    end

    rect rgb(220, 240, 200)
    Note over Bot, Stirling: Phase 2: Compression
    Bot->>Stirling: POST /api/v1/misc/compress-pdf
    Stirling-->>Bot: Returns Optimized PDF
    end

    Bot-->>User: Sends final processed file
    Bot->>Disk: Cleanup Temporary Files

B. Activity Diagram: Command vs. Agent Logic

This represents the decision flow when the system receives a file.
Fragmento de código

activityDiagram
    start
    :User uploads PDF;
    if (Layer?) is (Phase 1: Bot) then
        :Show Menu (OCR, Merge, Convert);
        :User selects specific command;
        :Execute 1:1 API mapping;
    else (Phase 2: MCP Agent)
        :Analyze user prompt with LLM;
        :Identify required Stirling Tools;
        repeat
            :Execute next Tool in chain;
        backward: Next step;
        until (Goal reached?)
    endif
    :Send final file to User;
    stop

C. C4 System Architecture

High-level view of how the components interact on your Raspberry Pi.
Fragmento de código

graph TD
    User((Telegram User))
    
    subgraph "Raspberry Pi 4B (8GB RAM)"
        direction TB
        TG_API[Telegram Bot API]
        Bot_Logic[Bot Logic / MCP Client]
        
        subgraph "Stirling PDF System"
            SPDF_API[Stirling PDF API]
            Libre[LibreOffice / OCR Engines]
        end
        
        Disk[(1TB USB Disk)]
    end
    
    LLM[Cloud LLM / Local Ollama]

    User <--> TG_API
    TG_API <--> Bot_Logic
    Bot_Logic <--> SPDF_API
    SPDF_API <--> Libre
    Bot_Logic <--> Disk
    Bot_Logic <--> LLM

3. High-Value API Endpoint Mapping

Based on the Stirling PDF OpenAPI spec, the following endpoints are prioritized for the bot:
Category	Endpoint	Bot Feature
OCR	/api/v1/misc/ocr-pdf	Searchable PDF conversion
Optimization	/api/v1/misc/compress-pdf	Reduce file size
Conversion	/api/v1/convert/pdf/word	PDF to Docx
Security	/api/v1/security/add-password	Encrypt files
Analysis	/api/v1/analysis/page-count	Get document info
4. Implementation Steps

    Deployment: Use Docker Compose to launch stirling-tools/stirling-pdf:latest.

    Environment: Map the 1TB USB disk as the /configs and /tmp volumes in Docker to prevent SD card wear.

    Bot Development: Write the Python service using python-telegram-bot and httpx to interface with Stirling.

    MCP Integration: Once Phase 1 is stable, create a stirling-mcp-server that maps the JSON spec to MCP tool definitions.
