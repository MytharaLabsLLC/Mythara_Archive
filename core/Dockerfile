# Mythara Engine — Dockerfile

# Base image with reproducible pinned version
FROM python:3.11.6-slim-bookworm AS base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip==23.3.1 && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create output directory
RUN mkdir -p /output

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MYTHARA_ENV=production
ENV MYTHARA_MANIFEST_REF=ME-archive-0001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command runs validation suite
CMD ["python", "run_validation_suite.py"]

# Metadata
LABEL maintainer="Herbert Velez Jr. <MytharaLabsLLC@yahoo.com>"
LABEL version="1.0.0"
LABEL description="Mythara Engine - Symbolic clause orchestration system"
LABEL org.mythara.manifest-ref="ME-archive-0001"
