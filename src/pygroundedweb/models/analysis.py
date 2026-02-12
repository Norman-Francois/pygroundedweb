from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import HttpUrl

from .base import APIModel
from .configuration import Configuration
from .selection import Selection

class AnalysisStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Hole(APIModel):
    number: int
    volume: float

class Analysis(APIModel):
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
