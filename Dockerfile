# ---------------------------------------------------------
# Team C: Production-Ready Dockerfile for Ledger Service
# ---------------------------------------------------------

# 1. Use a lightweight and secure base image
FROM python:3.11-slim

# 2. Set environment variables for production optimization
# Prevents Python from writing .pyc files and ensures output is sent straight to logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# 3. Set the working directory
WORKDIR /app

# 4. Install essential system dependencies for psycopg2 and security
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    libc-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Install Python dependencies
# Layer caching optimization: Copy requirements first
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Copy application code
COPY . .

# 7. Security: Create a non-root user to run the application
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
USER appuser

# 8. Expose the appropriate service port
EXPOSE 8000

# 9. Configure application startup commands
# Using uvicorn to serve the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
