## =============================================================================
## Dockerfile — FastAPI + SQLAlchemy + MySQL client
## =============================================================================

FROM python:3.10-slim

WORKDIR /app

## Install system dependencies needed by mysqlclient build
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    curl \
 && rm -rf /var/lib/apt/lists/*

## Copy dependency list first (better layer caching)
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r /app/requirements.txt

## Copy application code
COPY main.py /app/main.py

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
