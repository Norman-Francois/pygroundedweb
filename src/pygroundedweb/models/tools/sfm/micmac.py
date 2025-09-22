from __future__ import annotations

from pygroundedweb.models.tools.sfm.base import SFM
from pygroundedweb.models.tools.sfm.enums import DistortionModel, ZoomFinal, TapiocaMode


class MicMac(SFM):
    distortion_model: DistortionModel
    zoom_final: ZoomFinal
    tapioca_mode: TapiocaMode
    tapioca_resolution: int
    tapioca_second_resolution: int
