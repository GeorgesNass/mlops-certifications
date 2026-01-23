#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
__author__ = "Georges Nassopoulos"
__copyright__ = None
__version__ = "1.0.0"
__email__ = "georges.nassopoulos@gmail.com"
__status__ = "Dev"
__desc__ = "HTTP Basic authentication dependency for FastAPI (exam scope)."
"""

from __future__ import annotations

import secrets
from typing import Dict

from fastapi import Depends, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from src.core.exceptions import UnauthorizedAccessException

## HTTP Basic security scheme used by FastAPI dependencies
security = HTTPBasic()

## In-memory users database (kept as-is for the exam scope)
USERS: Dict[str, str] = {
    "alice": "wonderland",
    "bob": "builder",
    "clementine": "mandarine",
}

def authenticate(
    request: Request,
    credentials: HTTPBasicCredentials = Depends(security),
) -> str:
    """
        Authenticate a user using HTTP Basic credentials

        This function is designed to be used as a FastAPI dependency:
            user: str = Depends(authenticate)

        Args:
            request (Request): Incoming FastAPI request (used to build custom exceptions)
            credentials (HTTPBasicCredentials): Username/password provided via HTTP Basic auth

        Returns:
            str: The authenticated username

        Raises:
            UnauthorizedAccessException: If credentials are missing or invalid
    """
    
    ## Retrieve expected password from our in-memory store
    expected_password = USERS.get(credentials.username)

    ## Compare passwords using constant-time comparison
    is_valid = expected_password is not None and secrets.compare_digest(
        credentials.password,
        expected_password,
    )

    if not is_valid:
        raise UnauthorizedAccessException(request)

    return credentials.username