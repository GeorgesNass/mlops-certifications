#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
__author__ = "Georges Nassopoulos"
__copyright__ = None
__version__ = "1.0.0"
__email__ = "georges.nassopoulos@gmail.com"
__status__ = "Dev"
__desc__ = "Pydantic models (schemas) used by the FastAPI quiz endpoints."
"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

class QuizRequest(BaseModel):
    """
        Schema representing the payload required to generate a quiz

        This model is used by the `/generate_quiz` endpoint
    """

    test_type: str = Field(
        ...,
        description="Type of test to generate (e.g. 'multiple_choice', 'validation_test').",
        example="multiple_choice",
    )
    categories: List[str] = Field(
        ...,
        description="List of categories/subjects to filter questions.",
        example=["Docker", "FastAPI"],
    )
    number_of_questions: int = Field(
        ...,
        gt=0,
        description="Number of questions to include in the generated quiz.",
        example=5,
    )