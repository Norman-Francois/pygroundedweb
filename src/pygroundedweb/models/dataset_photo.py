from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import HttpUrl

from .base import APIModel


class TypePhoto(Enum):
    BEFORE = "before"
    AFTER = "after"

class DatasetPhoto(APIModel):
    name: str
    type: TypePhoto
    thumb: Optional[HttpUrl]
    preview: Optional[HttpUrl]
    full_compressed: Optional[HttpUrl]
    original: Optional[HttpUrl]


