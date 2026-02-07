from __future__ import annotations

from .base import APIModel


class ScaleBar(APIModel):
    start: int
    end: int
    length: float
