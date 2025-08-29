# Multi-stage Docker build for Django ML app
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies and Python packages
RUN apt-get update && apt-get install -y \
    curl \
    g++ \
    gcc \
    libmariadb-dev \
    libpq-dev \
    pkg-config \
    wget \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash app

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ .

# Create necessary directories and set permissions
RUN mkdir -p /app/ml_models/saved_models \
    /app/media \
    /app/staticfiles \
    /app/logs \
    && chown -R app:app /app

# Copy ML models if they exist
COPY --chown=app:app src/ml_models/saved_models/ /app/ml_models/saved_models/

# Switch to non-root user
USER app

# Collect static files
RUN python manage.py collectstatic --noinput

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Expose port
EXPOSE 8000

# Default command - can be overridden
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

