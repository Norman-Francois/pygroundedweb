from __future__ import annotations

from typing import List, Optional

from .base import APIModel
from .dataset import Dataset
from .dataset_photo import DatasetPhoto


class Selection(APIModel):
    """Représente une sélection de photos.

    Champs:
        dataset: instance `Dataset` source de la sélection.
        photos: liste optionnelle de `DatasetPhoto` incluses dans la sélection.

    Raises:
        pydantic.ValidationError: si la structure fournie ne respecte pas le schéma.
    """

    dataset: Dataset
    photos: Optional[List[DatasetPhoto]]
