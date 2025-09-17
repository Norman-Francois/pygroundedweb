from __future__ import annotations

from datetime import date

from pydantic import HttpUrl

from .base import APIModel
from .selection import Selection


class Analysis(APIModel):
    name: str
    date: date
    point_cloud_before: HttpUrl
    point_cloud_after: HttpUrl
    logs: HttpUrl
    selection: Selection
