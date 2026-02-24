# ============================================
# STAGE 1: Builder
# ============================================
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# ============================================
# STAGE 2: Runtime
# ============================================
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install from wheels WITH dependencies
COPY --from=builder /wheels /wheels
COPY --from=builder /build/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf /wheels requirements.txt

# Copy app files
COPY main.py database.py models.py schemas.py cache.py helpers.py ./

# Cleanup
RUN find /usr/local -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true \
    && find /usr/local -type f -name '*.pyc' -delete

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]