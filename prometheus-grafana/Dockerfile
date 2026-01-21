## Use a modern Python version compatible with scikit-learn 1.5.x
FROM python:3.11-slim

## Set the working directory inside the container
WORKDIR /usr/src/app

## Copy the application source code
COPY ./src /usr/src/app/src

## Copy the FastAPI entrypoint module
COPY ./main.py /usr/src/app/main.py

## Copy the trained model artifacts
COPY ./models /usr/src/app/models

## Copy Python dependencies
COPY ./requirements.txt /usr/src/app/requirements.txt

## Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /usr/src/app/requirements.txt

## Expose the FastAPI port
EXPOSE 8000

## Run the FastAPI app with reduced log noise
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "warning"] ## no logs INFO
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "warning", "--access-log", "false"]
