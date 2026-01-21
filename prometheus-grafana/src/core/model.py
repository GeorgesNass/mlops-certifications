'''
__author__ = "Georges Nassopoulos"
__copyright__ = None
__version__ = "1.0.0"
__email__ = "georges.nassopoulos@gmail.com"
__status__ = "Prod"
__desc__ = "Model loading and feature vector utilities."
'''

from __future__ import annotations

from pathlib import Path
from typing import Any
import os

import joblib
import numpy as np

from src.schemas.accident import Accident

def load_model() -> Any:
    """
        Load the trained model from disk

        Priority:
        1) MODEL_PATH env var (if set)
        2) /usr/src/app/models/trained_model.joblib (container standard)
        3) ./models/trained_model.joblib (when running locally from project root)
    """
    env_path = os.getenv("MODEL_PATH")
    candidates = [
        Path(env_path) if env_path else None,
        Path("/usr/src/app/models/trained_model.joblib"),
        Path("models/trained_model.joblib"),
    ]

    for path in [p for p in candidates if p is not None]:
        if path.is_file():
            return joblib.load(path)

    checked = "\n".join(f"- {p}" for p in candidates if p is not None)
    raise FileNotFoundError(
        f"Model file not found. Checked:\n{checked}"
    )
    
def build_features(accident: Accident) -> np.ndarray:
    """
        Build the model input feature vector from the request payload

        Args:
            accident (Accident): Parsed request payload

        Returns:
            np.ndarray: Feature vector shaped as (1, n_features)
    """
    
    ## Build the feature vector exactly like the original code
    features = np.array([
        accident.place, accident.catu, accident.sexe, accident.secu1, accident.year_acc,
        accident.victim_age, accident.catv, accident.obsm, accident.motor, accident.catr,
        accident.circ, accident.surf, accident.situ, accident.vma, accident.jour, accident.mois,
        accident.lum, accident.dep, accident.com, accident.agg_, accident.int_, accident.atm,
        accident.col, accident.lat, accident.long, accident.hour,
        accident.nb_victim, accident.nb_vehicules,
    ])

    ## Ensure correct shape for scikit-learn predict
    return features.reshape(1, -1)
