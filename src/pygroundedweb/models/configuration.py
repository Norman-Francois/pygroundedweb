from __future__ import annotations

from typing import List

from .base import APIModel
from .scalebar import ScaleBar
   

class Configuration(APIModel):
    name: str
    scalebar: List[ScaleBar]
