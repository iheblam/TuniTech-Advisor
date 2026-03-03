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
COPY mlruns/     ./mlruns/
COPY train_model.py .
COPY run_api.py .

# Expose the API port
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
