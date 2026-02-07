from __future__ import annotations

from enum import Enum

from pydantic import HttpUrl

from .base import APIModel


class TypePhoto(Enum):
    BEFORE = "before"
    AFTER = "after"

class DatasetPhoto(APIModel):
    name: str
    type: TypePhoto
    thumb: HttpUrl
    preview: HttpUrl
    full_compressed: HttpUrl
    original: HttpUrl


