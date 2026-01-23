#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
__author__ = "Georges Nassopoulos"
__copyright__ = None
__version__ = "1.0.0"
__email__ = "georges.nassopoulos@gmail.com"
__status__ = "Dev"
__desc__ = "Exploratory Data Analysis (EDA) on the questions dataset with plots (wordcloud, pie chart, histogram)."
"""

from __future__ import annotations

import os
from collections import Counter
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
import spacy
from wordcloud import WordCloud

## Resolve base directory (fastapi/)
BASE_DIR = Path(__file__).resolve().parents[2]

## Dataset and output folders
QUESTIONS_CSV_PATH = BASE_DIR / "data" / "questions.csv"
EDA_PLOTS_DIR = BASE_DIR / "eda_plots"

def _load_spacy_french_model(model_name: str = "fr_core_news_sm") -> Optional[spacy.Language]:
    """
        Load the French spaCy model required for stopwords filtering

        Args:
            model_name (str): spaCy French model name

        Returns:
            spacy.Language | None: Loaded spaCy NLP object, or None if loading fails
    """
    
    try:
        return spacy.load(model_name)
    except Exception:
        print(
            f"The spaCy model '{model_name}' is not installed.\n"
            f"Install it with: python3 -m spacy download {model_name}"
        )
        return None

def run_eda() -> None:
    """
        Run a basic EDA on the questions CSV and generate plots

        This script:
          - Prints simple descriptive statistics
          - Generates three plots into `eda_plots/`:
            1) Histogram of available answers per question
            2) Pie chart of subjects distribution
            3) Word cloud of frequent words in questions (stopwords removed)
    """
    
    ## Load dataset
    df = pd.read_csv(QUESTIONS_CSV_PATH)

    ## Load spaCy French model
    nlp = _load_spacy_french_model()
    if nlp is None:
        return

    stopwords = nlp.Defaults.stop_words

    ## Create output directory for plots
    os.makedirs(EDA_PLOTS_DIR, exist_ok=True)

    ## Basic stats
    print(f"Number of questions: {len(df)}")
    print("\nSubject distribution:")
    print(df["subject"].value_counts())
    print("\nTest type distribution:")
    print(df["use"].value_counts())

    ## Histogram: number of available responses (A/B/C/D not null)
    df["nb_answers"] = df[["responseA", "responseB", "responseC", "responseD"]].notna().sum(axis=1)

    plt.figure()
    df["nb_answers"].value_counts().sort_index().plot(kind="bar")
    plt.title("Number of answers per question")
    plt.xlabel("Number of available answers")
    plt.ylabel("Number of questions")
    plt.tight_layout()
    plt.savefig(EDA_PLOTS_DIR / "histogram_reponses.png")

    ## Pie chart: subjects distribution
    plt.figure()
    df["subject"].value_counts().plot(kind="pie", autopct="%1.1f%%")
    plt.title("Subjects distribution")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(EDA_PLOTS_DIR / "pie_subjects.png")

    ## Word cloud: frequent words from questions (min frequency >= 3)
    text = " ".join(df["question"].dropna().astype(str)).lower()

    ## Tokenize and filter (alphabetic tokens only, no stopwords)
    tokens = [t.text for t in nlp(text) if t.is_alpha and t.text not in stopwords]

    freq = Counter(tokens)
    freq_filtered = {word: count for word, count in freq.items() if count >= 3}

    if not freq_filtered:
        print("\nNot enough frequent words to generate a word cloud.")
        return

    wc = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(freq_filtered)
    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.title("Word cloud from questions (frequent words only)")
    plt.tight_layout()
    plt.savefig(EDA_PLOTS_DIR / "wordcloud_questions.png")

    print(f"\nPlots saved into: {EDA_PLOTS_DIR}")

if __name__ == "__main__":
    run_eda()