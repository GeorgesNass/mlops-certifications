## Lightweight Python base image (recent and stable)
FROM python:3.12-slim

## Set working directory inside the container
WORKDIR /app

## Copy the test script into the container
COPY test_auth.py .

## Install runtime dependency (avoid caching build artifacts)
RUN pip install --no-cache-dir requests

## Run the authentication test
CMD ["python", "test_auth.py"]
