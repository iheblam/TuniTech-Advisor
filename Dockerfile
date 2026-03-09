# ── Backend Dockerfile ──────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Install OS-level deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api/        ./api/
COPY dataset/    ./dataset/
COPY models/     ./models/
COPY train_model.py .
COPY run_api.py .

# mlruns is gitignored – create an empty directory so MLflow can write to it
RUN mkdir -p /app/mlruns

# data/ is no longer needed in the image – all persistent data lives in MongoDB
RUN mkdir -p /app/data

# Expose the API port
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
