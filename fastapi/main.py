#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
__author__ = "Georges Nassopoulos"
__copyright__ = None
__version__ = "1.0.0"
__email__ = "georges.nassopoulos@gmail.com"
__status__ = "Dev"
__desc__ = "FastAPI server entrypoint (root) exposing quiz endpoints with basic auth and custom error handlers."
"""

from __future__ import annotations

import datetime
import random
from typing import Any, Dict, List

import pandas as pd
from fastapi import Depends, FastAPI, HTTPException

from src.core.auth import authenticate
from src.core.data import load_questions, save_questions
from src.core.exceptions import register_exception_handlers
from src.models.schemas import QuizRequest

## Create FastAPI application (root entrypoint expected by uvicorn: main:app)
app = FastAPI()

## Register custom exception handlers (401/400/404/422 + custom examples)
register_exception_handlers(app)

## Load questions once at startup (in-memory list) from CSV
_df_questions, QUESTIONS = load_questions()

@app.get("/verify")
def verify() -> Dict[str, str]:
    """
        Healthcheck endpoint to verify the API is running

        Returns:
            dict: A short success message
    """
    
    return {"message": "API is running."}

@app.post("/generate_quiz")
def generate_quiz(
    payload: QuizRequest,
    user: str = Depends(authenticate),
) -> Dict[str, List[Dict[str, Any]]]:
    """
        Generate a quiz from the CSV dataset based on filters

        This endpoint is protected with HTTP Basic authentication

        Args:
            payload (QuizRequest): Request payload containing test_type, categories, and number_of_questions
            user (str): Authenticated username (injected by FastAPI dependency)

        Returns:
            dict: A JSON object containing a list of formatted quiz questions

        Raises:
            HTTPException: 404 if no questions match the filters
    """
    
    ## Filter questions by 'use' (test_type) and 'subject' (categories)
    wanted_categories = [cat.strip().lower() for cat in payload.categories]
    wanted_test_type = payload.test_type.strip().lower()

    filtered = [
        q
        for q in QUESTIONS
        if (q.get("use") or "").strip().lower() == wanted_test_type
        and (q.get("subject") or "").strip().lower() in wanted_categories
    ]

    if not filtered:
        ## Keep the same behavior: a 404 with a structured detail object
        raise HTTPException(
            status_code=404,
            detail={
                "error": "No questions found.",
                "message": f"HTTP error detected at {datetime.datetime.now().isoformat()}",
            },
        )

    ## Randomize order then take the requested amount
    random.shuffle(filtered)
    selected = filtered[: payload.number_of_questions]

    ## Format output without reinventing data structure
    formatted = []
    for q in selected:
        propositions = {
            key[-1]: q[key]
            for key in q
            if key.startswith("response") and pd.notna(q[key])
        }

        formatted.append(
            {
                "question": q.get("question"),
                "propositions": propositions,
                "answer": q.get("correct"),
            }
        )

    return {"quiz": formatted}

@app.post("/create_question")
def create_question(new_question: Dict[str, Any]) -> Dict[str, str]:
    """
        Create a new question (admin-only) and persist it to CSV

        Notes:
            - This keeps the original simple admin credentials check
            - The question is appended to the in-memory list and then saved to disk

        Args:
            new_question (dict): Question payload including admin_username/admin_password plus question fields

        Returns:
            dict: Success message

        Raises:
            HTTPException: 403 if admin credentials are invalid
    """
    
    ## Minimal admin gate (kept as-is for the exam scope)
    if (
        new_question.get("admin_username") != "admin"
        or new_question.get("admin_password") != "4dm1N"
    ):
        raise HTTPException(status_code=403, detail="Access denied.")

    ## Remove admin credentials before persisting
    cleaned_question = {
        key: value
        for key, value in new_question.items()
        if key not in {"admin_username", "admin_password"}
    }

    ## Update in-memory list
    QUESTIONS.append(cleaned_question)

    ## Persist to CSV using the shared helper
    df_updated = pd.DataFrame(QUESTIONS)
    save_questions(df_updated)

    return {"message": "Question created successfully and saved to CSV."}