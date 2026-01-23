#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
__author__ = "Georges Nassopoulos"
__copyright__ = None
__version__ = "1.0.0"
__email__ = "georges.nassopoulos@gmail.com"
__status__ = "Dev"
__desc__ = "Custom exceptions and exception handlers registration for FastAPI."
"""

from __future__ import annotations

import datetime
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

class MyException(Exception):
    """Example custom exception (kept for the exam scope)"""

    def __init__(self, name: str, date: str) -> None:
        """
            Initialize the exception

            Args:
                name (str): Exception name
                date (str): Date string
        """
        
        self.name = name
        self.date = date

class BadIndexException(Exception):
    """Custom exception used when an index is invalid (kept for the exam scope)"""

    def __init__(self, request: Request) -> None:
        """
            Initialize the exception

            Args:
                request (Request): The incoming request
        """
        
        self.request = request
        self.name = "Invalid Index"
        self.date = str(datetime.datetime.now())

class InvalidIndexTypeException(Exception):
    """Custom exception used when an index has an invalid type (kept for the exam scope)"""

    def __init__(self, request: Request) -> None:
        """
            Initialize the exception

            Args:
                request (Request): The incoming request
        """
        
        self.request = request
        self.name = "Invalid Type"
        self.date = str(datetime.datetime.now())


class UnauthorizedAccessException(Exception):
    """Custom exception used when authentication fails (kept for the exam scope)"""

    def __init__(self, request: Request) -> None:
        """
            Initialize the exception

            Args:
                request (Request): The incoming request
        """
        
        self.request = request
        self.name = "Unauthorized"
        self.date = str(datetime.datetime.now())

def register_exception_handlers(app: FastAPI) -> None:
    """
        Register all custom exception handlers on the FastAPI app

        This function centralizes exception handling configuration

        Args:
            app (FastAPI): The FastAPI application instance
    """

    @app.exception_handler(MyException)
    async def handle_my_exception(request: Request, exc: MyException) -> JSONResponse:
        """
            Handle MyException with a playful 418 response

            Args:
                request (Request): Incoming request
                exc (MyException): Raised exception instance

            Returns:
                JSONResponse: JSON response describing the error
        """
        return JSONResponse(
            status_code=418,
            content={
                "url": str(request.url),
                "name": exc.name,
                "message": "Custom exception raised intentionally.",
                "date": exc.date,
            },
        )

    @app.exception_handler(BadIndexException)
    async def handle_bad_index(
        request: Request, exc: BadIndexException
    ) -> JSONResponse:
        """
            Handle BadIndexException

            Args:
                request (Request): Incoming request
                exc (BadIndexException): Raised exception instance

            Returns:
                JSONResponse: JSON response with status code 404
        """
        return JSONResponse(
            status_code=404,
            content={
                "url": str(request.url),
                "name": exc.name,
                "message": "Invalid index used to access a resource.",
                "date": exc.date,
            },
        )

    @app.exception_handler(InvalidIndexTypeException)
    async def handle_invalid_type(
        request: Request, exc: InvalidIndexTypeException
    ) -> JSONResponse:
        """
            Handle InvalidIndexTypeException

            Args:
                request (Request): Incoming request
                exc (InvalidIndexTypeException): Raised exception instance

            Returns:
                JSONResponse: JSON response with status code 400
        """
        return JSONResponse(
            status_code=400,
            content={
                "url": str(request.url),
                "name": exc.name,
                "message": "Invalid index type (e.g., an integer was expected).",
                "date": exc.date,
            },
        )

    @app.exception_handler(UnauthorizedAccessException)
    async def handle_unauthorized(
        request: Request, exc: UnauthorizedAccessException
    ) -> JSONResponse:
        """
            Handle UnauthorizedAccessException

            Args:
                request (Request): Incoming request
                exc (UnauthorizedAccessException): Raised exception instance

            Returns:
                JSONResponse: JSON response with status code 401
        """
        return JSONResponse(
            status_code=401,
            content={
                "url": str(request.url),
                "name": exc.name,
                "message": "Unauthorized access. Please authenticate.",
                "date": exc.date,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """
            Handle request validation errors (422)

            Args:
                request (Request): Incoming request
                exc (RequestValidationError): Validation error

            Returns:
                JSONResponse: JSON response describing validation issues
        """
        _ = request  ## Keep signature; request can be used for logging if needed
        return JSONResponse(
            status_code=422,
            content={"error": exc.errors(), "message": "Data validation error."},
        )

    @app.exception_handler(StarletteHTTPException)
    async def starlette_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """
            Handle Starlette HTTP exceptions (FastAPI underlying HTTP errors)

            Args:
                request (Request): Incoming request
                exc (StarletteHTTPException): HTTP exception

            Returns:
                JSONResponse: JSON response mirroring the status code and detail
        """
        
        _ = request  ## Keep signature; request can be used for logging if needed
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "message": f"HTTP error detected at {datetime.datetime.now().isoformat()}",
            },
        )

def _ensure_jsonable(detail: Any) -> Dict[str, Any]:
    """
        Ensure a detail object is JSON-serializable

        Notes:
            This helper is not used by default;
            useful to standardize error formatting later

        Args:
            detail (Any): Any detail object

        Returns:
            dict: A dictionary representation
    """
    
    if isinstance(detail, dict):
        return detail
    return {"detail": str(detail)}
