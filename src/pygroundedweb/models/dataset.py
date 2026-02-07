from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional, Union

from pydantic import field_validator

from .base import APIModel
from .dataset_photo import DatasetPhoto
from .user import User


class Dataset(APIModel):
    name: str
    date: date
    user: Union[User, str]
    photos: Optional[List[DatasetPhoto]] = None

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, value):
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value).date()
            except ValueError:
                raise ValueError(f"Invalid date string: {value}")
        return value
