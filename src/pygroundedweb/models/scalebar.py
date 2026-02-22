from __future__ import annotations

from .base import APIModel


class ScaleBar(APIModel):
    """Représente une règle (échelle) utilisée pour calibrer les dimensions.

    Champs:
        start (int): identifiant de début de la ScaleBar.
        end (int): identifiant de la fin de la ScaleBar.
        length (float): longueur de la ScaleBar.

    Raises:
        pydantic.ValidationError: si les champs fournis sont manquants ou de mauvais type.
    """

    start: int
    end: int
    length: float
