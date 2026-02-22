from __future__ import annotations

from typing import Literal

from ..base import ToolModel
from pygroundedweb.models.tools.sfm.enums import DistortionModel, ZoomFinal, TapiocaMode


class MicMac(ToolModel):
    """Configuration SFM pour MicMac.

    Champs:
        resource_type: identifiant de ressource (fixé à 'MicMac').
        distorsion_model: modèle de distorsion optique à utiliser (enum).
        zoom_final: mode de zoom final à appliquer (enum).
        tapioca_mode: stratégie d'extraction de points d'intérêt (enum).
        tapioca_resolution: résolution principale (entier, >0).
        tapioca_second_resolution: résolution secondaire (entier, >0).

    Raises:
        pydantic.ValidationError: si les valeurs fournies ne respectent pas le schéma.
    """
    resource_type: Literal['MicMac'] = 'MicMac'
    distorsion_model: DistortionModel
    zoom_final: ZoomFinal
    tapioca_mode: TapiocaMode
    tapioca_resolution: int
    tapioca_second_resolution: int
