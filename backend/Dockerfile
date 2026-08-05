FROM python:3.11-slim

WORKDIR /app

# Set environment variables for threading & tokenizer memory optimization
ENV OMP_NUM_THREADS=1
ENV TOKENIZERS_PARALLELISM=false
ENV PYTHONUNBUFFERED=1

# Install system dependencies for C compilation and PostgreSQL driver
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Pre-install CPU-only PyTorch wheel before requirements.txt to prevent pulling heavy GPU/CUDA wheels
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download & cache spaCy model and ONNX sentence-transformers model at BUILD time
RUN python -m spacy download en_core_web_sm
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2', backend='onnx')"

COPY . .

EXPOSE 8000

# Run with single worker to prevent memory model duplication on 512MB RAM free hosts
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
