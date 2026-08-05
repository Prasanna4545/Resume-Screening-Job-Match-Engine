# ---------- Stage 1: Export ONNX model (torch used only here, discarded after) ----------
FROM python:3.11-slim AS exporter

WORKDIR /export

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir "optimum[exporters]" transformers

RUN python -c "\
from optimum.onnxruntime import ORTModelForFeatureExtraction; \
from transformers import AutoTokenizer; \
model = ORTModelForFeatureExtraction.from_pretrained('sentence-transformers/all-MiniLM-L6-v2', export=True); \
model.save_pretrained('/export/onnx_model'); \
tok = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2'); \
tok.save_pretrained('/export/onnx_model')"

# ---------- Stage 2: Final slim runtime image (no torch at all) ----------
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV OMP_NUM_THREADS=1
ENV TOKENIZERS_PARALLELISM=false
ENV ONNX_MODEL_DIR=/app/onnx_model

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m spacy download en_core_web_sm

COPY --from=exporter /export/onnx_model /app/onnx_model

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
