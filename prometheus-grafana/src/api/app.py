'''
__author__ = "Georges Nassopoulos"
__copyright__ = None
__version__ = "1.0.0"
__email__ = "georges.nassopoulos@gmail.com"
__status__ = "Prod"
__desc__ = "FastAPI application factory (model load + routes + metrics)."
'''

from __future__ import annotations

from fastapi import FastAPI

from src.api.routes import router
from src.core.model import load_model
from src.monitoring.metrics import setup_metrics


def create_app() -> FastAPI:
    app = FastAPI(title="Accident Severity Prediction API")

    ## Load model once
    app.state.model = load_model()

    ## Register routes
    app.include_router(router)

    ## Prometheus metrics
    setup_metrics(app)

    return app


## ASGI entrypoint
app = create_app()
