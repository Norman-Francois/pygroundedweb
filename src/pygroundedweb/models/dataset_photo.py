"""Modèle pour une photo attachée à un dataset.

Contient le type (before/after) et les URLs vers différentes résolutions/artefacts.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import HttpUrl

from .base import APIModel


class TypePhoto(Enum):
    """Types possibles pour une photo: BEFORE ou AFTER."""
    BEFORE = "before"
    AFTER = "after"

class DatasetPhoto(APIModel):
    """Représente une photo de dataset avec différentes URL de rendus.

    Champs:
        name: nom/fichier de la photo.
        type: TypePhoto indiquant si c'est "before" ou "after".
        thumb/preview/full_compressed/original: URLs optionnelles.
    """
    name: str
    type: TypePhoto
    thumb: Optional[HttpUrl]
    preview: Optional[HttpUrl]
    full_compressed: Optional[HttpUrl]
    original: Optional[HttpUrl]

