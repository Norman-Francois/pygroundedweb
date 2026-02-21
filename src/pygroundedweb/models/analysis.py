"""Modèles relatifs aux analyses (Analysis, Hole, AnalysisStatus).

Ces modèles décrivent l'état et les résultats (liens point cloud, logs) d'une analyse.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import HttpUrl

from .base import APIModel
from .configuration import Configuration
from .selection import Selection

class AnalysisStatus(str, Enum):
    """Statut possible d'une analyse."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Hole(APIModel):
    """Représente un trou détecté avec numéro et volume."""
    number: int
    volume: float

class Analysis(APIModel):
    """Modèle représentant une analyse.

    Champs importants :
        name, date, user, status, selection, configuration, holes, et URLs vers les
        artefacts produits (point_cloud, logs).
    """
    name: str
    date: datetime
    user: str
    status: Optional[AnalysisStatus] = None
    point_cloud_before: Optional[HttpUrl] = None
    point_cloud_after: Optional[HttpUrl] = None
    logs: Optional[HttpUrl] = None
    selection: Selection
    notify_by_email: bool
    configuration: Configuration
    holes: List[Hole]
