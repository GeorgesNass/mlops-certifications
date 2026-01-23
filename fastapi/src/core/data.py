#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
__author__ = "Georges Nassopoulos"
__copyright__ = None
__version__ = "1.0.0"
__email__ = "georges.nassopoulos@gmail.com"
__status__ = "Dev"
__desc__ = "Data access layer for loading and saving quiz questions from/to CSV."
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import pandas as pd

## Resolve base directory (fastapi/)
BASE_DIR = Path(__file__).resolve().parents[2]

## Path to the CSV file containing quiz questions
QUESTIONS_CSV_PATH = BASE_DIR / "data" / "questions.csv"

def load_questions() -> Tuple[pd.DataFrame, List[dict]]:
    """
        Load quiz questions from the CSV file

        The questions are loaded once and kept in memory for fast access
        This function preserves the original behavior: CSV -> DataFrame -> list of dicts

        Returns:
            tuple:
                - pandas.DataFrame: Raw DataFrame loaded from CSV
                - list[dict]: List of questions as dictionaries
    """
    
    ## Read CSV file containing questions
    df = pd.read_csv(QUESTIONS_CSV_PATH)

    ## Convert DataFrame to list of dictionaries (original behavior)
    questions = df.to_dict(orient="records")

    return df, questions

def save_questions(df: pd.DataFrame) -> None:
    """
        Persist quiz questions to the CSV file

        This function overwrites the existing CSV file with the provided DataFrame

        Args:
            df (pandas.DataFrame): Updated DataFrame containing all questions
    """
    
    ## Save DataFrame back to CSV without index
    df.to_csv(QUESTIONS_CSV_PATH, index=False)