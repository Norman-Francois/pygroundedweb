"""Modèle représentant un Dataset retourné par l'API.

Contient le validateur de champ `date` pour accepter str/datetime.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional, Union

from pydantic import field_validator

from .base import APIModel
from .dataset_photo import DatasetPhoto
from .user import User


class Dataset(APIModel):
    """Représente un dataset côté client.

    Attributs
    ---------
    name: str
        Nom du dataset.
    date: date
        Date associée au dataset (convertie depuis str/datetime si nécessaire).
    user: Union[User, str]
        Utilisateur propriétaire (ou identifiant string).
    photos: Optional[List[DatasetPhoto]]
        Liste facultative des photos associées.
    """

    name: str
    date: date
    user: Union[User, str]
    photos: Optional[List[DatasetPhoto]] = None

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, value):
        """Accepte une datetime ou une chaîne ISO et renvoie une date.

        Lève ValueError si la chaîne n'est pas un ISO date valide.
        """
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value).date()
            except ValueError:
                raise ValueError(f"Invalid date string: {value}")
        return value
