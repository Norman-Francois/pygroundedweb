from __future__ import annotations

from typing import Literal

from ..base import ToolModel
from pygroundedweb.models.tools.sfm.enums import DistortionModel, ZoomFinal, TapiocaMode


class MicMac(ToolModel):
    resource_type: Literal['MicMac'] = 'MicMac'
    distorsion_model: DistortionModel
    zoom_final: ZoomFinal
    tapioca_mode: TapiocaMode
    tapioca_resolution: int
    tapioca_second_resolution: int
