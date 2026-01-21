'''
__author__ = "Georges Nassopoulos"
__copyright__ = None
__version__ = "1.0.0"
__email__ = "georges.nassopoulos@gmail.com"
__status__ = "Prod"
__desc__ = "Request schema for accident severity prediction."
'''

from __future__ import annotations

from pydantic import BaseModel

class Accident(BaseModel):
    """
        Input payload for the /predict/ endpoint

        This schema is extracted from the original monolithic app.py and kept
        unchanged to avoid breaking compatibility with the existing model and
        dashboards
    """

    ## Categorical / numeric features used by the trained model
    place: int
    catu: int
    sexe: int
    secu1: float
    year_acc: int
    victim_age: int
    catv: int
    obsm: int
    motor: int
    catr: int
    circ: int
    surf: int
    situ: int
    vma: int
    jour: int
    mois: int
    lum: int
    dep: int
    com: int
    agg_: int
    int_: int
    atm: int
    col: int
    lat: float
    long: float
    hour: int
    nb_victim: int
    nb_vehicules: int
