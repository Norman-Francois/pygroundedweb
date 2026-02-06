from typing import Union

from .micmac import MicMac
from .enums import DistortionModel, ZoomFinal, TapiocaMode

SFM = Union[MicMac]

__all__ = ["MicMac", "SFM", "DistortionModel", "ZoomFinal", "TapiocaMode"]
