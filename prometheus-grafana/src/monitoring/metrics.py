'''
__author__ = "Georges Nassopoulos"
__copyright__ = None
__version__ = "1.0.0"
__email__ = "georges.nassopoulos@gmail.com"
__status__ = "Prod"
__desc__ = "Prometheus metrics utilities and middleware for FastAPI."
'''

from __future__ import annotations

from fastapi import FastAPI
from prometheus_client import Counter, Summary
from prometheus_fastapi_instrumentator import Instrumentator

## Summary metric to track model inference duration
inference_time_seconds = Summary(
    "inference_time_seconds",
    "Time spent during model inference",
)

## Counter metric to track total prediction requests
api_predict_total = Counter(
    "api_predict_total",
    "Total number of prediction requests",
)

## Backward-compatible aliases (in case other modules import old names)
inference_time_summary = inference_time_seconds
prediction_counter = api_predict_total

def setup_metrics(app: FastAPI) -> None:
    """Attach Prometheus instrumentation and expose /metrics endpoint.

    Args:
        app: FastAPI application instance.
    """
    
    ## Instrument HTTP requests (latency, status codes, etc.) and expose /metrics
    Instrumentator().instrument(app).expose(app)
