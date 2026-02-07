from __future__ import annotations

from typing import List, Optional

from .base import APIModel
from .dataset import Dataset
from .dataset_photo import DatasetPhoto


class Selection(APIModel):
    dataset: Dataset
    photos: Optional[List[DatasetPhoto]]
