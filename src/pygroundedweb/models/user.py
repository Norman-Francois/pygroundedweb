from __future__ import annotations

from .base import APIModel


class User(APIModel):
    name: str
    first_name: str
    last_name: str
    email: str