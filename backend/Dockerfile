FROM python:3.11-slim-bookworm

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy pip configuration for faster/more reliable downloads
COPY pip/pip.conf /etc/pip.conf

# Copy requirements and wheels
COPY requirements.txt .
COPY wheels /wheels

# Install Python packages with extended timeout
# Install from local wheels (no network needed!)
# Install from wheels first, then fall back to PyPI for missing ones
RUN pip install --no-cache-dir --find-links=/wheels --timeout 600 --retries 10 -r requirements.txt


# Copy application
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
