# --- STAGE 1: Builder ---
# Use Python 3.14 for development and build-time optimizations
FROM python:3.14-slim AS builder

# Update OS packages and install build essentials if needed
RUN apt-get update && apt-get upgrade -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Upgrade pip and setuptools to fix known vulnerabilities
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set build directory
WORKDIR /app

# Enable bytecode compilation for faster startup
ENV UV_COMPILE_BYTECODE=1

# Copy build manifest and lockfile
COPY pyproject.toml uv.lock README.md /app/

# Sync dependencies (exclude dev group for production)
RUN uv sync --frozen --no-dev --no-install-project

# Copy source code and build/install the project
COPY src /app/src
RUN uv sync --frozen --no-dev

# --- STAGE 2: Runtime ---
# Use a fresh 3.14-slim image to discard build tools and reduce image size
FROM python:3.14-slim AS runtime

# Set runtime optimization flags
ENV PYTHONUNBUFFERED=1 \
    PYTHONOPTIMIZE=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Create a non-root system user for security (UID 1000 is standard for Pi)
RUN groupadd -r appgroup && useradd -r -g appgroup -u 1000 appuser

# Set work directory
WORKDIR /app

# Copy the virtual environment and installed package from the builder
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appgroup /app/src /app/src

# Set working directory permissions
RUN chown -R appuser:appgroup /app

# Switch to non-privileged user
USER appuser

# Healthcheck to ensure the container is alive (optional but recommended)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD pgrep -f "stirling-bot" || exit 1

# Launch the bot
CMD ["stirling-bot"]
