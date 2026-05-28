FROM python:3.11-slim-bookworm

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy pip configuration for faster/more reliable downloads
COPY pip/pip.conf /etc/pip.conf

# Copy requirements
COPY requirements.txt .

# Install Python packages with extended timeout
RUN pip install --no-cache-dir --timeout 600 --retries 10 -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p models data

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5001/health')" || exit 1

# Run startup script that trains models if needed
CMD ["./startup.sh"]
